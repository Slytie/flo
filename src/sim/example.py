import unittest;
import numpy as np
from environment import Environment;
from namespace import Namespace;

class Example(unittest.TestCase):

    def test_environment_init(self):
        e = Environment()

        def wanting_carbs(state, connected_state):
            l = connected_state[0].get('level')
            w = 1/l
            state.set('wanting', w)

        cWanting = e.add_function(wanting_carbs, "seeking.carbs", ["physiology.blood.glucose"])
        cWanting.set('wanting', 0)

        def decision(state, connected_state):
            w = connected_state[0].get('wanting')
            v = connected_state[1].get('carb_volume')

            if w > 10:
                state.set('carbs', True)

            if v > 4:
                state.set('carbs', False)

        cDecision = e.add_function(decision, "decision.eat", ["seeking.carbs",'stomach.contents'])
        cDecision.set('carbs', False)

        def carb_consumption(state, connected_state):
            d = connected_state[0].get('carbs')
            c = state.get('carb_volume')
            c = c*0.95

            if d:
                c += 5
            state.set('carb_volume', c)

        cConsumption = e.add_function(carb_consumption, "stomach.contents", ["decision.eat", 'stomach.contents'])
        cConsumption.set('carb_volume', 10)

        def carb_metabolism(state, connected_state):
            d = connected_state[0].get('carb_volume')
            d2 = d*0.90
            b_s_c = d-d2
            l = state.get('level')
            l = l+b_s_c*2-l*(1-0.95)
            state.set('level', l)

        cMetabolism = e.add_function(carb_metabolism, 'physiology.blood.glucose', ["stomach.contents"])
        cMetabolism.set('level',1)

        '''
        def reduce_carb(state, connected_state):
            d = state.get('carb_volume')
            d = d*0.75
            state.set('carb_volume', d)

        cReduce = e.add_function(reduce_carb, 'stomach.contents', [])
        cReduce.set('carb_volume',10)
        '''

        def probe_glucose(level):
            print("Blood Glucose Level {}".format(level))

        def probe_wanting(want):
            print("Wanting carbs {}".format(want))

        def probe_carb_volume(vol):
            print("Stomach carb volume {}".format(vol))

        def probe_eat_decision(d):
            print("Stomach eat decision {}".format(d))

        e.add_probe('physiology.blood.glucose', 'level', probe_glucose)
        e.add_probe('seeking.carbs', 'wanting', probe_wanting)
        e.add_probe('stomach.contents', 'carb_volume', probe_carb_volume)
        e.add_probe('decision.eat', 'carbs', probe_eat_decision)

        for i in range(0, 1000):
            e.tick()


if __name__ == '__main__':
    unittest.main()
