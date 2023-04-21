[![Build Status](https://travis-ci.com/datacite/viringo.svg?branch=master)](https://travis-ci.com/datacite/viringo)

# Viringo

OAI-PMH Compatible provider for exposing PID related metadata.
Specifically built for support for DataCite metadata. To use this service please
go to [https://oai.datacite.org](https://oai.datacite.org).

## What's a "Viringo"
Viringo is one of the names for the Peruvian hairless dog.
Chosen to fit into a naming scheme within DataCite, it also represents
an element of this mostly being about exposing what's underneath, i.e. no need
for hair.

## Installation

Using Docker.

```bash
docker run -p 8091:80 datacite/viringo
```

or

```bash
docker-compose up
```

You can now point your browser to `http://localhost:8091` and use the application.

## Development

Unit and Integration tests are split out to allow optional faster builds.
Integration tests are higher level tests that will usually integrate or mock with
other dependencies.

* Linter: `docker-compose exec web pipenv run pylint **/*.py`
* All tests: `docker-compose exec web pipenv run pytest`
* Only mocked tests: `docker-compose exec web pipenv run pytest -v -m "not real"`
* Integration tests: `docker-compose exec web pipenv run pytest tests/integration`
* Unit tests: `docker-compose exec web pipenv run pytest tests/unit`

Follow along via [Github Issues](https://github.com/datacite/lupo/issues).

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

### Note on Patches/Pull Requests

* Fork the project
* Write tests for your new feature or a test that reproduces a bug
* Implement your feature or make a bug fix
* Do not mess with version or history
* Commit, push and make a pull request. Bonus points for topical branches.


## License

**Viringo** is released under the [MIT License](https://github.com/datacite/viringo/blob/master/LICENSE).
