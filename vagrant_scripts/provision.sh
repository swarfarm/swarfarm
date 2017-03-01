#!/usr/bin/env bash

# Install packages
echo "Installing software packages..."
sudo apt-get -qq update
sudo apt-get -qq upgrade -y
sudo apt-get -qq install -y nginx python2.7 python-virtualenv python-dev libjpeg-dev libffi-dev postgresql postgresql-contrib libpq-dev rabbitmq-server redis-server

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

# Set up python env
echo "Setting up python environment..."
virtualenv -q swarfarm_env
source swarfarm_env/bin/activate
pip install -qq -r /vagrant/requirements_dev.txt

# Set up Django project
echo "Running database migrations..."
cd /vagrant
python manage.py migrate
echo "Loading initial bestiary data..."
python manage.py loaddata bestiary_data.json

sudo mv ~/gunicorn_upstart.conf /etc/init/swarfarm.conf
sudo service swarfarm start

deactivate
echo "Done! Check the console for any errors."