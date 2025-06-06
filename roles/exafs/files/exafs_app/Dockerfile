# Use the official Python image from the Docker Hub
FROM python:3.11-alpine

# upgrade pip as root
RUN pip install --upgrade pip

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV USER_ID=1000
ENV GROUP_ID=1000
ENV USER_NAME=deploy
ENV GROUP_NAME=deploy
ENV FLASK_APP=run.py
ENV TZ="Europe/Prague"

# Install system dependencies
RUN apk add --update && apk add --no-cache bash curl gcc git mariadb-connector-c-dev mariadb-dev musl-dev vim

# Create a group and user 
RUN addgroup -g $GROUP_ID $GROUP_NAME && \
 adduser --shell /sbin/nologin --disabled-password \
  --uid $USER_ID --ingroup $GROUP_NAME $USER_NAME

# Change to the user
USER $USER_NAME

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone -b develop https://github.com/CESNET/exafs.git .

# Install Python dependencies
COPY --chown=$USER_NAME:$USER_NAME ./requirements-docker.txt /app/requirements-docker.txt
RUN pip install --user -r requirements-docker.txt
COPY --chown=$USER_NAME:$USER_NAME ./run.py /app/run.py
COPY --chown=$USER_NAME:$USER_NAME ./config.py /app/config.py

# Create a directory for the logs
RUN mkdir -p /app/logs

# add user bin to PATH
ENV PATH="/home/${USER_NAME}/.local/bin:${PATH}"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with Gunicorn
CMD ["gunicorn"  , "--bind", "0.0.0.0:8000", "run:app"]


