import unittest
import pickle as pkl
import numpy as np
import pandas as pd
import os

from keras.preprocessing import image
from keras.applications import vgg16
from src.server.context import Context
from src.model.prediction import PredictionHandler
from src.model.encoder import Encoder


DATA_DIR = "tests/data"
EXPECTED_DIR = "tests/expected"

FILES = [
    "predicted_categories_VSAM+FL_deepfashion.pkl",
    "predicted_categories_probs_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_VSAM+FL_deepfashion.pkl",
    "predicted_attributes_probs_VSAM+FL_deepfashion.pkl",
]


TOLERANCE = 1e-06


def load_encoder(file):
    with open(file, 'rb') as fp:
        params = pkl.load(fp)
    encoder = Encoder(*params)
    n_classes = len(encoder.encoder.classes_)
    return encoder, n_classes


def is_close_row(row1, row2):
    index1, values1 = row1
    index2, values2 = row2
    return index1 == index2 and all(np.isclose(values1, values2, rtol=TOLERANCE, atol=TOLERANCE))


def is_close_df(df1, df2):
    return all([
        is_close_row(row1, row2) for row1, row2 in zip(df1.iterrows(), df2.iterrows())
    ])


class PredictionHandlerUT(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self) -> None:
        config = Context()
        self.expected = []
        model_dir: str = config.model_dir
        categories_path: str = model_dir + '/' + config.ohe_categories
        attributes_path: str = model_dir + '/' + config.ohe_attributes
        weights_path: str = model_dir + '/' + config.weights
        self.categories_encoder, n_categories = load_encoder(categories_path)
        self.attributes_encoder, n_attributes = load_encoder(attributes_path)
        self.service = PredictionHandler(weights_path, n_categories, n_attributes)
        for file in FILES:
            with open(EXPECTED_DIR + "/" + file, 'rb') as fp:
                self.expected.append(pkl.load(fp))

    def __test_single_image(self, file_name):
        img = image.load_img(DATA_DIR + '/' + file_name, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = vgg16.preprocess_input(x)
        heatmap = np.random.randn(224, 224)
        heatmap = np.expand_dims(heatmap, axis=0)
        heatmap = np.expand_dims(heatmap, axis=3)
        result_x = self.service.predict([x, heatmap])

        # for multiclass - category level
        pred_cat2 = result_x[0]
        max_pred_indx = np.argmax(pred_cat2)
        prob_cat2 = np.max(pred_cat2)
        np_zeros_ones_array_cat2 = np.zeros([pred_cat2.shape[1], 1], dtype=np.int8)
        np_zeros_ones_array_cat2[max_pred_indx] = 1

        np_diagonal = np.zeros(shape=(pred_cat2.shape[1], pred_cat2.shape[1]))
        np.fill_diagonal(np_diagonal, 1)
        columns = [x[0] for x in self.categories_encoder.decode(np_diagonal)]

        y_pred_cat = pd.DataFrame(np.array(np_zeros_ones_array_cat2).reshape(1, -1), columns=columns).T
        y_pred_cat_expected = pd.DataFrame(self.expected[0].loc[file_name])
        self.assertTrue(is_close_df(y_pred_cat, y_pred_cat_expected))

        y_pred_probs_cat = pd.DataFrame(pred_cat2.reshape(1, -1), columns=columns).T
        y_pred_probs_cat_expected = pd.DataFrame(self.expected[1].loc[file_name])
        self.assertTrue(is_close_df(y_pred_probs_cat, y_pred_probs_cat_expected))

        # for multilabel - attributes level
        multi_label_threshold = 0.5  # threshold used when the focal loss is applied
        pred_att = result_x[1]
        np_pred_att_boolean = np.array(pred_att) > multi_label_threshold
        prob_att = pred_att[0][(np.where(np_pred_att_boolean)[1])]
        np_zeros_ones_array_att = np_pred_att_boolean.astype(int)

        np_diagonal = np.zeros(shape=(pred_att.shape[1], pred_att.shape[1]))
        np.fill_diagonal(np_diagonal, 1)
        columns = [x[0] for x in self.attributes_encoder.decode(np_diagonal)]

        y_pred_att = pd.DataFrame(np_zeros_ones_array_att, columns=columns).T
        y_pred_att_expected = pd.DataFrame(self.expected[2].loc[file_name])
        self.assertTrue(is_close_df(y_pred_att, y_pred_att_expected))

        y_pred_probs_att = pd.DataFrame(pred_att, columns=columns).T
        y_pred_probs_att_expected = pd.DataFrame(self.expected[3].loc[file_name])
        self.assertTrue(is_close_df(y_pred_probs_att, y_pred_probs_att_expected))

    def test_all_image(self):
        print()
        for file_name in os.listdir(DATA_DIR):
            print(f"""Testing Prediction {file_name}""")
            self.__test_single_image(file_name)