# SWARFARM
An assistant website for Summoner's War. 

## API
SWARFARM exposes an API that contains detailed game data (most notably monster and skill data), in addition to public 
user profiles. The root endpoint is [https://swarfarm.com/api/v2/](https://swarfarm.com/api/v2/). Documentation of all
endpoints is available [here](https://swarfarm.com/api/v2/docs/). This API is free and public but subject to rate 
limits, and any abuse or abnormal use of server resources will see restrictions applied. The API powers tools like 
[SW Optimizer](https://tool.swop.one/) and the [SWOP Discord bot](https://top.gg/bot/417128270950170624).

The API schema is not finalized and may change at any time.

### Can I use it to power my own website?
Yes - but you *must* proxy requests through your own server. CORS restrictions are in place. Your server will be subject
to rate limits just like any other client.

### API Authentication
Authentication is required to perform actions that change your account data or to view your own profile (if private).  

#### Basic Token Authentication
You can get or generate a basic token from your edit profile page on swarfarm.com via the dropdown menu on your
username. The token is equivalent to your password so **do not share it**. Tokens never expire, but you can change yours
at any time by generating a new one. This authentication method is ideal to allow a tool to perform actions on your
account's behalf such as the SWARFARM plugin for SW-Exporter.

#### JWT Authentication
JSON Web Tokens are ideal for temporary authentication, since they expire automatically after a time.

Generating a token:
```bash
$ curl -X POST -H "Content-Type: application/json" -d '{"username":"myaccount","password":"password123"}' https://swarfarm.com/api/v2/auth/get-token/
```

Using the token in a request:
```bash
$ curl -H "Authorization: JWT <your_token>" https://swarfarm.com/api/v2/<endpoint>/
```

## Contributing
You don't need to code to contribute ideas. If you have a feature request, notice a bug, inaccuracies in the monster/
skill data, or anything else, submit an issue here on github or in the 
[feedback section](https://swarfarm.com/feedback/) of the site. For UI ideas, chop together a quick example in paint 
to help communicate your thoughts.

Pull requests are always welcome, but first create an issue so the change can be discussed. Coding can begin after there
is an agreement with the maintainers if and how the change should be implemented. 

If you want to talk about the site or have questions about the code base, 
[join the developer Discord server](https://discord.gg/EuJyvTGkxQ). 

## Setting up for Development
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

### Vagrant and Hyper-V
The default VM provider VirtualBox is incompatible with Windows Hyper-V. If you want to keep Hyper-V enabled (if you use 
Docker, for example), you will want to use the `hyperv` Vagrant provider. There are a few potential issues:

#### Not available at 10.243.243.10 after provisioning
Check the output of the `vagrant up` command for the correct IP address. This is a 
[known limitation](https://www.vagrantup.com/docs/providers/hyperv/limitations.html#limited-networking) with Vagrant and 
Hyper-V.

#### Shared folders (SBM) throws errors
Turn on SBM 1.x and SBM Direct from Windows Features (the same place where you can turn on Hyper-V)
 
#### Shared folders (SBM) asking for password
If you don't have password for your Windows account, then you need to set one

#### `pyenv` can't change directory to /vargant and/or SSH working really slow
Your Network Sharing doesn't allow Vargant to access your files. To fix this:

1. Go to Network and Internet -> Network and Sharing Center -> Advanced sharing settings
2. From Guest or Public section Turn on file and printer sharing
3. From All Networks section Turn off password protected sharing

This can open up some security holes; a better solution is welcome.

### Creating your admin user
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

### Running the tests
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
