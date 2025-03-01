class ThoughtNode:

    def __init__(self, thought=None):
        self.thought = thought
        self.connections = []

    def _think(self, input):
        if callable(self.thought):
            return self.thought(input)
        else:
            return self.thought

    def execute(self, input=None):
        response = self._think(input)
        for connection in self.connections:
            if connection["condition"](response):
                return connection["node"].execute(response)
        return response

    def connect(self, node, condition=lambda x: True):
        self.connections.append({"node": node, "condition": condition})
