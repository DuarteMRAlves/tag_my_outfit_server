ARG WORKSPACE=/workspace
ARG PROTO_FILE=tag_my_outfit.proto

# --------------------------------------
# Builder stage to generate .proto files
# --------------------------------------

FROM python:3.6.12-slim-buster as builder
# Renew build args
ARG WORKSPACE
ARG PROTO_FILE

COPY requirements-build.txt ${WORKSPACE}/

WORKDIR ${WORKSPACE}

RUN pip install --upgrade pip && \
    pip install -r requirements-build.txt && \
    rm requirements-build.txt

ARG PROTOS_FOLDER_DIR=protos
COPY ${PROTOS_FOLDER_DIR} ${WORKSPACE}/

# Compile proto file and remove it
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ${PROTO_FILE}

# -----------------------------
# Stage to generate final image
# -----------------------------

FROM python:3.6.12-slim-buster
# Renew build args
ARG WORKSPACE
ARG PROTO_FILE

ARG USER=worker
ARG GROUP=worker-group

# Create non-privileged user to run
RUN addgroup --system ${GROUP} && \
    adduser --system --no-create-home --ingroup ${GROUP} ${USER} && \
    mkdir ${WORKSPACE} && \
    chown -R ${USER}:${GROUP} ${WORKSPACE}

# Install python packages
COPY requirements.txt ${WORKSPACE}/

WORKDIR ${WORKSPACE}

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt


# COPY .proto file to root to meet ai4eu specifications
COPY --from=builder --chown=${USER}:${GROUP} ${WORKSPACE}/${PROTO_FILE} /

# Copy generated code to workspace
COPY --from=builder --chown=${USER}:${GROUP} ${WORKSPACE}/*.py ${WORKSPACE}/src/

# Copy source code and necessary files to workspace
COPY --chown=${USER}:${GROUP} model ${WORKSPACE}/model/
COPY --chown=${USER}:${GROUP} config ${WORKSPACE}/config/
COPY --chown=${USER}:${GROUP} src ${WORKSPACE}/src/

# Expose port for incomming connections
EXPOSE 8061

# Run the server
CMD ["python", "src/server.py"]
