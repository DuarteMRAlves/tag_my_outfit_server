# Create builder image to clone repositories
FROM debian:buster as builder

# Install git and git lfs to clone repositories
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends git ca-certificates

# Set workdir to opt
WORKDIR /opt

# Clone interface repository from v0.0.1 tag
RUN git clone -b v0.0.1 https://github.com/sipg-isr/tag_my_outfit_interface.git

# Start from debian slim buster with python install
FROM python:3.6.10-slim-buster

# Install python packages
COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# Install gRPC service interface package
COPY --from=builder /opt/tag_my_outfit_interface /opt/tag_my_outfit_interface
RUN cd /opt/tag_my_outfit_interface/python && \
    pip install grpcio-tools && \
    bash bin/grpc.sh && \
    bash bin/install.sh && \
    cd ../.. && \
    # Remove code now that package is installed
    rm -rf tag_my_outfit_interface

# Set up user and permissions
RUN useradd -m -g users -s /bin/bash user
USER user:users

# Copy source code and necessary files to workdir
WORKDIR /home/user
COPY --chown=user:users model model/
COPY --chown=user:users config config/
COPY --chown=user:users src src/

# Expose port for incomming connections
EXPOSE ${PORT}

# Run the server
CMD python src/server.py
