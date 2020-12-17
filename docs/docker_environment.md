# Docker Environment
Docker is a widely used and well-known technology used in development and deployment of software. When developing for SWARFARM, docker can be used as an alternative to Vagrant.

## Setup Docker Environment
The setup for Docker is kept pretty close to the Vagrant setup in order to be able to easily switch between the two development environments.  

To be able to use docker, you have to:
1. Copy `.env.example-docker` to `.env`. No modifications are necessary to work with the default `docker-compose.yml` file.
    * The container startup **will fail** if you do not have a .env file present.
2. Install [Docker](https://docs.docker.com/engine/install/) and perform any required setup per Docker documentation
    * Docker uses [Hyper-V](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v) on Windows. Hyper-V is not compatible with some other virtualization technologies like some Android emulators. **Make sure you know the limitations before installing.**
3. Run `docker-compose up` in the root directory of this project.
   * This keeps the console open and blocking. You can shut down the docker stack using `CTRL+C`. If you want to keep the containers running when closing the console, you have to run `docker-compose up -d` and shut it down with `docker-compose down`.
4. **On first setup** you need to run the following two commands *manually* from the command line. These need to be executed only **once** *after* the container is running:
   * `docker-compose exec postgres psql -U swarfarmer_dev swarfarm_dev -f /reset_sequences.sql`
   * `docker-compose exec -w /app swarfarm deployment_assets/run_initial_setup.sh` 

## Working with the docker environment
After setting up the docker environment in daemon mode (`docker-compose up -d`), you can easily start and stop the containers using `docker-compose start` and `docker-compose stop`. This will keep all data between restarts.  
If you want to erase all container data and start over, you can do `docker-compose down --remove-orphans --rmi local -v` and follow the setup instructions again.  
If you do not use the daemon mode, you can just exit the console using `CTRL+C` and spin the container back up using `docker-compose up`.

If you make changes to the infrastructure part of the project that could affect the deployment (for example add new dependencies) you need to rebuild the `swarfarm` docker image using `docker-compose build`. If something does not work, you can at any point delete all containers and start over.

### Accessing the local SWARFARM instance
When the container is running, you can access the SWARFARM instance at http://localhost:8080. If for some reason the port `8080` is already in use on your device, you can change the it in the `docker-compose.yml` file under the `nginx` service port mapping configuration.

### Interacting with the CLI
Since we're running the SWARFARM instance and all its' dependencies in Docker, you need to prefix every command you want to run on the container with `docker-compose exec swarfarm`. An example: If you want to create a new admin user you need to run `docker-compose exec swarfarm python manage.py createsuperuser`.

## Docker Environment Specifics
For ease of operation, some environment variables are set up differently when using Docker. In docker most services are split up in different containers. This means that the default localhost configuration will fail if the environment variables are not set up correctly.

The following variables **need** to be set:
* `CELERY_BROKER` has to point to either some sort of MQTT broker (like `rabbitmq`) or to a `redis` instance.
* `CACHE_LOCATION` needs to point to a valid endpoint depending on the value of `CACHE_BACKEND`. The Docker default for this is to point to a local `redis` database.

Due to the way some connection checks are implemented in the Docker setup, the database parameters are set differently compared to the Vagrant setup. When using Docker, you need to make sure the following parameters are set:
* `SQL_HOST`: The database IP or hostname (default: `postgres`).
* `SQL_USER`: The username that is used to connect to the database (default: `swarfarmer_dev`).
* `SQL_PASS`: The password that is used to connect to the database (default: `intentionallyweak`).
* `SQL_DB`: The database that is connected to (default: `swarfarm_dev`).

**Important**: If the environment variable `DATABASE_URL` is not set, it is populated using the `SQL_` variables. Should you decide to set it manually you need to make sure it points to the correct database. Copying the contents of the Vagrant setup **will not work** because the database is located on a different container and not on localhost.
