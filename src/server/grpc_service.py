from annotations.profiling import profile
from contract.service_pb2 import PredictRequest, PredictResponse, StreamPredictResponse, Prediction, Correspondence
from contract.service_pb2_grpc import PredictionServiceServicer
from model.service import Service


class PredictionServerImpl(PredictionServiceServicer):

    def __init__(self, service: Service):
        self.__service = service

    @profile
    def predict(self, request: PredictRequest, context):
        categories_results, attributes_results = self.__process_single_predict(request)
        return PredictResponse(predicted_categories=categories_results,
                               predicted_attributes=attributes_results)

    @profile
    def stream_predict(self, request_iterator, context):
        predictions = map(self.__process_single_request, request_iterator)
        return StreamPredictResponse(predictions=predictions)

    def __process_single_request(self, request):
        categories_results, attributes_results = self.__process_single_predict(request)
        return Prediction(predicted_categories=categories_results, predicted_attributes=attributes_results)

    def __process_single_predict(self, request):
        image_bytes = request.image_data
        all_categories = request.all_categories
        all_attributes = request.all_attributes
        categories_results, attributes_results = self.__service.predict(image_bytes, all_categories, all_attributes)
        categories_results = map(lambda x: Correspondence(label=x[0], value=x[1]), categories_results)
        attributes_results = map(lambda x: Correspondence(label=x[0], value=x[1]), attributes_results)
        return categories_results, attributes_results