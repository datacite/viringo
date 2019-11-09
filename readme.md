[![Build Status](https://travis-ci.com/datacite/viringo.svg?branch=master)](https://travis-ci.com/datacite/viringo) [![Docker Build Status](https://img.shields.io/docker/cloud/datacite/viringo.svg)](https://hub.docker.com/r/datacite/viringo)

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

Unit and Interation tests are split out to allow optional faster builds. 
Integration tests are higher level tests that will usually integrate or mock with
other dependencies.

* All tests: `docker-compose exec web pipenv run pytest`
* Only mocked tests: `docker-compose exec web pipenv run pytest -v -m "not real"`
* Integration tests: `docker-compose exec web pipenv run pytest tests/integration`
* Unit tests: `docker-compose exec web pipenv run pytest tests/unit`

Follow along via [Github Issues](https://github.com/datacite/lupo/issues).

### Note on Patches/Pull Requests

* Fork the project
* Write tests for your new feature or a test that reproduces a bug
* Implement your feature or make a bug fix
* Do not mess with version or history
* Commit, push and make a pull request. Bonus points for topical branches.

## License

**Viringo** is released under the [MIT License](https://github.com/datacite/viringo/blob/master/LICENSE).
