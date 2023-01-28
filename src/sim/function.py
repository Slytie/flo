class Function:
    """A Function object encapsulates meta information about functions
    executing within the Environment. An encapsulated function acts as
    the primary mutator of the environment state."""

    def __init__(self, function, namespace, connected_namespaces):
        self.function = function
        self.namespace = namespace
        self.connected_namespaces = connected_namespaces

    def invoke(self, state, connected_state):
        self.function(state, connected_state)

    def get_namespace(self):
        return self.namespace

    def get_connected_namespaces(self):
        return self.connected_namespaces
