import unittest;
from environment import Environment;
from namespace import Namespace;

def func_time(state, connected_states):
    s = connected_states.pop()
    ls = s.get('lightspeed')

    t = 1 * (1 - ls)
    state.set('second_length', t)

def func_speed(state, _): # Has no connected states so ignores them
    ls = state.get('lightspeed')
    ls = ls + ls * 0.01
    state.set('lightspeed', ls)

def setup_time_testcase(e):
    sTime = e.add_function(func_time, 'physics.time', ['physics.speed'])
    sTime.set('second_length', 1.0)

    sSpeed = e.add_function(func_speed, 'physics.speed', [])
    sSpeed.set('lightspeed', 0.01)

def probe_speed(speed):
    print("Speed in Fractional Light Speed {}".format(speed))

def probe_time(second_length):
    print("Second Relative Length: {0}".format(second_length))

class TestEnvironment(unittest.TestCase):

    def test_environment_init(self):
        e = Environment()

    def test_register_function_init_called(self):
        e = Environment()

        setup_time_testcase(e)

        e.start_trace()
        for i in range(0, 100):
            e.tick()
        e.stop_trace()



    def test_probes(self):
        e = Environment()
        setup_time_testcase(e)
        e.add_probe("physics.time", "second_length", probe_time)
        e.add_probe("physics.speed", "lightspeed", probe_speed)

        for i in range(0, 100):
            e.tick()

    def test_injectors(self):

        def validate_speed(speed):
            self.assertEqual(2.0, speed)


        e = Environment()
        setup_time_testcase(e)

        e.add_probe("physics.speed", "lightspeed", probe_speed)
        i = e.get_injector("physics.speed", "lightspeed")

        i.set(2.0)

        e.tick()


class TestGraph(unittest.TestCase):

    def test_graph_shortest_path(self):
        g = Graph(
            [ (1, {'state': 'start'}),
              (2, {'thing': 'potato'}),
              (3, {'action': 'cut'}),
              (4, {'action': 'boil'}) ],

            [ (1, 2, {'cost': 1}),
              (2, 3, {'cost': 1}),
              (3, 4, {'cost': 2.4}) ]
            )

        g.add_node(5, {'action': 'eat'})
        g.add_edge(4, 5, {'cost': 2})

        path = g.lowest_cost_path_by('cost', 1, 5)
        print(path)


class TestNamespaces(unittest.TestCase):

    def test_namespace_insert(self):
        item = 'Viagras Staff + 3'

        root = Namespace('')
        root.insert('weapons.wizard.staff', item)
        root.insert('weapons.barbarian.clubs', 'The Morning Wood + 4')

        staff = root.get('weapons.wizard.staff')

        self.assertEqual(item, staff.pop())

        all_weapons = root.get('weapons')
        self.assertEqual(2, len(all_weapons))


if __name__ == '__main__':
    unittest.main()
