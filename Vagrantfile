# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end

  config.vm.network "private_network", ip: "10.243.243.10"

  config.vm.provision "shell", inline: <<-SHELL
    # Install packages
    echo "Installing software packages..."
    apt-get -qq update
	apt-get -qq upgrade -y
	apt-get -qq install -y nginx python2.7 python-virtualenv python-dev libjpeg-dev libffi-dev postgresql postgresql-contrib libpq-dev rabbitmq-server redis-server

	# Postgresql setup
	# Allow listening on all interfaces
	echo "Setting up postgresql database and roles..."
	sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "/etc/postgresql/9.3/main/postgresql.conf"
	# Append to pg_hba.conf to add password auth:
    echo "host    all             all             all                     md5" >> /etc/postgresql/9.3/main/pg_hba.conf

	service postgresql restart

	# Set up database and user
    sudo -u postgres psql --command="CREATE DATABASE swarfarm_dev;"
    sudo -u postgres psql --command="CREATE USER swarfarmer_dev WITH PASSWORD 'intentionallyweak';"
    sudo -u postgres psql --command="GRANT ALL PRIVILEGES ON DATABASE swarfarm_dev TO swarfarmer_dev;"

	# Set up python env
	# echo "Setting up python environment..."
	# sudo -u vagrant virtualenv swarfarm_env
	# source swarfarm_env/bin/activate
	# pip install -qq -r /vagrant/requirements_dev.txt

    # Set up Django project
    # echo "Running database migrations..."
	# cd /vagrant
	# python manage.py migrate

	# deactivate

	echo "Done!"
	echo "Note: There are a few steps that must be completed manually:"
	echo " * Set up your local python environment."
	echo " * Run 'manage.py migrate' to update the database structure."
	echo " * Run 'manage.py createsuperuser' to set your admin user account."
	echo " * Create a .env file. See the .env.example file. It will work without edits for this Vagrant VM."
  SHELL
end
