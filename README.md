# SWARFARM
SWARFARM needs contributors! I'd really love to get a small core group of people who can continue to develop SWARFARM 
into the future. If you're interested in taking on this role, please [join our Discord server](https://discord.gg/EuJyvTGkxQ)
and send a message to porksmash.

## Contributing
Any ideas should be raised as an issue first.
If you want to contribute code for an idea, fork the repository and create a pull request.
Any changes in data models that affects the database structure will be highly scrutinized and may be delayed in 
deployment if accepted. Base your work on the current master branch, which will represent what is running on the live 
site. Any other branches that might exist are either under development or experimental. 

### Setting up for Development
1. Copy `.env.example` to `.env`. No modifications are necessary to work with the default Vagrant config.
    * Vagrant provisioning **will fail** if you do not have a .env file present.
2. Install [Vagrant](https://www.vagrantup.com/downloads.html) and perform any required setup per Vagrant documentation
    * Vagrant is configured to use [VirtualBox](https://www.virtualbox.org/) as the VM provider. You are free to choose
    your own provider.
3. Run `vagrant up` in the root directory of this project.

This will get you:
* Fully operational production stack compressed into one VM (nginx, postgres, gunicorn, redis, rabbitmq, celery)
* Debug mode enabled
* Hot reloading code based this local source directory. No hot reload for celery daemon, though.
* Server accessible at http://10.243.243.10
* Monster bestiary data already filled in
 
What won't work:
* Parsing the game data files. This requires decryption keys which I will not distribute.
* reCaptcha for user registration. [Create your own](https://www.google.com/recaptcha/admin/create) set of keys and add 
them to the `.env` file using the `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` keys. Be sure to add your local 
development IP address to the list of approved domains.

You can use the python virtualenv on the Vagrant VM (located at `/home/vagrant/.pyenv/versions/swarfarm-3.6.8/bin/python`) 
as a remote interpreter if your development environment supports it. The ports for postgres, redis, and RabbitMQ are 
forwarded to your host machine so they are accessible from localhost. The Vagrant VM requires at least 3GB of RAM.

A full list of available environment variables is available at the top of `swarfarm/settings.py`.

#### Vagrant and Hyper-V
The default VM provider VirtualBox is incompatible with Windows Hyper-V. If you want to keep Hyper-V enabled (if you use 
Docker, for example), you will want to use the `hyperv` Vagrant provider. There are a few potential issues:

##### Not available at 10.243.243.10 after provisioning
Check the output of the `vagrant up` command for the correct IP address. This is a 
[known limitation](https://www.vagrantup.com/docs/providers/hyperv/limitations.html#limited-networking) with Vagrant and 
Hyper-V.

##### Shared folders (SBM) throws errors:
Turn on SBM 1.x and SBM Direct from Windows Features (the same place where you can turn on Hyper-V)
 
##### Shared folders (SBM) asking for password:
If you don't have password for your Windows account, then you need to set one

##### `pyenv` can't change directory to /vargant and/or SSH working really slow*:
Your Network Sharing doesn't allow Vargant to access your files. To fix this:

1. Go to Network and Internet -> Network and Sharing Center -> Advanced sharing settings
2. From Guest or Public section Turn on file and printer sharing
3. From All Networks section Turn off password protected sharing

This can open up some security holes; a better solution is welcome.


#### Creating your admin user
Run `python manage.py createsuperuser` and follow the prompts.

This admin user functions with the Django admin, but not the rest of the SWARFARM site. If you want the same account to 
work as a normal profile account as well, you need to attach a `Summoner` profile model instance to it. To do so, open a 
Django shell by running `python manage.py shell` and run the following commands:

```python
from django.contrib.auth.models import User
from herders.models import Summoner
Summoner.objects.create(user=User.objects.first())
```

**Note:** Adjust the `User` queryset to pick the account you want to be admin if necessary.

## Running the tests
Run `python manage.py test --settings=swarfarm.settings_test`. It is also recommended to use the `--keepdb` argument to reduce the amount of time spend creating the database.

## Built With
* [Python](https://www.python.org/)
* [Django](https://www.djangoproject.com/) - The web framework
* [Django REST Framework](http://www.django-rest-framework.org/) - REST API for Django
* [Celery](http://www.celeryproject.org/) - Asynchronous task runner
* Many other packages. See requirements.txt

## Authors
* [**Peter Andersen**](https://github.com/PeteAndersen) - swarfarm@porksmash.com
* [Many contributors](https://github.com/PeteAndersen/swarfarm/graphs/contributors)

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgments
* [SWProxy](https://github.com/kakaroto/SWProxy/) for easily extracting game data, which makes SWARFARM orders of magnitude easier to use. 
* [SWProxy-plugins](https://github.com/lstern/SWProxy-plugins/) for including the SwarfarmLogger.py plugin and making the [data logs](https://swarfarm.com/data/log/) possible.
* [SW-Exporter](https://github.com/Xzandro/sw-exporter), the new proxy hotness for exporting and logging.
