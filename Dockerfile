FROM phusion/passenger-customizable:2.2.0
LABEL maintainer="support@datacite.org"

# Set correct environment variables.
ENV HOME /home/app
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Allow app user to read /etc/container_environment
RUN usermod -a -G docker_env app

RUN /pd_build/python.sh
# Update installed APT packages
RUN apt-get update && apt-get upgrade -y -o Dpkg::Options::="--force-confold"
RUN apt-get install -y ntp pandoc pipenv
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# Enable Passenger and Nginx and remove the default site
# Preserve env variables for nginx
RUN rm -f /etc/service/nginx/down && \
    rm /etc/nginx/sites-enabled/default
COPY vendor/docker/webapp.conf /etc/nginx/sites-enabled/webapp.conf
COPY vendor/docker/00_app_env.conf /etc/nginx/conf.d/00_app_env.conf
COPY vendor/docker/cors.conf /etc/nginx/conf.d/cors.conf
COPY vendor/docker/env.conf /etc/nginx/main.d/env.conf

# Use Amazon NTP servers
COPY vendor/docker/ntp.conf /etc/ntp.conf

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

# Copy webapp folder
COPY . /home/app/webapp/

# Configure permissions
RUN chown -R app:app /home/app/webapp && \
    chmod -R 755 /home/app/webapp

# Set working directory
WORKDIR /home/app/webapp

# Update Pip and Pipenv
RUN pip install -U pip pipenv

# Install any needed packages specified in pipenv pipfile
RUN pipenv install --system --deploy --ignore-pipfile

# Expose web
EXPOSE 80
