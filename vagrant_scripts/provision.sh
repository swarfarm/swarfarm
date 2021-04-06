#!/usr/bin/env bash

# Add postgresql repo
echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install packages
echo "Installing software packages..."
sudo DEBIAN_FRONTEND=noninteractive apt -yq update
sudo DEBIAN_FRONTEND=noninteractive apt -yq upgrade
sudo DEBIAN_FRONTEND=noninteractive apt -yq install nginx postgresql-11 libpq-dev rabbitmq-server redis-server git make build-essential libjpeg-dev libffi-dev libssl-dev zlib1g-dev libreadline-dev libbz2-dev libsqlite3-dev

# Postgresql setup
# Allow listening on all interfaces to connect directly from host PC
echo "Setting up postgresql database and roles..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "/etc/postgresql/11/main/postgresql.conf"
# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" | sudo tee --append /etc/postgresql/11/main/pg_hba.conf > /dev/null

sudo service postgresql restart

# Set up database and user
sudo -u postgres psql --command="CREATE DATABASE swarfarm_dev template=template0 ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';"
sudo -u postgres psql --command="CREATE USER swarfarmer_dev WITH PASSWORD 'intentionallyweak';"
sudo -u postgres psql --command="ALTER ROLE swarfarmer_dev SET client_encoding TO 'utf8';"
sudo -u postgres psql --command="ALTER ROLE swarfarmer_dev SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql --command="ALTER ROLE swarfarmer_dev SET timezone TO 'UTC';"
sudo -u postgres psql --command="ALTER ROLE swarfarmer_dev WITH SUPERUSER;"

# Set up nginx
sudo mv ~/nginx_config /etc/nginx/sites-available/swarfarm
sudo ln -s /etc/nginx/sites-available/swarfarm /etc/nginx/sites-enabled/swarfarm
sudo rm /etc/nginx/sites-enabled/default
sudo service nginx reload

# Install pyenv + friends
curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
echo 'export PATH="/home/vagrant/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# Repeat above commands because 'source ~/.bashrc' doesn't work here
export PATH="/home/vagrant/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install python + init virtualenv
pyenv install 3.6.8
pyenv virtualenv 3.6.8 swarfarm-3.6.8
cd /vagrant
pyenv local swarfarm-3.6.8

echo "Setting up python environment..."
pip install -qq -r /vagrant/requirements_dev.txt

# Set up Django project
echo "Running database migrations..."
python manage.py migrate
echo "Loading initial data..."
python manage.py loaddata bestiary_data
python manage.py loaddata initial_auth_groups
python manage.py loaddata reports

# Reset SQL table sequences after loading fixtures
sudo -u postgres psql swarfarm_dev -f ~/reset_sequences.sql > /dev/null

# Configure upstart and start python processes
sudo mv ~/swarfarm.socket /etc/systemd/system/swarfarm.socket
sudo mv ~/swarfarm.service /etc/systemd/system/swarfarm.service
sudo mv ~/celery.service /etc/systemd/system/celery.service
sudo mv ~/celery_beat.service /etc/systemd/system/celery_beat.service

sudo systemctl daemon-reload
sudo systemctl enable swarfarm
sudo systemctl enable celery
sudo systemctl enable celery_beat
sudo service swarfarm start
sudo service celery start
sudo service celery_beat start

echo "Done! Check the console for any errors."
