# Tag My Outfit

## Overview

This project implements a gRPC service to classify clothing parts within a set of categories, as well as predict their attributes.

## API Reference

The server implements the gRPC interface specified in the [tag_my_outfit_interface](https://github.com/DuarteMRAlves/tag_my_outfit_interface) github project.

## Technologies

 * [Python](https://www.python.org)

 * [Keras](https://keras.io)
 
 * [TensorFlow](https://www.tensorflow.org)
 
 * [Scikit-learn](https://scikit-learn.org/stable/)
 
 * [SciPy](https://www.scipy.org)
 
 * [NumPy](https://numpy.org)
 
 * [gRPC](https://grpc.io)
 
 * [Docker](https://www.docker.com)

## Getting Started

### Pre-Requisites

In order to clone the project github repository, it's required to install [git large file system](https://github.com/git-lfs/git-lfs?utm_source=gitlfs_site&utm_medium=repo_link&utm_campaign=gitlfs) to download the model weights file.

### Installing

The project was developed with python v3.6.10, the [gRPC interface package](https://github.com/DuarteMRAlves/tag_my_outfit_interface/tree/v0.0.1) v0.0.1, and the package's versions in the [requirements file](requirements.txt) so it's recommended to use the same software.

The installation steps are as follows:

 * Install [python](https://www.python.org/downloads/) and the [interface package v0.0.1](https://github.com/DuarteMRAlves/tag_my_outfit_interface/tree/v0.0.1) by following the respective page's instructions
 
 * Clone the github repository:
 
```
$ git clone -b v0.0.1 https://github.com/DuarteMRAlves/tag_my_outfit_server.git
```
 
 * Install the necessary packages by running the following command in the project's root directory:

```
$ pip install -r requirements.txt
```

### Running

With the required software installed, we can start the server with the following command, executed in the project's root directory:

```
$ python src/server.py
```

### Testing

The project tests require the unittest package. All the following commands should be executed inside the project's root directory.

#### Unit testing

This tests do not need the server running and only verifies if key project components are functional:

```
$ python -m unittest discover -s tests/unit/ -p *.py
```

#### Integration testing

This tests need the server running (to run the server follow the steps in the [Deployment Section](#deployment)) and will create clients to exhaustively test the server functionality:

```
$ python -m unittest discover -s tests/integration/ -p *.py
```

#### Load testing

This tests also require that the server is running, and will check its performance and correctness in a load scenario by sending multiple requests simultaneously. 
Not all possible combinations of message parameters are tested since [Integration Tests](#integration-testing) will cover all cases:

```
$ python -m unittest discover -s tests/load/ -p *.py
```

## Deployment

The project can be deployed with docker, and does not need any other pre-requisites since they will be installed in the generated image.
Also, a docker-compose file is provided for an easy deployment with default configurations.
In order to achieve that, execute the following steps:

 * Install [docker](https://docs.docker.com/get-docker/) and [docker compose](https://docs.docker.com/compose/install/) by following the respective page's instructions *(Note: Docker compose might be automatically installed with docker)*

 * Download the [Dockerfile](Dockerfile) and [docker-compose](docker-compose.yml) files from the github repository

 * Build the docker image:

```
$ docker-compose build
```

 * Start the server:

```
$ docker-compose up
```