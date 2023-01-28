import unittest;
from environment import Environment;
from namespace import Namespace;

class Example(unittest.TestCase):

    def test_environment_init(self):
        e = Environment()

        def sim_blood_sugar_level(state, connected_state):
            l = state.get('level')
            l = l * 0.95

            ate = state.get('just_ate')
            if ate:
                l = l + 100

            state.set('level', l)
            state.set('just_ate', False)

        sGlucose = e.add_function(sim_blood_sugar_level, "physiology.blood.glucose", [])
        sGlucose.set('level', 1.0)
        sGlucose.set('just_ate', False)

        def sim_salience_smell_of_pizza(state, connected_state):
            stateG = connected_state.pop()
            l = stateG.get('level')
            s = state.get('need')
            s = s * 1.0 / l
            state.set('need', s)

        sSalience = e.add_function(sim_salience_smell_of_pizza, "physiology.brain.salience", ['physiology.blood.glucose'])
        sSalience.set('need', 10.0)

        def probe_glucose(level):
            print("Blood Glucose Level {}".format(level))

        def probe_need(need):
            print("Need {}".format(need))

        e.add_probe('physiology.blood.glucose', 'level', probe_glucose)
        e.add_probe('physiology.brain.salience', 'need', probe_need)

        for i in range(0, 10):
            e.tick()

        i_eat_pizza = e.get_injector('physiology.blood.glucose', 'just_ate')
        i_eat_pizza.set(True)

        for i in range(0, 10):
            e.tick()

if __name__ == '__main__':
    unittest.main()
