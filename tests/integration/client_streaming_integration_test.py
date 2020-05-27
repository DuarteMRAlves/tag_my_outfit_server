from contract.service_pb2 import PredictRequest, StreamPredictResponse, Prediction
from tests.integration.base_integration_test import BaseIT


class ClientStreamingIT(BaseIT):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __generate_batch(self, all_categories, all_attributes):
        for _, img in self._image_bytes.items():
            yield PredictRequest(image_data=img, all_categories=all_categories, all_attributes=all_attributes)

    def __generate_mixed_batch(self, prediction_params):
        for img, param in zip(self._image_bytes.items(), prediction_params):
            yield PredictRequest(image_data=img[1], all_categories=param[0], all_attributes=param[1])

    @staticmethod
    def __diff_len_msg(expected_len):
        return f'Prediction sizes differ: Expected {expected_len} predictions'

    def test_all_cat_all_attr_batch(self):
        print()
        print('Testing All Categories and All Attributes for Image batch')
        # Build generator of predictions
        batch_iter = self.__generate_batch(True, True)
        # Execute prediction
        response: StreamPredictResponse = self._stub.stream_predict(batch_iter)
        # Check results
        predictions: list = [el for el in response.predictions]
        self.assertEqual(len(predictions), len(self._image_bytes), self.__diff_len_msg(len(self._image_bytes)))
        for name, prediction in zip(self._image_bytes.keys(), predictions):
            self._check_all_categories(name, prediction)
            self._check_all_attributes(name, prediction)

    def test_all_cat_selected_attr_batch(self):
        print()
        print('Testing All Categories and Selected Attributes for Image batch')
        # Build generator of predictions
        batch_iter = self.__generate_batch(True, False)
        # Execute prediction
        response: StreamPredictResponse = self._stub.stream_predict(batch_iter)
        # Check results
        predictions: list = [el for el in response.predictions]
        self.assertTrue(len(predictions) == len(self._image_bytes), self.__diff_len_msg(len(self._image_bytes)))
        for name, prediction in zip(self._image_bytes.keys(), predictions):
            self._check_all_categories(name, prediction)
            self._check_selected_attributes(name, prediction)

    def test_selected_cat_all_attr_batch(self):
        print()
        print('Testing Selected Category and All Attributes for Image batch')
        # Build generator of predictions
        batch_iter = self.__generate_batch(False, True)
        # Execute prediction
        response: StreamPredictResponse = self._stub.stream_predict(batch_iter)
        # Check results
        predictions: list = [el for el in response.predictions]
        self.assertTrue(len(predictions) == len(self._image_bytes), self.__diff_len_msg(len(self._image_bytes)))
        for name, prediction in zip(self._image_bytes.keys(), predictions):
            self._check_selected_category(name, prediction)
            self._check_all_attributes(name, prediction)

    def test_selected_cat_selected_attr_batch(self):
        print()
        print('Testing Selected Category and Selected Attributes for Image batch')
        # Build generator of predictions
        batch_iter = self.__generate_batch(False, False)
        # Execute prediction
        response: StreamPredictResponse = self._stub.stream_predict(batch_iter)
        # Check results
        predictions: list = [el for el in response.predictions]
        self.assertTrue(len(predictions) == len(self._image_bytes), self.__diff_len_msg(len(self._image_bytes)))
        for name, prediction in zip(self._image_bytes.keys(), predictions):
            self._check_selected_category(name, prediction)
            self._check_selected_attributes(name, prediction)

    def test_mix_cat_attr_batch(self):
        print()
        print('Testing Mix Category and Attributes for Image batch')
        prediction_params = [
            (i % 4 == 0 or i % 4 == 1, i % 2 == 0) for i in range(len(self._image_bytes))
        ]
        batch_iter = self.__generate_mixed_batch(prediction_params)
        # Execute prediction
        response: StreamPredictResponse = self._stub.stream_predict(batch_iter)
        # Check results
        predictions: list = [el for el in response.predictions]
        self.assertTrue(len(predictions) == len(self._image_bytes), self.__diff_len_msg(len(self._image_bytes)))
        for name, prediction, prediction_param in zip(self._image_bytes.keys(), predictions, prediction_params):
            if prediction_param[0]:
                self._check_all_categories(name, prediction)
            else:
                self._check_selected_category(name, prediction)
            if prediction_param[1]:
                self._check_all_attributes(name, prediction)
            else:
                self._check_selected_attributes(name, prediction)
        pass
