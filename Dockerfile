
FROM phusion/passenger-full:1.0.6

# Allow app user to read /etc/container_environment
RUN usermod -a -G docker_env app

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Update installed APT packages
RUN apt-get update && apt-get upgrade -y -o Dpkg::Options::="--force-confold" && \
    apt-get install -y ntp

# Fetch PIP install script and run
ADD "https://bootstrap.pypa.io/get-pip.py" /tmp/get-pip.py
RUN python3 /tmp/get-pip.py

# Fetch pipenv install script and run
ADD "https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py" /tmp/get-pipenv.py
RUN python3 /tmp/get-pipenv.py

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Enable Passenger and Nginx and remove the default site
# Preserve env variables for nginx
RUN rm -f /etc/service/nginx/down && \
    rm /etc/nginx/sites-enabled/default
COPY vendor/docker/webapp.conf /etc/nginx/sites-enabled/webapp.conf

# Use Amazon NTP servers
COPY vendor/docker/ntp.conf /etc/ntp.conf

# enable SSH
RUN rm -f /etc/service/sshd/down && \
    /etc/my_init.d/00_regen_ssh_host_keys.sh

# install custom ssh key during startup
RUN mkdir -p /etc/my_init.d
COPY vendor/docker/10_ssh.sh /etc/my_init.d/10_ssh.sh

## Viringo setup

# Copy webapp folder
COPY . /home/app/webapp/

# Copy tests over to app folder
COPY tests /home/app/tests

# Configure permissions
RUN chown -R app:app /home/app/webapp && \
    chmod -R 755 /home/app/webapp

# # Set working directory to crawler
WORKDIR /home/app/webapp

# Install any needed packages specified in pipenv pipfile
RUN pipenv install --system --deploy --ignore-pipfile

# Expose web
EXPOSE 80