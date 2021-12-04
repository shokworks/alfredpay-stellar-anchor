# Installing Django-Polaris Project for Alfred Stellar-Anchor.
## _Alfred.pay an easier way to send and receive cross border payments._

[![N|Solid](https://alfred-pay.com/wp-content/themes/Alfred%20Pay%20Theme/assets/images/Logo_Alfred.svg)](https://alfredpay.io)

_Alfred is a compliant Crypto to FIAT payment network where transactions and settlements are instant. Save time and money today with Alfred._

_Polaris is an extendable django app for Stellar Ecosystem Proposal (SEP) implementations maintained by the Stellar Development Foundation (SDF)._

## Installing a Polaris app of Django with a LEMP (Linux, Nginx, MariaDB y Python) Server.

### General Documentation:
-- The **LEMP** software stack is a group of software that can be used to serve dynamic web pages and web applications. This is an acronym that describes a **L**inux operating system like [Ubuntu], with an [Nginx] (pronounced like “**E**ngine-X”) web server, a backend data is stored with **M**ySQL like database [MariaDB] and the dynamic processing is handled by **P**ython.
-- These instructions assume you have already set up a django project. If you haven't, take a look at the [Python-PIP], [Django], [Polaris] and [Gunicorn] Documentation for more details.

### Installation of the packages and his dependencies.
- The project requires _MariaDB_ Server and Client to run, _Nginx_ and _Python3_ with his _pip_ package.
```sh
sudo aptitude install default-libmysqlclient-dev build-essential libldap2-dev mariadb-server-10.3 mariadb-client-10.3 nginx python3-dev python3-pip 
```
- The _MariaDB_ database software is now installed, but its configuration is not yet complete.
```sh
sudo mariadb -u root -p
CREATE DATABASE ${database};
CREATE USER '${username}'@'localhost' IDENTIFIED BY '${password}';
GRANT ALL PRIVILEGES ON ${database}.* TO '${username}'@'localhost';
FLUSH PRIVILEGES;
exit
```
> Note: Be sure to swap out `${database}`, `${username}` and `${password}` with the actual values of your configuration.

### Cloning the repository.
_To run this anchor server using your own stellar accounts, follow the instructions below._

- First, clone the repository:
```sh
git clone git@github.com:shokworks/alfredpay-stellar-anchor.git
cd ${WorkingFolder}
```
> Note: Be sure to swap out `${WorkingFolder}` with the actual values of your configuration.

- Then Install the virtualenv: Virtualenv is another key Python tool. It enables you to create a series of controlled environments where you can install and experiment with Python modules without upsetting any previously installed software. In the project folder type the folling command.
```sh
python3 -m pip install virtualenv
```
- Creating and activating a virtual environment.
```sh
python3 -m virtualenv ${WorkingFolder}/venv
source ${WorkingFolder}/venv/bin/activate
python -m pip install -r ${WorkingFolder}/backend/requirements.txt
```

- Then, add a config.json file containing the necessary environment variables in the folder ${WorkingFolder}/backend/src/etc/

```sh
{"Seccion Comments 1": "Django Secrets Env Values.",
"SECRET_KEY": "${Django Secret Key}",
"ALLOWED_HOSTS": ["127.0.0.1", "localhost", "${Domain Name}"],
"DATABASES": {"default": {"ENGINE": "django.db.backends.mysql", "NAME": "${database}", 
              "USER": "${username}", "PASSWORD": "${password}", "HOST": "127.0.0.1", "PORT": ""}},
"CORS_ALLOWED_ORIGINS": ["https://127.0.0.1", "https://localhost"],
"Seccion Comments 2": "Polaris Secrets Env Values.",
"STELLAR_NETWORK_PASSPHRASE": "Test SDF Network ; September 2015",
"HORIZON_URI": "https://horizon-testnet.stellar.org/",
"HOST_URL": "${Domain Name}",
"LOCAL_MODE": 0,
"ACTIVE_SEPS": ["sep-1", "sep-10", "sep-24"],
"Seccion Comments 3": "SEP 10 Configuration.",
"SEP10_HOME_DOMAINS": ["${Domain Name}"],
"SEP10_JWT_KEY": "${JWT Secret Key}",
"SEP10_SERVER_KEY":  "${First Stellar Account}",
"SEP10_SERVER_SEED": "${First Signing Account Seed}",
"SEP10_CLIENT_KEY":  "${Second Stellar Account}",
"SEP10_CLIENT_SEED": "${Second Signing Account Seed}",
"SEP10_CLIENT_A_REQ": "False"}
```

- You can make yours accounts with the folling link in the [Stellar Laboratory].
> Note: If you want to change the `config.json` file or the `settings.py` of the project, you can follow the documentation of the Polaris proyect in the [Polaris Tutorial].

### Testing Gunicorn’s Ability to Serve the Project

The last thing we want to do before leaving our virtual environment is test Gunicorn to make sure that it can serve the application.

```sh
cd ${WorkingFolder}/backend/src
gunicorn --bind 0.0.0.0:8000 ${project}.wsgi
```

> Note: `${project}` is in the same folder as `manage.py` in most of the configurations.

When you are finished testing, hit CTRL-C in the terminal window to stop Gunicorn. We’re now finished configuring our Django application. We can back out of our virtual environment by typing:

```sh
deactivate
```

Now we can create a Gunicorn systemd Service File, and configure Nginx to Proxy Pass to Gunicorn. Both configurations are outside the scope of this file for more documentation see, [Nginx] and [Gunicorn].

[Ubuntu]: <https://ubuntu.com/server/docs>
[MariaDB]: https://mariadb.com/kb/en/documentation/
[Nginx]: https://nginx.org/en/docs/
[Python-PIP]: https://pip.pypa.io/en/stable/
[Django]: https://docs.djangoproject.com/en/3.2/
[Polaris]: https://django-polaris.readthedocs.io/
[Gunicorn]: https://docs.gunicorn.org/en/stable/index.html
[Stellar Laboratory]: https://laboratory.stellar.org/#account-creator?network=test
[Polaris Tutorial]: https://django-polaris.readthedocs.io/en/stable/tutorials/index.html
