import copy

def copy_all_state_nodes(state_nodes):
    copy = []
    for n in state_nodes:
        copy.append(n.copy())
    return copy

class StateNode:
    """A StateNode contains the state for a single entity. State is
    kept in key-value pairs. A StateNode is meant to be hosted within
    a Namespace. It keeps a reference to its namespace for easy access."""

    def __init__(self, namespace):
        self.values = {}
        self.namespace = namespace

    def get_namespace(self):
        return self.namespace

    def set(self, key, value):
        """If the key already exists it's overwritten."""
        self.values[key] = value

    def get(self, key):
        """Returns the value of the given key, or None."""
        if key in self.values:
            return self.values[key]

        return None

    def copy(self):
        """Returns a deep copy of this StateNode."""
        values = copy.deepcopy(self.values)

        clone = StateNode(self.namespace)
        clone.values = values

        return clone

    def to_kvp(self):
        form = {}
        form['type'] = 'StateNode';
        form['values'] = self.values
        return form
