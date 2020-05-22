from concurrent import futures
from model.impl import PredictionServerImpl
from contract.service_pb2_grpc import add_PredictionServiceServicer_to_server
from server.service import Service
from model.preprocess import PreprocessHandler
from model.prediction import PredictionHandler
from model.results import ResultsHandler
from model.encoder import Encoder
from server.context import Context
import grpc
import logging
import pickle as pkl
import time

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def load_encoder(file):
    with open(file, 'rb') as fp:
        params = pkl.load(fp)
    encoder = Encoder(*params)
    n_classes = len(encoder.encoder.classes_)
    return encoder, n_classes


def startServer():
    # Get configs
    server_context = Context()
    model_dir = server_context.model_dir
    model_weights_path = model_dir + '/' + server_context.weights
    categories_path = model_dir + '/' + server_context.ohe_categories
    attributes_path = model_dir + '/' + server_context.ohe_attributes

    # Load encoders
    categories_encoder, n_categories = load_encoder(categories_path)
    attributes_encoder, n_attributes = load_encoder(attributes_path)

    # Init handlers
    preprocess_handler: PreprocessHandler = PreprocessHandler()
    prediction_handler: PredictionHandler = PredictionHandler(model_weights_path, n_categories, n_attributes)
    results_handler: ResultsHandler = ResultsHandler(categories_encoder, n_categories, attributes_encoder, n_attributes)

    service = Service(preprocess_handler, prediction_handler, results_handler)
    service_impl = PredictionServerImpl(service)

    # Init server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    add_PredictionServiceServicer_to_server(service_impl, server)
    server.add_insecure_port(f'{server_context.host}:{server_context.port}')
    server.start()
    logging.info(f'Server running at {server_context.host}:{server_context.port}')
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.info('Server stopped by keyboard interruption')
        server.stop(0)


if __name__ == '__main__':
    startServer()
