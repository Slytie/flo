class Injector:
    """An injector allows a values to be injected into StateNodes
    within an environment. The values are injected by their keys
    and done once per tick."""

    def __init__(self, state_node, key):
        self.state_node = state_node
        self.key = key
        self.value_set = False
        self.value = None

    def set(self, value):
        self.value_set = True
        self.value = value

    def inject(self):
        if self.value_set:
            self.state_node.set(self.key, self.value)

        self.value = None
        self.value_set = False
