import grpc
import numpy as np
import pandas as pd
import pickle as pkl
import os
import unittest


from collections import OrderedDict
from contract.service_pb2_grpc import PredictionServiceStub


TOLERANCE = 1e-06

DATA_DIR = "tests/data"
EXPECTED_DIR = "tests/expected"

FILES = [
    "predicted_categories_VSAM+FL_deepfashion.pkl",
    "predicted_categories_probs_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_probs_VSAM+FL_deepfashion.pkl",
]


def _is_close_row(row1, row2):
    index1, values1 = row1
    index2, values2 = row2
    return index1 == index2 and all(np.isclose(values1, values2, rtol=TOLERANCE, atol=TOLERANCE))


def _is_close_df(df1, df2):
    return all([
        _is_close_row(row1, row2) for row1, row2 in zip(df1.iterrows(), df2.iterrows())
    ])


class BaseIT(unittest.TestCase):
    """
    basic class for integration tests
    defines common checks for results
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __loadImageData(self):
        self._image_bytes: OrderedDict = OrderedDict()
        for file in os.listdir(DATA_DIR):
            with open(DATA_DIR + "/" + file, 'rb') as fp:
                self._image_bytes[file] = fp.read()

    def __loadExpectedResults(self):
        self.__expected = []
        for file in FILES:
            with open(EXPECTED_DIR + "/" + file, 'rb') as fp:
                self.__expected.append(pkl.load(fp))

    @staticmethod
    def __wrong_len_msg(test_param, file_name, expected, predicted):
        return f'Failed selected {test_param} for file \'{file_name}\': Wrong number of predictions: '\
               f'Expected {expected} but got {predicted}'

    @staticmethod
    def __wrong_label_msg(test_param, file_name, expected, predicted):
        return f'Failed selected {test_param} for file \'{file_name}\': Wrong prediction label: '\
               f'Expected {expected} but got {predicted}'

    @staticmethod
    def __wrong_value_msg(test_param, file_name, expected, predicted):
        return f'Failed selected {test_param} for file \'{file_name}\': Wrong prediction value: '\
               f'Expected {expected} but got {predicted}'

    def _check_selected_category(self, file_name, prediction):
        expected_df: pd.DataFrame = self.__expected[0].loc[file_name]
        expected_label = expected_df[expected_df == 1].index[0]
        expected_prob_df: pd.DataFrame = self.__expected[1].loc[file_name]
        expected_prob = expected_prob_df[expected_label]
        predicted_categories = prediction.predicted_categories
        # Assert num predictions
        self.assertEqual(len(predicted_categories), 1,
                         self.__wrong_len_msg('categories', file_name, 1, len(predicted_categories)))
        # Assert label
        self.assertEqual(predicted_categories[0].label, expected_label,
                         self.__wrong_label_msg('categories', file_name, expected_label, predicted_categories[0].label))
        # Assert value
        self.assertTrue(np.isclose(predicted_categories[0].value, expected_prob, rtol=TOLERANCE),
                        self.__wrong_value_msg('categories', file_name, expected_prob, predicted_categories[0].value))

    def _check_selected_attributes(self, file_name, predict_response):
        expected_df: pd.DataFrame = self.__expected[2].loc[file_name]
        expected_prediction = expected_df[expected_df == 1].index
        expected_prob_df: pd.DataFrame = self.__expected[3].loc[file_name]
        expected_prob_prediction = expected_prob_df[expected_prediction]
        predicted_attributes = predict_response.predicted_attributes
        # Assert num predictions
        self.assertEqual(len(expected_prediction), len(predicted_attributes),
                         self.__wrong_len_msg('attributes', file_name, len(expected_prediction), len(predicted_attributes)))

        for expected_label, expected_prob, predicted \
                in zip(expected_prob_prediction.index, expected_prob_prediction, predicted_attributes):
            # Assert label
            self.assertEqual(expected_label, predicted.label,
                             self.__wrong_label_msg('attributes', file_name, expected_label, predicted.label))
            # Assert value
            self.assertTrue(np.isclose(expected_prob, predicted.value, rtol=TOLERANCE),
                            self.__wrong_value_msg('attributes', file_name, expected_prob, predicted.value))

    @staticmethod
    def __check_all_aux(name, predicted, expected_df):
        predicted_attributes_df = pd.DataFrame(predicted[:, 1].reshape(1, -1).astype(np.double),
                                               columns=predicted[:, 0],
                                               index=[name]).T
        predicted_attributes_expected = pd.DataFrame(expected_df.loc[name])
        return _is_close_df(predicted_attributes_df, predicted_attributes_expected)

    def _check_all_categories(self, file_name, predict_response):
        predicted_categories = np.array([(el.label, el.value) for el in predict_response.predicted_categories])
        self.assertTrue(self.__check_all_aux(file_name, predicted_categories, self.__expected[1]),
                        f'Failed all categories for file \'{file_name}\'')

    def _check_all_attributes(self, file_name, predict_response):
        predicted_attributes = np.array([(el.label, el.value) for el in predict_response.predicted_attributes])
        self.assertTrue(self.__check_all_aux(file_name, predicted_attributes, self.__expected[3]),
                        f'Failed all attributes for file \'{file_name}\'')

    def setUp(self) -> None:
        self.__channel = grpc.insecure_channel("localhost:50051")
        self._stub = PredictionServiceStub(self.__channel)
        self.__loadImageData()
        self.__loadExpectedResults()
