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
> Note: Be sure to swap out  `${database}`, `${username}` and `${password}` with the actual values of your configuration.

[Ubuntu]: <https://ubuntu.com/server/docs>
[MariaDB]: https://mariadb.com/kb/en/documentation/
[Nginx]: https://nginx.org/en/docs/
[Python-PIP]: https://pip.pypa.io/en/stable/
[Django]: https://docs.djangoproject.com/en/3.2/
[Polaris]: https://django-polaris.readthedocs.io/
[Gunicorn]: https://docs.gunicorn.org/en/stable/index.html
