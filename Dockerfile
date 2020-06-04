FROM python:3.6.10-slim-buster

# Install packages (common utilis for network debuging)
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends git make

# Install python packages
COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# Install gRPC service interface
RUN git clone -b v0.0.1 https://github.com/DuarteMRAlves/tag_my_outfit_interface.git && \
    cd tag_my_outfit_interface/python && \
    make && \
    cd ../.. && \
    rm -rf tag_my_outfit_interface

# Clean files
RUN apt-get autoremove --purge -y && \
  apt-get clean && \
  apt-get autoclean && \
  rm -rf /var/lib/apt/lists/*

# Set up user and permissions
RUN useradd -m -g users -s /bin/bash user
USER user:users

# Copy src and necessary files to workdir
WORKDIR /home/user
COPY --chown=user:users model model/
COPY --chown=user:users config config/
COPY --chown=user:users src src/

# Expose port for incomming connections
EXPOSE ${PORT}

# Run the server
CMD python src/server.py
