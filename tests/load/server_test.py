import grpc
import multiprocessing as mp
import numpy as np
import os
import pandas as pd
import pickle as pkl
import sys
import time

# Add sources dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from contract.service_pb2_grpc import PredictionServiceStub
from contract.service_pb2 import PredictRequest, PredictResponse


class AnsiColors:
    """
    Aux class to define colors
    """
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    NC = '\033[m'


DATA_DIR = "tests/data"
EXPECTED_DIR = "tests/expected"
FILES = [
    "predicted_categories_VSAM+FL_deepfashion.pkl",
    "predicted_categories_probs_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_probs_VSAM+FL_deepfashion.pkl",
]
TOLERANCE = 1e-06


def loadExpectedResults():
    expected = []
    for file in FILES:
        with open(EXPECTED_DIR + "/" + file, 'rb') as fp:
            expected.append(pkl.load(fp))
    return expected


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


def check_all_categories(name, predict_response, expected):
    predicted_categories = np.array([(el.label, el.value) for el in predict_response.predicted_categories])
    return check_all_aux(name, predicted_categories, expected[1])


def check_all_attributes(name, predict_response, expected):
    predicted_attributes = np.array([(el.label, el.value) for el in predict_response.predicted_attributes])
    return check_all_aux(name, predicted_attributes, expected[3])


def check_predictions(file_name, predictions, expected):
    success = True
    for predict in predictions:
        if not check_all_attributes(file_name, predict, expected):
            success = False
        if not check_all_categories(file_name, predict, expected):
            success = False
    if success:
        print(f"""{os.getpid()}: {AnsiColors.GREEN}SUCCESS{AnsiColors.NC}""")
    else:
        print(f"""{os.getpid()}: {AnsiColors.RED}FAILURE{AnsiColors.NC}""")


def send_requests(requests, file_name, expected):
    channel = grpc.insecure_channel("localhost:50051")
    stub = PredictionServiceStub(channel)
    num_requests = len(requests)
    print(f"""{os.getpid()} started for file {file_name}""")
    predictions = []
    for idx, request in enumerate(requests):
        predictions.append(stub.predict(request))
        if idx % 10 == 0:
            print(f"""{os.getpid()} at {idx} of {num_requests}""")
    print(f"""{os.getpid()} done""")
    # Uncomment to check results, Comment for performance test
    # print(f"""{os.getpid()} checking results""")
    # check_predictions(file_name, predictions, expected)


if __name__ == '__main__':
    images_data = []
    file_names = []
    process_count = 0
    # Get data
    for file_name in os.listdir(DATA_DIR):
        with open(DATA_DIR + '/' + file_name, 'rb') as fp:
            images_data.append(fp.read())
        file_names.append(file_name)
        process_count += 1

    # Get expected results
    expected_results = loadExpectedResults()

    # Create processes
    num_dup = 50
    processes = []
    for i in range(process_count):
        process_messages = [
            PredictRequest(image_data=images_data[i], all_categories=True, all_attributes=True)
            for _ in range(num_dup)
        ]
        process = mp.Process(target=send_requests,
                             args=(process_messages, file_names[i], expected_results))
        processes.append(process)

    start = time.time()
    # Start processes
    for p in processes:
        p.start()

    # Join processes
    for p in processes:
        p.join()
    stop = time.time()

    print(f"""TOTAL: {num_dup * process_count} messages in {stop - start} seconds""")
    print(f"""AVG: {(num_dup * process_count) / (stop - start)} messages per second""")
