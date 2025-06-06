"""
This is run py for the application. Copied to the container on build.
"""

from os import environ

from flowapp import create_app, db
import config


# Configurations
EXAFS_ENV = environ.get("EXAFS_ENV", "Production")
EXAFS_ENV = EXAFS_ENV.lower()

# Call app factory
if EXAFS_ENV in ("devel", "development"):
    APP = create_app(config.DevelopmentConfig)
else:
    APP = create_app(config.ProductionConfig)

# init database object
db.init_app(APP)

# run app
if __name__ == "__main__":
    APP.run(host="::", port=8080, debug=True)
