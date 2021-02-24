import grpc
import os

from tag_my_outfit_pb2_grpc import TagMyOutfitServiceStub
from tests.load.base_load_test import BaseLoadTest


class ClientSingleRequestLT(BaseLoadTest):

    @staticmethod
    def __send_requests(requests, file_name):
        channel = grpc.insecure_channel("localhost:8061")
        stub = TagMyOutfitServiceStub(channel)
        num_requests = len(requests)
        print(f"""{os.getpid()} started for file {file_name}""")
        predictions = []
        for idx, request in enumerate(requests):
            predictions.append(stub.predict(request))
            if idx % 10 == 0:
                print(f"""{os.getpid()} at {idx} of {num_requests}""")
        print(f"""{os.getpid()} done""")
        channel.close()
        return predictions

    def __send_requests_checked(self, requests, file_name):
        predictions = self.__send_requests(requests, file_name)
        print(f"""{os.getpid()} checking results""")
        self._check_predictions(file_name, predictions)

    def test_performance(self):
        print()
        print("Client Single Request Performance Load Test")
        self._baseRun(self.__send_requests)

    def test_results(self):
        print()
        print("Client Single Request Assert Results Load Test")
        self._baseRun(self.__send_requests_checked)