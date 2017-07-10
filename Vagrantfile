# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "bento/ubuntu-14.04"
    config.vm.provider "virtualbox" do |v|
        v.memory = 2048
        v.cpus = 2
    end

    config.vm.network "private_network", ip: "10.243.243.10"
    config.vm.network "forwarded_port", guest: 5432, host: 5432  # postgres
    config.vm.network "forwarded_port", guest: 6432, host: 6432  # pgbouncer
    config.vm.network "forwarded_port", guest: 5672, host: 5672  # AMQP
    config.vm.network "forwarded_port", guest: 6379, host: 6379  # redis
    config.vm.network "forwarded_port", guest: 8000, host: 8000  # manage.py runserver using remote python interpreter

    config.vm.provision "file", source: "./vagrant_scripts/gunicorn_upstart.conf", destination: "gunicorn_upstart.conf"
    config.vm.provision "file", source: "./vagrant_scripts/celery_upstart.conf", destination: "celery_upstart.conf"
    config.vm.provision "file", source: "./vagrant_scripts/celery_beat_upstart.conf", destination: "celery_beat_upstart.conf"
    config.vm.provision "file", source: "./vagrant_scripts/nginx_config", destination: "nginx_config"
    config.vm.provision "file", source: "./vagrant_scripts/pgbouncer.ini", destination: "pgbouncer.ini"
    config.vm.provision "file", source: "./vagrant_scripts/pgbouncer_userlist.txt", destination: "pgbouncer_userlist.txt"
    config.vm.provision "file", source: "./vagrant_scripts/pgbouncer_start", destination: "pgbouncer_start"
    config.vm.provision "shell", privileged: false, path: './vagrant_scripts/provision.sh'
end
