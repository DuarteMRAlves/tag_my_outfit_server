import grpc
import os

from itertools import zip_longest

from outfit_tagging.interface.service_pb2_grpc import TagMyOutfitServiceStub
from outfit_tagging.interface.service_pb2 import StreamPredictResponse
from tests.load.base_load_test import BaseLoadTest


class ClientStreamingLT(BaseLoadTest):

    @staticmethod
    def __batch_generator(iterable, n):
        args = [iter(iterable)] * n
        return zip_longest(*args)

    @staticmethod
    def __send_requests(requests, file_name):
        channel = grpc.insecure_channel("localhost:50051")
        stub = TagMyOutfitServiceStub(channel)
        num_requests = len(requests)
        print(f"""{os.getpid()} started for file {file_name}""")
        predictions = []
        batch_size, idx = 10, 0
        for batch in ClientStreamingLT.__batch_generator(requests, batch_size):
            response: StreamPredictResponse = stub.stream_predict(iter(batch))
            predictions.extend(response.predictions)
            idx += batch_size
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
        print("Client Streaming Performance Load Test")
        self._baseRun(self.__send_requests)

    def test_results(self):
        print()
        print("Client Streaming Assert Results Load Test")
        self._baseRun(self.__send_requests_checked)
