from state_node import StateNode, copy_all_state_nodes
from function import Function
from namespace import Namespace
from probe import Probe
from injector import Injector
from utils import timestamp
import json
import os

class Environment:
    """A Simulation Environment. An Environment is the global
    container for Simulation state. It also containers functions for
    ticking the simulation forward."""

    def __init__(self, trace_path = './trace'):
        self.time = 0;
        self.state = Namespace()
        self.functions = Namespace()
        self.root = Namespace()
        self.probes = []
        self.injectors = {}
        self.trace = False
        self.init_timestamp = timestamp()
        self.trace_path = trace_path

        if not os.path.exists(self.trace_path):
            os.makedirs(self.trace_path)

    def tick(self):
        """The tick function iterates the environment by one
        step. Note, that tick here does not denote time, but rather a
        discrete iteration of the environment.

        During an iteration, the environment:
           1) If trace is enabled, traces states and functions.
           2) Iterates through the functions.
           3) Gets state and connected states for the functions.
           4) Executes the functions with the states.
           5) Calls the probes with the values.
           6) Adds injected values into states."""

        if self.trace:
            self.write_trace()

        self.time = self.time + 1

        fun_iterator = self.functions.iterator()

        for f in fun_iterator:
            function = f.item
            namespace = function.get_namespace()
            connected_namespaces = function.get_connected_namespaces()

            state = self.state.get(namespace)
            state = state.pop()

            connected_states = []
            for cns in connected_namespaces:
                connected_states.extend(self.state.get(cns))

            connected_states_copy = copy_all_state_nodes(connected_states)

            function.invoke(state, connected_states_copy)

        for p in self.probes:
            p.invoke()

        for i in self.injectors.values():
            i.inject()


    def add_function(self, function, namespace, connected_namespaces):
        """Adds a function with a given namespace to the
        environment. A namespace is a name in the form
        org.suborg.name. A namespace can be searched for either in
        full for a single match or partial (org.suborg) for a list of
        matches within the namespace.

        The connected_namespaces are namespaces
        that the function is connected to, that are created
        by other functions. This is a mechanism for creating inter
        dependencies within functions through
        namespaces.

        I.e. functions never call each other directly, but
        interact through namespaces, mediated by the environment. A
        single namespace may match only a single function, however
        multiple functions may be matched by a namespace
        pattern. I.e. org.suborg.function_a and org.suborg.function_b
        both match the org.suborg pattern."""

        s = StateNode(namespace);
        self.state.insert(namespace, s)

        f = Function(function, namespace, connected_namespaces)
        self.functions.insert(namespace, f)

        return s

    def add_probe(self, namespace, key, callback):
        """Adds a probe into the environment. A probe allows an
        external application to view internal environment state. State
        is encapsulated in StateNodes that have key value pairs. A
        probe allows an external application to get a single value from
        a StateNode for a given Key."""

        s = self.state.get(namespace)
        if len(s) == 0:
            raise "Namespace does not have a StateNode"

        if len(s) != 1:
            raise "Namespace has multiple StateNodes. A probe targets a single."

        s = s.pop()

        value = s.get(key)

        if value == None:
            raise "There is no value attached to that key."

        p = Probe(s, key, callback)
        self.probes.append(p)

    def get_injector(self, namespace, key):
        """Creates and returns an Injector for the environment. An
        Injector allows calling code to set the value of a single Key
        within the StateNode that is attached to the Function."""

        s = self.state.get(namespace)

        if len(s) == 0:
            raise "Namespace does not have a StateNode."

        if len(s) != 1:
            raise "Namespace has multiple StateNodes. An injector targets a single."

        s = s.pop()

        value = s.get(key)

        if value == None:
            raise "The key was not found."

        i = Injector(s, key)

        injector_key = "{}.{}".format(namespace, key)

        self.injectors[injector_key] = i

        return i

    def to_json(self):
        form = []
        form.append(self.state.to_kvp())
        form.append(self.functions.to_kvp())

        return json.dumps(form, sort_keys=True, indent=4);

    def write_trace(self):
        filename = '{0}-tick-{1}.json'.format(self.init_timestamp, self.time)
        file_path = '{0}/{1}'.format(self.trace_path, filename)
        with open(file_path, 'w') as f:
            f.write(self.to_json())


    def start_trace(self):
        self.trace = True

    def stop_trace(self):
        self.trace = False
