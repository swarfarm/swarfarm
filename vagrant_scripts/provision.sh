#!/usr/bin/env bash

# Install packages
echo "Installing software packages..."
sudo apt-get -qq update
sudo apt-get -qq upgrade -y
sudo apt-get -qq install -y nginx postgresql postgresql-contrib libpq-dev rabbitmq-server redis-server git make build-essential libjpeg-dev libffi-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev

# Postgresql setup
# Allow listening on all interfaces
echo "Setting up postgresql database and roles..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "/etc/postgresql/9.3/main/postgresql.conf"
# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" | sudo tee --append /etc/postgresql/9.3/main/pg_hba.conf > /dev/null

sudo service postgresql restart

# Set up database and user
sudo -u postgres psql --command="CREATE DATABASE swarfarm_dev;"
sudo -u postgres psql --command="CREATE USER swarfarmer_dev WITH PASSWORD 'intentionallyweak';"
sudo -u postgres psql --command="GRANT ALL PRIVILEGES ON DATABASE swarfarm_dev TO swarfarmer_dev;"

# Set up nginx
sudo mv ~/nginx_config /etc/nginx/sites-available/swarfarm
sudo ln -s /etc/nginx/sites-available/swarfarm /etc/nginx/sites-enabled/swarfarm
sudo rm /etc/nginx/sites-available/default
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
pyenv install 3.6.1
pyenv virtualenv 3.6.1 swarfarm-3.6.1
pyenv activate swarfarm-3.6.1

echo "Setting up python environment..."
pip install -qq -r /vagrant/requirements_dev.txt

# Set up Django project
echo "Running database migrations..."
cd /vagrant
python manage.py migrate
echo "Loading initial bestiary data..."
python manage.py loaddata bestiary_data.json

# Configure upstart and start python processes
sudo mv ~/gunicorn_upstart.conf /etc/init/swarfarm.conf
sudo mv ~/celery_upstart.conf /etc/init/celeryd.conf
sudo mv ~/celery_beat_upstart.conf /etc/init/celerybeat.conf

sudo service swarfarm start
sudo service celeryd start
sudo service celerybeat start

pyenv deactivate
echo "Done! Check the console for any errors."
