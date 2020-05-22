from annotations.profiling import profile
from contract.service_pb2 import PredictRequest, PredictResponse, Correspondence
from contract.service_pb2_grpc import PredictionServiceServicer
from server.service import Service


class PredictionServerImpl(PredictionServiceServicer):

    def __init__(self, service: Service):
        self.__service = service

    @profile
    def predict(self, request: PredictRequest, context):
        image_bytes = request.image_data
        all_categories = request.all_categories
        all_attributes = request.all_attributes
        categories_results, attributes_results = self.__service.predict(image_bytes, all_categories, all_attributes)
        categories_results = map(lambda x: Correspondence(label=x[0], value=x[1]), categories_results)
        attributes_results = map(lambda x: Correspondence(label=x[0], value=x[1]), attributes_results)
        return PredictResponse(predicted_categories=categories_results,
                               predicted_attributes=attributes_results)
