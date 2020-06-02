FROM python:3.6.10-slim-buster

# Install packages (common utilis for network debuging)
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends iputils-ping net-tools ncat && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# Set up user and permissions
RUN useradd -m -g users -s /bin/bash user
USER user:users

# Copy src and necessary files to workdir
WORKDIR /home/user
COPY --chown=user:users model model/
COPY --chown=user:users config config/
COPY --chown=user:users src src/

# Generate gRPC code
RUN cd src && python contract/generate_sources.py

# Expose port for incomming connections
EXPOSE ${PORT}

# Run the server
CMD python src/server.py
