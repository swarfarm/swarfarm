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
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 2.7
* PostgreSQL 9.4

Additional prerequisites for production:

* nginx
* Redis
* RabbitMQ

### Installing a development environment

1. Get your postgres set up with a user role and a database.
2. Install all the python packages, preferably in a virtual environment

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and edit the variables to fit your environment.
    * The minimum settings required to work in a development environment are `SECRET_KEY` and `DATABASE_URL`.
    * See the [Django documentation](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY) for `SECRET_KEY` before continuing.
    * `CACHE_BACKEND` and `CACHE_LOCATION` can be left unchanged and will utilize Django's dummy cache, which doesn't actually do anything.
    * `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` must be set to be able to submit forms in certain sections of the site. Create your own keys [here](https://www.google.com/recaptcha/admin).
    * `GOOGLE_API_KEY` is used for Google's URL shortener API and is not required unless you are testing the Twitch.tv Nightbot API.

4. Run all database migrations

```bash
python manage.py migrate
```

5. Create a superuser
```commandline
python manage.py createsuperuser
```

6. Load the bestiary data from the fixtures **COMING SOON**
7. Run the server
```commandline
python manage.py runserver
```

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