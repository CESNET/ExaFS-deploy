import secrets
import string
import yaml
import os
import click


# Function to generate a secure random password
def generate_password(length=32):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def ensure_dir_exists(host_dir):
    if not os.path.exists(host_dir):
        os.makedirs(host_dir)


@click.command()
@click.option("--hostname", default="exaflow.cesnet.cz", help="Shortname / hostname of the server")
@click.option(
    "--root-dir",
    default="./inventory/host_vars/",
    help="Root directory of the source codes, default is ./inventory/host_vars/",
)
@click.option("--env-file", default=".env", help="Name of the .env file")
@click.option(
    "--exafs-env",
    default="production",
    help="Environment of the exafs app any value other than 'development' or 'devel' will be considered as 'production'",
)
@click.option("--local-ip", default="127.0.0.1", help="IP address of the server, used by ExaFS app internally")
@click.option("--local-ip6", default="::ffff:", help="IPv6 address of the server, used by ExaFS app internally")
def main(hostname, root_dir, env_file, exafs_env, local_ip, local_ip6):
    """
    Generates environment variables and secrets for a given hostname and writes them to secrets.yaml file.\n
    The secrets.yaml file is used by Ansible to set the secrets for the services and for setting the enviroment variables in Docker.\n
    Files can be found in the directory: root_dir/hostname and eventually manually edited.
    Important: The secrets.yaml file should not be shared or stored in a public repository.
    Important 2: The host_vars/hosts.yaml file should be updated with the hostname - this is not done automatically.

    Dependencies: Python 3.6 or higher, click, PyYAML
    """
    host_dir = os.path.join(root_dir, hostname)
    ensure_dir_exists(host_dir)

    rabbitmq_default_pass = generate_password()

    env_vars = {
        "env_variables": {
            "jwt_secret": generate_password(128),
            "secret_key": generate_password(128),
            "exa_api_rabbit_host": "rabbitmq",
            "exa_api_rabbit_port": "5672",
            "exa_api_rabbit_pass": rabbitmq_default_pass,
            "exa_api_rabbit_user": "exaapi",
            "exa_api_rabbit_vhost": "/",
            "exa_api_rabbit_queue": "exa_api",
            "mysql_host": "mariadb",
            "mysql_root_password": generate_password(),
            "mysql_database": "exafs",
            "mysql_user": "exafs",
            "mysql_password": generate_password(32),
            "rabbitmq_default_user": "exaapi",
            "rabbitmq_default_pass": rabbitmq_default_pass,
            "exafs_env": exafs_env,
            "local_ip": local_ip,
            "local_ip6": local_ip6,
        },
        "backup_user_password": generate_password(),
    }

    secrets_file_name = os.path.join(host_dir, "secrets.yaml")
    # Write the secrets.yaml file
    with open(secrets_file_name, "w") as secrets_file:
        yaml.dump(env_vars, secrets_file, default_flow_style=False)

    print("secrets.yaml file generated successfully.")


if __name__ == "__main__":
    main()
