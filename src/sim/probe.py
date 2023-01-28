class Probe:
    """A Probe represents and external outlet for state that exists
    within an environment namespace."""

    def __init__(self, state_node, key, callback):
        self.state_node = state_node
        self.key = key
        self.callback = callback

    def invoke(self):
        value = self.state_node.get(self.key)
        self.callback(value)
