from contract.service_pb2 import PredictRequest, PredictResponse
import inspect


class GrpcMessageBuilder:
    """
    Static class to simplify the building of grpc messages
    """

    __PREDICT_REQUEST_PARAMS = {
        'categories',
        'categories_probabilities',
        'attributes',
        'attributes_probabilities'
    }

    @classmethod
    def build_predict_request(cls, **kwargs):
        """
        Args:
            **kwargs:
                image_data (bytes):  with the image data
                categories (boolean, defaults=false): true if the response should contain the predicted categories
                data and false otherwise
                categories_probabilities (boolean, default=false): true if the response should contain the predicted
                categories probabilities data and false otherwise
                attributes (boolean, default=false): true if the response should contain the predicted attributes data
                and false otherwise
                attributes_probabilities (boolean, default=false): true if the message should contain the predicted
                attributes probabilities data and false otherwise
        Returns:
            PredictRequest with the given params

        """
        return PredictRequest(**kwargs)

    @classmethod
    def build_predict_response(cls, **kwargs):
        """
        Args:
            **kwargs:
                prediction (double),
        Returns:

        """
        return PredictResponse(0)