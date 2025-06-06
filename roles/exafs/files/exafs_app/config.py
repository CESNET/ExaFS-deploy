"""
Configuration module for the ExaFS application.

This module defines the configuration settings for the ExaFS application across
different environments. It includes three configuration classes:

1. Config: Base configuration class with default settings for all environments.
2. ProductionConfig: Configuration settings specific to production environment.
3. DevelopmentConfig: Configuration settings specific to development environment.

The configuration includes settings for:
- Application identification and behavior
- Authentication methods (SSO, header-based, local)
- Security keys and secrets
- ExaAPI communication (HTTP or RabbitMQ)
- Flowspec and RTBH rule limits
- VRF (Virtual Routing and Forwarding) settings
- Multi-neighbor BGP configuration
- Database connections
- Logging

Environment variables are used for sensitive information and can override default values.
"""

import os


class Config:
    """
    Basic app configuration for current instalation. Values set here are default values for all environments.

    Secret keys and other sensitive information should be stored in environment variables and loaded here

    Other configuration values can be set here and overwritten in specific environment configuration
    """

    # APP Name - display in main toolbar
    APP_NAME = "ExaFS"

    # App configuration
    DEBUG = True
    TESTING = False
    SSO_AUTH = False
    HEADER_AUTH = False
    LOCAL_AUTH = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = os.getenv("JWT_SECRET", "secret")
    SECRET_KEY = os.getenv("SECRET_KEY", "secret2")

    LOGOUT_URL = "logout"

    # ExaApi configuration
    # possible values HTTP, RABBIT
    EXA_API = "RABBIT"
    # for HTTP EXA_API_URL must be specified
    EXA_API_URL = "http://localhost:5000"
    # for RABBITMQ EXA_API_RABBIT_* must be specified
    EXA_API_RABBIT_HOST = os.getenv("EXA_API_RABBIT_HOST", "localhost")
    EXA_API_RABBIT_PORT = os.getenv("EXA_API_RABBIT_PORT", "5672")
    EXA_API_RABBIT_PASS = os.getenv("EXA_API_RABBIT_PASS", "exaapi")
    EXA_API_RABBIT_USER = os.getenv("EXA_API_RABBIT_USER", "exaapi")
    EXA_API_RABBIT_VHOST = os.getenv("EXA_API_RABBIT_VHOST", "/")
    EXA_API_RABBIT_QUEUE = os.getenv("EXA_API_RABBIT_QUEUE", "exaapi")

    # Limits
    FLOWSPEC4_MAX_RULES = 9000
    FLOWSPEC6_MAX_RULES = 9000
    RTBH_MAX_RULES = 100000

    # Route Distinguisher for VRF
    # When True set your rd string and label to be used in messages
    USE_RD = False
    RD_STRING = "2852:2505"
    RT_STRING = "2852:2505"
    RD_LABEL = "16"

    # Multi neighbor configuration
    USE_MULTI_NEIGHBOR = True
    MULTI_NEIGHBOR = {
        "primary": ["192.168.1.1", "192.168.144.6"],
        "2852:9823": "192.168.2.1",
    }

    # list of RTBH Communities that are allowed to be used in whitelist, real ID from DB
    ALLOWED_COMMUNITIES = [1, 2]

    LOG_LEVEL = "INFO"
    LOG_FILE = "/app/logs/exafs-web.log"


class ProductionConfig(Config):
    """
    Production app configuration
    """

    LOCAL_IP = os.getenv("LOCAL_IP", "127.0.0.1")
    LOCAL_IP6 = os.getenv("LOCAL_IP6", "::ffff:")

    d_user = os.getenv("MYSQL_USER")
    d_pwd = os.getenv("MYSQL_PASSWORD")
    d_db = os.getenv("MYSQL_DATABASE")
    d_host = os.getenv("MYSQL_HOST")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{d_user}:{d_pwd}@{d_host}/{d_db}?charset=utf8"

    SSO_AUTH = True
    SSO_ATTRIBUTE_MAP = {
        "eppn": (False, "HTTP_X_EPPN"),
        "HTTP_X_EPPN": (False, "eppn"),
    }
    SSO_LOGIN_URL = "/login"
    API_KEY = ""
    DEVEL = False
    BEHIND_PROXY = True


class DevelopmentConfig(Config):
    """
    Development app configuration
    """

    d_pwd = os.getenv("MYSQL_ROOT_PASSWORD")
    d_db = os.getenv("MYSQL_DATABASE")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{d_pwd}@mariadb:3306/{d_db}?charset=utf8"
    LOCAL_IP = "127.0.0.1"
    LOCAL_IP6 = "::ffff:127.0.0.1"
    DEBUG = True
    DEVEL = True

    # LOCAL user parameters - when the app is used without SSO_AUTH
    # Defined in User model, uses local-login endpoint
    LOCAL_USER_UUID = "vrany@cesnet.cz"
    LOCAL_AUTH = True
