# Deployment scripts for ExaFS
## with Docker Compose and Ansible

This repository contains ansible playbooks for deploying [ExaFS](https://github.com/CESNET/) with docker compose on target machine.

## Introductory Notes

* The Ansible playbooks currently expect the target OS to be RPM-based – RHEL 9 or Rocky Linux. Other OS support in progress. 
* Services are installed under the root account, with possible privilege escalation to the `deploy` user.
* You must set up an SSH key on the target server and have Ansible installed to run the playbook.


## What Needs to Be Resolved in Advance

The following tasks must be done manually before starting the deployment:

* Instalation of HTTP server and choice of auth method. Our recomended combination is Apache httpd + Shibboleth Auth. Don't forget to set HTTPS certificates and finally configure ProxyPass to Docker.
* Proxy config should include X-Forwarded-For header. Configuration files `shib.conf` and `ssl.conf` are provided as examples in [./docs/apache\_conf](./docs/apache_conf)
* Installation of [Docker + Docker Compose plugin](https://docs.docker.com/engine/install/rhel/) from the Docker repository.
* Firewall configuration
* For RHEL, the `codeready-builder-for-rhel-9-x86_64-rpms` repository must be enabled due to dependencies (python3.xx packaging).

## Deployment Steps

* Use the **generate\_env\_vars.py** script to generate the *secrets.yaml* file for installation.

  * The generated data is written to **inventory/host\_vars/{hostname}/secrets.yaml**.
  * This file can be manually edited or created entirely using the provided template in the `example` directory.
  * The generation script has a CLI for specifying some parameters – most importantly, the public IP addresses of the target machine.
  * Usage:

    * `python generate_env_vars.py --help`
    * `python generate_env_vars.py --hostname test.example.com --local-ip 192.168.1.2`
  * Requirements: `click`, `PyYAML`. See *requirements.txt*
* Create an entry for the server in **/inventory/host\_vars/hosts.yaml**
* In **roles/exafs/files/exafs\_app/**, modify **config.py** and **run.py** if needed, according to the planned installation. Key parameters are usually set via environment variables, so modifying **secrets.yaml** is often sufficient.
* Currently the develop branch of [ExaFS repository](https://github.com/CESNET/exafs/tree/develop) is used. This can be modified in the **Dockerfile** of exafs role in **roles/exafs/files/exafs\_app/**
* The directory **roles/exafs/files/database/** contains the files **01\_app\_tables\_data.sql** and **02\_rule\_tables\_empty.sql**, which create the basic database structure used in CESNET. The content can be replaced by a database dump (e.g., when restoring from a backup). If the database doesn't have the ExaFS 1.0.x structure, migration is necessary.
* Run `ansible-playbook site.yaml`. This file defines the order of playbooks – database, RabbitMQ, application, ExaBGP + process. If needed, you can run each playbook separately, for example:
  `ansible-playbook site.yaml --tags exabpg`
  or limit execution to a specific host:
  `ansible-playbook site.yaml --limit hostname`
* If a database migration is needed, run the script with an environment variable that triggers the migration. Migration is only necessary when the model changes – typically with a major application version change (see changelog of ExaFS).
  `ansible-playbook -i inventory site.yaml -e "run_migrations=true" --limit exa.civ.cvut.cz`

## What and Where Was Installed?

* ExaFS runs in Docker containers under the `deploy` user (Ansible creates this user if it doesn’t exist).
* The application is installed in **/opt/exafs**, where you can manage the containers using Docker Compose.
* Daily database backups are configured at 3 AM to **/opt/exafs/backups**
* A cron job is configured to call the endpoint *[https://example.com/rules/withdraw\_expired](https://example.com/rules/withdraw_expired)* every 10 minutes.
* The `guarda` service is no longer used. The endpoint */rules/announce\_all* is contacted directly by the ExaBGP service after restart (via `ExecStartPost`).
* RabbitMQ is used for sending messages from ExaFS to ExaBGP. The communication process (formerly `exa_api`) is installed as the Python package `exabgp-process`.
* Logging:

  * Containers use the 'syslog' driver; logs are then written via syslog into three files in **/opt/exafs/logs/**
  * Standard Docker Compose logging is also available
  * `exabgp-process` logs together with ExaBGP to **/var/log/exabgp**

## What Needs to Be Done Afterwards

* Final configuration of ExaBGP + connecting BGP to the network (ExaBGP package will be installed). At the beginning of **/etc/exabgp/exabgp.conf**, add:

```
process flowspec {
    run /usr/local/bin/exabgp-process;
    encoder json;
}
```

