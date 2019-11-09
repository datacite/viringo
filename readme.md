[![Build Status](https://travis-ci.com/datacite/viringo.svg?branch=master)](https://travis-ci.com/datacite/viringo) [![Docker Build Status](https://img.shields.io/docker/build/datacite/viringo.svg)](https://hub.docker.com/r/datacite/viringo/)

# Viringo

OAI-PMH Compatible provider for exposing PID related metadata.
Specifically built for support for DataCite metadata.

## What's a "Viringo"
Viringo is one of the names for the Peruvian hairless dog.
Chosen to fit into a naming scheme within DataCite, it also represents
an element of this mostly being about exposing what's underneath, i.e. no need
for hair.

### Requirements
* Python 3.6+
* Pipenv to manage dependencies

# Development

## Local system development

With pipenv it is simple to configure in a virtualenv for local development.
This method allows full usage of the native flask development server.

### Pipenv
This project uses Pipenv, full details can be found here https://docs.pipenv.org/en/latest/

```
$ pipenv install
$ pipenv shell
$ FLASK_APP=viringo FLASK_ENV=development flask run
```

Access on: http://localhost:5000/

## Testing

Unit and Interation tests are split out to allow optional faster builds.
Integration tests are higher level tests that will usually integrate or mock with
other dependencies.

* All tests: `pipenv run pytest`
* Only mocked tests: `pipenv run pytest -v -m "not real"`
* Integration tests: `pipenv run pytest tests/integration`
* Unit tests: `pipenv run pytest tests/unit`


# Docker (Passenger)

The main dockerfile is built to use the phusion passenger docker image and run
with the passenger application server (and nginx webserver).
A docker-compose file exists to allow easy starting of this locally.

`docker-compose up` - to get started

Access via http://localhost:8091

### Development
You can develop using this docker image but you won't get helpers like auto-reload, it is preferred to use one of the above alternative options.

## License

**Viringo** is released under the [MIT License](https://github.com/datacite/viringo/blob/master/LICENSE).
