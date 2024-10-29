import json


class Payload(object):
    def __init__(self, j):
        self.results = None
        self.__dict__ = json.loads(j)
