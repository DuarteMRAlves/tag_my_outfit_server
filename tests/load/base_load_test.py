import multiprocessing as mp
import numpy as np
import os
import pandas as pd
import pickle as pkl
import time
import unittest

from tag_my_outfit_pb2 import PredictRequest

DATA_DIR = "tests/data"
EXPECTED_DIR = "tests/expected"
FILES = [
    "predicted_categories_VSAM+FL_deepfashion.pkl",
    "predicted_categories_probs_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_probs_VSAM+FL_deepfashion.pkl",
]
TOLERANCE = 1e-06


def is_close_row(row1, row2):
    index1, values1 = row1
    index2, values2 = row2
    return index1 == index2 and all(np.isclose(values1, values2, rtol=TOLERANCE, atol=TOLERANCE))


def is_close_df(df1, df2):
    return all([
        is_close_row(row1, row2) for row1, row2 in zip(df1.iterrows(), df2.iterrows())
    ])


def check_all_aux(name, predicted, expected_df):
    predicted_attributes_df = pd.DataFrame(predicted[:, 1].reshape(1, -1).astype(np.double),
                                           columns=predicted[:, 0],
                                           index=[name]).T
    predicted_attributes_expected = pd.DataFrame(expected_df.loc[name])
    return is_close_df(predicted_attributes_df, predicted_attributes_expected)


class BaseLoadTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self) -> None:
        self._image_bytes = []
        self._file_names = []
        self.__expected = []
        self._process_count = 0
        self._num_dup = 20

        self.__loadData()
        self.__loadExpectedResults()

    def __loadData(self):
        for file_name in os.listdir(DATA_DIR):
            with open(DATA_DIR + '/' + file_name, 'rb') as fp:
                self._image_bytes.append(fp.read())
            self._file_names.append(file_name)
            self._process_count += 1

    def __loadExpectedResults(self):
        for file in FILES:
            with open(EXPECTED_DIR + "/" + file, 'rb') as fp:
                self.__expected.append(pkl.load(fp))

    def _baseRun(self, target_fn):
        """
        executes a load test with one process for each image sending same request multiple time
        target_fn: function that every process should execute
                   messages_to_send x image_name -> ... (result ignored)
        """
        processes = []
        for i in range(self._process_count):
            process_messages = [
                PredictRequest(image_data=self._image_bytes[i], all_categories=True, all_attributes=True)
                for _ in range(self._num_dup)
            ]
            process = mp.Process(target=target_fn, args=(process_messages, self._file_names[i]))
            processes.append(process)

        start = time.time()
        # Start processes
        for p in processes:
            p.start()

        # Join processes
        for p in processes:
            p.join()
        stop = time.time()

        num_messages = self._num_dup * self._process_count
        elapsed_time = stop - start
        print(f'''TOTAL: {num_messages} messages in {elapsed_time} seconds''')
        print(f'''AVG: {num_messages / elapsed_time} messages per second''')

    def __check_all_categories(self, name, predict_response):
        predicted_categories = np.array([(el.label, el.value) for el in predict_response.categories])
        return check_all_aux(name, predicted_categories, self.__expected[1])

    def __check_all_attributes(self, name, predict_response):
        predicted_attributes = np.array([(el.label, el.value) for el in predict_response.attributes])
        return check_all_aux(name, predicted_attributes, self.__expected[3])

    def _check_predictions(self, file_name, predictions):
        self.assertEqual(len(predictions), self._num_dup)
        for prediction in predictions:
            self.assertTrue(self.__check_all_categories(file_name, prediction),
                            f'''Failure in file '{file_name}': Wrong categories''')
            self.assertTrue(self.__check_all_attributes(file_name, prediction),
                            f'''Failure in file '{file_name}': Wrong attributes''')