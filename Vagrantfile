# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "bento/ubuntu-18.04"
    config.vm.provider "virtualbox" do |v|
        v.memory = 3072
        v.cpus = 2
    end

    config.vm.network "private_network", ip: "10.243.243.10"
    config.vm.network "forwarded_port", guest: 5432, host: 5432  # postgres
    config.vm.network "forwarded_port", guest: 6432, host: 6432  # pgbouncer
    config.vm.network "forwarded_port", guest: 5672, host: 5672  # AMQP
    config.vm.network "forwarded_port", guest: 6379, host: 6379  # redis
    config.vm.network "forwarded_port", guest: 8000, host: 8000  # manage.py runserver using remote python interpreter

    config.vm.provision "file", source: "./vagrant_scripts/swarfarm.service", destination: "swarfarm.service"
    config.vm.provision "file", source: "./vagrant_scripts/swarfarm.socket", destination: "swarfarm.socket"
    config.vm.provision "file", source: "./vagrant_scripts/celery.service", destination: "celery.service"
    config.vm.provision "file", source: "./vagrant_scripts/celery_beat.service", destination: "celery_beat.service"
    config.vm.provision "file", source: "./vagrant_scripts/nginx_config", destination: "nginx_config"
    config.vm.provision "shell", privileged: false, path: './vagrant_scripts/provision.sh'
end
