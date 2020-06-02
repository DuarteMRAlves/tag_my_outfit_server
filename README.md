# Fashion Prediction

## API Reference

The server implements the contract specified in the [service proto file](src/contract/service.proto).

## Deployment

### Docker Deployment

The project can be deployed with docker. In order to achieve that, it's only required a docker installation, since all other project requirements will be installed in the generated docker image. Also, a [docker-compose file](docker-compose.yml) is provided for a simple deployment. 

In order to deploy the docker container, execute the following commands:

 * Build the docker image

```
$ docker-compose build
```

 * Start the server

```
$ docker-compose up
```

### Non-Docker Deployment

The project can run without docker. For that, a python installation is required, along with the packages in the [requirements file](requirements.txt).

The project was developed with python v3.6.10 and the package's versions in the [requirements file](requirements.txt) so it's recommended to use the same software.

With the required software installed, we can start the server with the following command, executed in the project's root directory:

```
$ python src/server.py
```

## Testing

The project tests require the unittest package. All the following commands should be executed inside the project's root directory.

### Unit testing

This tests do not need the server running and only verify if key project components are functional and can be executed with the following command:

```
$ python -m unittest discover -s tests/unit/ -p *.py
```

### Integration testing

This tests need the server running (to run the server follow the steps in the [Deployment Section](#deployment)) and will create clients to exhaustively test the server functionality.
They can be executed with the following command:

```
$ python -m unittest discover -s tests/integration/ -p *.py
```

### Load testing

This tests also require that the server is running, and will check its performance and correctness in a load scenario by sending multiple requests simultaneously. 
Not all possible combinations of message parameters are not tested since the [Integration Tests](#integration-tests) will cover all cases.
To run the tests execute the command:

```
$ python -m unittest discover -s tests/load/ -p *.py
```
