from outfit_tagging.interface.service_pb2 import PredictRequest, PredictResponse
from tests.integration.base_integration_test import BaseIT


class ClientSingleRequestIT(BaseIT):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_all_cat_all_attr(self):
        print()
        print(f'Testing All Categories and All Attributes for Single Image')
        for file_name, image_bytes in self._image_bytes.items():
            predict_request: 'PredictRequest' = PredictRequest(image_data=image_bytes, all_categories=True,
                                                               all_attributes=True)
            predict_response: 'PredictResponse' = self._stub.predict(predict_request)
            # Check predicted categories
            self._check_all_categories(file_name, predict_response)
            # Check predicted attributes
            self._check_all_attributes(file_name, predict_response)

    def test_selected_cat_all_attr(self):
        print()
        print(f'Testing Selected Category and All Attributes for Single Image')
        for file_name, image_bytes in self._image_bytes.items():
            predict_request: 'PredictRequest' = PredictRequest(image_data=image_bytes, all_categories=False,
                                                               all_attributes=True)
            predict_response: 'PredictResponse' = self._stub.predict(predict_request)
            # Check predicted categories
            self._check_selected_category(file_name, predict_response)
            # Check predicted attributes
            self._check_all_attributes(file_name, predict_response)

    def test_all_cat_selected_attr(self):
        print()
        print(f'Testing All Categories and Selected Attributes for Single Image')
        for file_name, image_bytes in self._image_bytes.items():
            predict_request: 'PredictRequest' = PredictRequest(image_data=image_bytes, all_categories=True,
                                                               all_attributes=False)
            predict_response: 'PredictResponse' = self._stub.predict(predict_request)
            # Check predicted categories
            self._check_all_categories(file_name, predict_response)
            # Check predicted attributes
            self._check_selected_attributes(file_name, predict_response)

    def test_selected_cat_selected_attr(self):
        print()
        print(f'Testing Selected Category and Selected Attributes for Single Image')
        for file_name, image_bytes in self._image_bytes.items():
            predict_request: 'PredictRequest' = PredictRequest(image_data=image_bytes, all_categories=False,
                                                               all_attributes=False)
            predict_response: 'PredictResponse' = self._stub.predict(predict_request)
            # Check predicted categories
            self._check_selected_category(file_name, predict_response)
            # Check predicted attributes
            self._check_selected_attributes(file_name, predict_response)