import copy


class ThoughtNode:

    def __init__(self, thought=None):
        self.thought = thought
        self.connections = []
        self.log = []

    def _think(self, input):
        if callable(self.thought):
            return self.thought(input)
        else:
            return self.thought

    def execute(self, input=None, log=None):
        log = log or self.log
        log_step = {
            "step": self.__class__.__name__,
            "input": copy.deepcopy(input),
            "output": None,
        }
        log.append(log_step)
        response = self._think(input)
        log_step["output"] = response
        for connection in self.connections:
            if connection["condition"](response):
                return connection["node"].execute(response, log)
        return response

    def connect(self, node, condition=lambda x: True):
        self.connections.append({"node": node, "condition": condition})
