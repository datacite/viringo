Viringo
-------

OAI-PMH Compatible provider for exposing PID related metadata.
Specifically built for support for DataCite metadata.

### What's a "Viringo"
Viringo is one of the names for the Peruvian hairless dog.
Chosen to fit into a naming scheme within DataCite, it also represents
an element of this mostly being about exposing what's underneath, i.e. no need
for hair.

## Requirements
* Python 3.6+
* Pipenv to manage dependencies and configure a python virtualenv.

## Development

### Pipenv
This project uses Pipenv, full details can be found here https://docs.pipenv.org/en/latest/

```
$ pipenv install
$ pipenv shell
$ FLASK_APP=viringo flask run
```

## Testing

Unit and Interation tests are split out to allow optional faster builds.
Integration tests are higher level tests that will usually integrate or mock with
other dependencies.

* All tests: ```pipenv run pytest```
* Integration tests: ```pipenv run pytest tests/integration```
* Unit tests: ```pipenv run pytest tests/unit```