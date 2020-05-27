import grpc
import pandas as pd
import pickle as pkl
import numpy as np
import os
import sys

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


def is_close_row(row1, row2):
    index1, values1 = row1
    index2, values2 = row2
    return index1 == index2 and all(np.isclose(values1, values2, rtol=TOLERANCE, atol=TOLERANCE))


def is_close_df(df1, df2):
    return all([
        is_close_row(row1, row2) for row1, row2 in zip(df1.iterrows(), df2.iterrows())
    ])


def loadExpectedResults():
    expected = []
    for file in FILES:
        with open(EXPECTED_DIR + "/" + file, 'rb') as fp:
            expected.append(pkl.load(fp))
    return expected


def check_not_all_categories(name, predict_response, expected):
    expected_df: pd.DataFrame = expected[0].loc[name]
    expected_prediction = expected_df[expected_df == 1].index[0]
    expected_prob_df: pd.DataFrame = expected[1].loc[name]
    expected_prob_prediction = expected_prob_df[expected_prediction]
    predicted_categories = predict_response.predicted_categories
    if len(predicted_categories) == 1 \
            and predicted_categories[0].label == expected_prediction \
            and np.isclose(predicted_categories[0].value, expected_prob_prediction, rtol=TOLERANCE):
        print(f"\t\tPredicted Categories: {AnsiColors.GREEN}SUCCESS{AnsiColors.NC}")
    else:
        print(f"\t\tPredicted Categories: {AnsiColors.RED}FAILURE{AnsiColors.NC}")


def check_not_all_attributes(name, predict_response, expected):
    expected_df: pd.DataFrame = expected[2].loc[name]
    expected_prediction = expected_df[expected_df == 1].index
    expected_prob_df: pd.DataFrame = expected[3].loc[name]
    expected_prob_prediction = expected_prob_df[expected_prediction]
    predicted_attributes = predict_response.predicted_attributes
    if len(expected_prediction) != len(predicted_attributes):
        print(f"\t\tPredicted Categories: {AnsiColors.RED}FAILURE{AnsiColors.NC}")
        return
    equal = True
    for expected_label, expected_prob, predicted \
            in zip(expected_prob_prediction.index, expected_prob_prediction, predicted_attributes):
        if expected_label != predicted.label or not np.isclose(expected_prob, predicted.value, rtol=TOLERANCE):
            equal = False
            break
    if equal:
        print(f"\t\tPredicted Attributes: {AnsiColors.GREEN}SUCCESS{AnsiColors.NC}")
    else:
        print(f"\t\tPredicted Attributes: {AnsiColors.RED}FAILURE{AnsiColors.NC}")


def check_all_aux(name, predicted, expected_df):
    predicted_attributes_df = pd.DataFrame(predicted[:, 1].reshape(1, -1).astype(np.double),
                                           columns=predicted[:, 0],
                                           index=[name]).T
    predicted_attributes_expected = pd.DataFrame(expected_df.loc[name])
    return is_close_df(predicted_attributes_df, predicted_attributes_expected)


def check_all_categories(name, predict_response, expected):
    predicted_categories = np.array([(el.label, el.value) for el in predict_response.predicted_categories])
    if check_all_aux(name, predicted_categories, expected[1]):
        print(f"\t\tPredicted Categories: {AnsiColors.GREEN}SUCCESS{AnsiColors.NC}")
    else:
        print(f"\t\tPredicted Categories: {AnsiColors.RED}FAILURE{AnsiColors.NC}")


def check_all_attributes(name, predict_response, expected):
    predicted_attributes = np.array([(el.label, el.value) for el in predict_response.predicted_attributes])
    if check_all_aux(name, predicted_attributes, expected[3]):
        print(f"\t\tPredicted Attributes: {AnsiColors.GREEN}SUCCESS{AnsiColors.NC}")
    else:
        print(f"\t\tPredicted Attributes: {AnsiColors.RED}FAILURE{AnsiColors.NC}")


def check_all_categories_all_attributes(name, image_bytes, expected):
    print()
    print("\tAll Categories, All Attributes")
    predict_request: PredictRequest = PredictRequest(image_data=image_bytes, all_categories=True, all_attributes=True)
    predict_response: PredictResponse = stub.predict(predict_request)
    # Check predicted categories
    check_all_categories(name, predict_response, expected)
    # Check predicted attributes
    check_all_attributes(name, predict_response, expected)


def check_not_all_categories_all_attributes(name, image_bytes, expected):
    print()
    print("\tNot All Categories, All Attributes")
    predict_request: PredictRequest = PredictRequest(image_data=image_bytes, all_categories=False, all_attributes=True)
    predict_response: PredictResponse = stub.predict(predict_request)
    # Check predicted category
    check_not_all_categories(name, predict_response, expected)
    # Check predicted attributes
    check_all_attributes(name, predict_response, expected)


def check_all_categories_not_all_attributes(name, image_bytes, expected):
    print()
    print("\tAll Categories, Not All Attributes")
    predict_request: PredictRequest = PredictRequest(image_data=image_bytes, all_categories=True, all_attributes=False)
    predict_response: PredictResponse = stub.predict(predict_request)
    # Check predicted categories
    check_all_categories(name, predict_response, expected)
    # Check predicted attributes
    check_not_all_attributes(name, predict_response, expected)


def check_not_all_categories_not_all_attributes(name, image_bytes, expected):
    print()
    print("\tNot All Categories, Not All Attributes")
    predict_request: PredictRequest = PredictRequest(image_data=image_bytes, all_categories=False, all_attributes=False)
    predict_response: PredictResponse = stub.predict(predict_request)
    # Check predicted categories
    check_not_all_categories(name, predict_response, expected)
    # Check predicted attributes
    check_not_all_attributes(name, predict_response, expected)


def test_file(name, expected):
    print()
    print(f"""Testing for file: '{name}'""")
    with open(DATA_DIR + '/' + name, 'rb') as f:
        image_bytes = f.read()
    check_all_categories_all_attributes(name, image_bytes, expected)
    check_not_all_categories_all_attributes(name, image_bytes, expected)
    check_all_categories_not_all_attributes(name, image_bytes, expected)
    check_not_all_categories_not_all_attributes(name, image_bytes, expected)


if __name__ == '__main__':
    channel = grpc.insecure_channel("localhost:50051")
    stub = PredictionServiceStub(channel)
    expected_results = loadExpectedResults()
    for file_name in os.listdir(DATA_DIR):
        test_file(file_name, expected_results)
