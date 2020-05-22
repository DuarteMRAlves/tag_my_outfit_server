import unittest
import numpy as np
from keras.preprocessing import image
from keras.applications import vgg16

from src.model.preprocess import PreprocessHandler


DATA_DIR = "tests/data"

FILES = [
    "209185-653175.jpg",
    "12012648_9451305_255.jpg",
    "12509914_12392960_255_rendered.png",
    "12887238_13144126_255.jpg",
    "bomberdoublezips_0000_06-07-2015_ami_zipbomberjacket_marine_1_jtl.jpg",
    "T1112914-Coral Blaze Ikat-1-P.jpg"
]


def read_file(file):
    with open(file, 'rb') as fp:
        return fp.read()


class PreprocessServiceTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected = {}
        self.target_size = (224, 224)
        self.service = PreprocessHandler(self.target_size)

    def setUp(self) -> None:
        for file in FILES:
            img = image.load_img(DATA_DIR + "/" + file, target_size=self.target_size)
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis=0)
            self.expected[file] = vgg16.preprocess_input(img)

    def test_data_image_preprocess_result(self):
        print()
        for file in FILES:
            print(f"""Testing Preprocess {file}""")
            image_data = read_file(DATA_DIR + '/' + file)
            img, _ = self.service.preprocess_image(image_data)
            self.assertTrue(np.all(np.equal(img, self.expected[file])))
