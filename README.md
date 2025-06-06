# Deployment Scripts for ExaFS
## with Docker Compose and Ansible

This repository contains Ansible playbooks for deploying [ExaFS](https://github.com/CESNET/) with Docker Compose on a target machine.

## Introductory Notes

* The Ansible playbooks currently expect the target OS to be RPM-based – RHEL 9 or Rocky Linux. Support for other operating systems is in progress.
* Services are installed under the root account, with possible privilege escalation to the `deploy` user.
* You must set up an SSH key on the target server and have Ansible installed to run the playbook.

## Prerequisites

The following tasks must be completed manually before starting the deployment:

* **HTTP server installation and authentication method selection**
  * Our recommended combination is Apache httpd + Shibboleth Auth
  * Don't forget to set up HTTPS certificates and configure ProxyPass to Docker
  * Proxy configuration should include the X-Forwarded-For header
  * Configuration files `shib.conf` and `ssl.conf` are provided as examples in [./docs/apache_conf](./docs/apache_conf)
* **Docker installation**
  * Install [Docker + Docker Compose plugin](https://docs.docker.com/engine/install/rhel/) from the Docker repository
* **Firewall configuration**
* **RHEL-specific requirement**
  * For RHEL, the `codeready-builder-for-rhel-9-x86_64-rpms` repository must be enabled due to dependencies (python3.x packaging)

## Deployment Steps

1. **Generate environment variables and secrets**
   * Use the `generate_env_vars.py` script to generate the `secrets.yaml` file for installation
   * The generated data is written to `inventory/host_vars/{hostname}/secrets.yaml`
   * This file can be manually edited or created entirely using the provided template in the `example` directory
   * The generation script has a CLI for specifying parameters – most importantly, the public IP addresses of the target machine
   * Usage:
     ```bash
     python generate_env_vars.py --help
     python generate_env_vars.py --hostname test.example.com --local-ip 192.168.1.2
     ```
   * Requirements: `click`, `PyYAML`. See `requirements.txt`

2. **Configure inventory**
   * Create an entry for the server in `inventory/host_vars/hosts.yaml`

3. **Configure application files**
   * In `roles/exafs/files/exafs_app/`, modify `config.py` and `run.py` if needed, according to your planned installation
   * Key parameters are usually set via environment variables, so modifying `secrets.yaml` is often sufficient

4. **Set ExaFS version**
   * Currently the develop branch of [ExaFS repository](https://github.com/CESNET/exafs/tree/develop) is used
   * This can be modified in the Dockerfile of the exafs role in `roles/exafs/files/exafs_app/`

5. **Configure database**
   * The directory `roles/exafs/files/database/` contains the files `01_app_tables_data.sql` and `02_rule_tables_empty.sql`, which create the basic database structure used in CESNET
   * The content can be replaced by a database dump (e.g., when restoring from a backup)
   * If the database doesn't have the ExaFS 1.0.x structure, migration is necessary

6. **Run deployment**
   * Run `ansible-playbook site.yaml`
   * This file defines the order of playbooks – database, RabbitMQ, application, ExaBGP + process
   * If needed, you can run each playbook separately, for example:
     ```bash
     ansible-playbook site.yaml --tags exabgp
     ```
   * Or limit execution to a specific host:
     ```bash
     ansible-playbook site.yaml --limit hostname
     ```

7. **Database migration (if needed)**
   * If database migration is needed, run the script with an environment variable that triggers the migration
   * Migration is only necessary when the model changes – typically with a major application version change (see ExaFS changelog)
   ```bash
   ansible-playbook -i inventory site.yaml -e "run_migrations=true" --limit exa.civ.cvut.cz
   ```

## What Gets Installed and Where?

* **ExaFS application**
  * Runs in Docker containers under the `deploy` user (Ansible creates this user if it doesn't exist)
  * The application is installed in `/opt/exafs`, where you can manage the containers using Docker Compose
* **Database backups**
  * Daily database backups are configured at 3 AM to `/opt/exafs/backups`
* **Scheduled tasks**
  * A cron job is configured to call the endpoint `https://example.com/rules/withdraw_expired` every 10 minutes
* **Services architecture**
  * The `guarda` service is no longer used
  * The endpoint `/rules/announce_all` is contacted directly by the ExaBGP service after restart (via `ExecStartPost`)
  * RabbitMQ is used for sending messages from ExaFS to ExaBGP
  * The communication process (formerly `exa_api`) is installed as the Python package `exabgp-process`
* **Logging**
  * Containers use the 'syslog' driver; logs are then written via syslog into three files in `/opt/exafs/logs/`
  * Standard Docker Compose logging is also available
  * `exabgp-process` logs together with ExaBGP to `/var/log/exabgp`

## Post-Installation Configuration

* **ExaBGP configuration**
  * Final configuration of ExaBGP + connecting BGP to the network (ExaBGP package will be installed)
  * At the beginning of `/etc/exabgp/exabgp.conf`, add:

```
process flowspec {
    run /usr/local/bin/exabgp-process;
    encoder json;
}
```