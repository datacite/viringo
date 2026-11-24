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

# Optional preferred Ubuntu mirror used only while building, e.g. a cloud-local
# mirror in CI where archive.ubuntu.com/security.ubuntu.com are slow. When set,
# apt uses mirror lists (like GitHub's own runner images do) with failover:
#  - main/updates/backports: this mirror first, then the default mirrors;
#  - security: security.ubuntu.com first, then this mirror, then archive.
#    The security index has no Valid-Until, so a mirror that silently stops
#    syncing could otherwise hide security fixes; it is only ~2 MB, so taking
#    it from the authoritative host costs little.
# Empty keeps the defaults. The image's own apt sources are restored afterwards.
ARG UBUNTU_MIRROR=
# Changing this value forces the upgrade layer below to rebuild so new OS
# security updates are picked up; CI passes the ISO week.
ARG APT_CACHE_BUST=

# Update installed APT packages
RUN echo "apt cache bust: ${APT_CACHE_BUST:-none}" && \
    cp /etc/apt/sources.list.d/ubuntu.sources /tmp/ubuntu.sources.orig && \
    if [ -n "${UBUNTU_MIRROR}" ]; then \
      printf '%s\tpriority:1\n%s\tpriority:2\n%s\tpriority:3\n' \
        "${UBUNTU_MIRROR%/}/" \
        "http://archive.ubuntu.com/ubuntu/" \
        "http://security.ubuntu.com/ubuntu/" > /etc/apt/apt-mirrors.txt && \
      printf '%s\tpriority:1\n%s\tpriority:2\n%s\tpriority:3\n' \
        "http://security.ubuntu.com/ubuntu/" \
        "${UBUNTU_MIRROR%/}/" \
        "http://archive.ubuntu.com/ubuntu/" > /etc/apt/apt-mirrors-security.txt && \
      sed -i -E \
        -e "s#^URIs: http://archive\.ubuntu\.com/ubuntu/?#URIs: mirror+file:/etc/apt/apt-mirrors.txt#" \
        -e "s#^URIs: http://security\.ubuntu\.com/ubuntu/?#URIs: mirror+file:/etc/apt/apt-mirrors-security.txt#" \
        /etc/apt/sources.list.d/ubuntu.sources; \
    fi && \
    apt-get update && \
    apt-get upgrade -y -o Dpkg::Options::="--force-confold" && \
    cp /tmp/ubuntu.sources.orig /etc/apt/sources.list.d/ubuntu.sources && \
    rm -f /etc/apt/apt-mirrors.txt /etc/apt/apt-mirrors-security.txt && \
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

# enable SSH. The base image ships pre-generated host keys, which every image
# built from it (and anyone who pulls it) shares. Delete them so
# /etc/my_init.d/00_regen_ssh_host_keys.sh generates unique keys when each
# container starts.
RUN rm -f /etc/service/sshd/down /etc/ssh/ssh_host_*

# install custom ssh key during startup
COPY vendor/docker/10_ssh.sh /etc/my_init.d/10_ssh.sh

# restart server on every request in development (FLASK_DEBUG set)
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
