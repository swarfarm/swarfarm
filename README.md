# SWARFARM

This is the entirety of the source code running on [swarfarm.com](https://swarfarm.com).
Previously, a portion of the site was published on github as [swarfarm_io](https://github.com/porksmash/swarfarm_io).
This was the code that dealt with uploaded user data, so I felt that being open about what it was doing was important.
Now, I've decided to publish the entire codebase to get more eyes on the code and hopefully some contributions. 
This project was started as a learning experience, and my web development and python skills started out rusty.
Some of that rust is still in the code today, so if you see something ugly it can probably be improved.

## Next steps for SWARFARM

Work is ongoing to fully flesh out the REST API and recreate the frontend with the latest and greatest web development technologies.
This opens the door to third-party clients and mobile apps.
Any new features or major refinements are on hold until the new frontend is ready.
The exceptions to that rule are bug fixes, data logging/report generation, and any minor effort improvements.

## Contributing

Any ideas should be raised as an issue first.
If you want to contribute code for an idea, fork the repository and create a pull request.
Any changes in data models that affects the database structure will be highly scrutinized and may be delayed in deployment if accepted.

### Setting up for Development

1. Copy `.env.example` to `.env`. No modifications are necessary to work with the default Vagrant config.
Vagrant provisioning will **fail** if you do not have a .env file present.
2. Install [Vagrant](https://www.vagrantup.com/downloads.html) and run `vagrant up` in the root directory of this project.
`.env.example` will automatically be copied to `.env` and will work without modification for development.

This will get you:
 * Fully operational production stack compressed into one VM (nginx, postgres, gunicorn, redis, rabbitmq, celery)
 * Debug mode enabled
 * Hot reloading code based this local source directory. No hot reload for celery daemon, though.
 * Server accessible at http://10.243.243.10
 * Monster bestiary data already filled in

You can use the python virtualenv on the Vagrant VM (located at `/home/vagrant/swarfarm_env`) as a remote interpreter if your development environment supports it.
The ports for postgres, redis, and RabbitMQ are forwarded to your host machine so they are accessible from localhost. 

## Running the tests

There are no tests yet. I am a horrible person. 

## Built With

* [Python](https://www.python.org/)
* [Django](https://www.djangoproject.com/) - The web framework
* [Django REST Framework](http://www.django-rest-framework.org/) - REST API for Django
* [Celery](http://www.celeryproject.org/) - Asynchronous task runner
* Many other packages. See requirements.txt

## Authors

* [**Peter Andersen**](https://github.com/porksmash) - swarfarm@porksmash.com

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [SWProxy](https://github.com/kakaroto/SWProxy/) for easily extracting game data, which makes SWARFARM orders of magnitude easier to use. 
* [SWProxy-plugins](https://github.com/lstern/SWProxy-plugins/) for including the SwarfarmLogger.py plugin and making the [data logs](https://swarfarm.com/data/log/) possible.
