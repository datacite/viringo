FROM phusion/passenger-python314:3.2.3
LABEL maintainer="support@datacite.org"

# Set correct environment variables.
ENV HOME=/home/app \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Allow app user to read /etc/container_environment
RUN usermod -a -G docker_env app

# Update installed APT packages
RUN apt-get update && \
    apt-get upgrade -y -o Dpkg::Options::="--force-confold" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install pipenv into its own virtualenv so it stays out of the system
# Python (PEP 668) and out of the application's virtualenv.
RUN python3 -m venv /opt/pipenv && \
    /opt/pipenv/bin/pip install --no-cache-dir -U pip pipenv && \
    ln -s /opt/pipenv/bin/pipenv /usr/local/bin/pipenv

# Application virtualenv. It lives outside /home/app/webapp so that the
# docker-compose bind mount of the source tree does not hide it. pipenv uses
# it automatically because VIRTUAL_ENV is set.
ENV VIRTUAL_ENV=/home/app/venv \
    PIPENV_VERBOSITY=-1
ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN python3 -m venv $VIRTUAL_ENV

# Enable Passenger and Nginx and remove the default site
# Preserve env variables for nginx
RUN rm -f /etc/service/nginx/down && \
    rm /etc/nginx/sites-enabled/default
COPY vendor/docker/webapp.conf /etc/nginx/sites-enabled/webapp.conf
COPY vendor/docker/00_app_env.conf /etc/nginx/conf.d/00_app_env.conf
COPY vendor/docker/cors.conf /etc/nginx/conf.d/cors.conf
COPY vendor/docker/env.conf /etc/nginx/main.d/env.conf

# Run additional scripts during container startup (i.e. not at build time)
RUN mkdir -p /etc/my_init.d

# enable SSH
RUN rm -f /etc/service/sshd/down && \
    /etc/my_init.d/00_regen_ssh_host_keys.sh

# install custom ssh key during startup
COPY vendor/docker/10_ssh.sh /etc/my_init.d/10_ssh.sh

# restart server on file changes in development
COPY vendor/docker/20_always_restart.sh /etc/my_init.d/20_always_restart.sh

## Viringo setup

# Set working directory
WORKDIR /home/app/webapp

# Install dependencies from the lockfile first so this layer is cached
# independently of application source changes.
COPY Pipfile Pipfile.lock /home/app/webapp/
RUN pipenv install --deploy && \
    rm -rf /root/.cache

# Copy webapp folder
COPY . /home/app/webapp/

# Configure permissions
RUN chown -R app:app /home/app/webapp && \
    chmod -R 755 /home/app/webapp

# Expose web
EXPOSE 80
