# CauseEffectMapping class definition to handle complex outcomes with multiple variables
import numpy as np

def tokenize_conditions(conditions):
    """
    Tokenize the logical conditions into individual tokens.

    Args:
        conditions (str): The logical conditions as a string.

    Returns:
        list: A list of tokens representing the logical conditions.
    """
    tokens = []
    i = 0
    while i < len(conditions):
        if conditions[i] in ['(', ')']:
            tokens.append(conditions[i])
        elif conditions[i] == ' ':
            i += 1
            continue
        elif conditions[i:i + 3] == "AND" or conditions[i:i + 2] == "OR" or conditions[i:i + 3] == "NOT":
            if conditions[i:i + 3] == "AND":
                tokens.append("AND")
                i += 2
            elif conditions[i:i + 2] == "OR":
                tokens.append("OR")
                i += 1
            elif conditions[i:i + 3] == "NOT":
                tokens.append("NOT")
                i += 2
        else:
            j = i
            while j < len(conditions) and conditions[j] not in [' ', '(', ')']:
                j += 1
            tokens.append(conditions[i:j])
            i = j - 1
        i += 1
    return tokens

def evaluate_logical_expression(expression):
    """
    Evaluate a logical expression in postfix notation.

    Args:
        expression (list): A list of tokens representing the logical expression.

    Returns:
        bool: The result of evaluating the logical expression.
    """

    operators = {'NOT': 3, 'AND': 2, 'OR': 1}
    stack = []
    postfix = []

    for token in expression:
        if token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        elif token in operators:
            while stack and operators.get(token, 0) <= operators.get(stack[-1], 0):
                postfix.append(stack.pop())
            stack.append(token)
        else:
            postfix.append(token)

    while stack:
        postfix.append(stack.pop())

    for token in postfix:
        if token == "NOT":
            operand = stack.pop()
            stack.append(not operand)
        elif token in ["AND", "OR"]:
            operand2 = stack.pop()
            operand1 = stack.pop()
            if token == "AND":
                stack.append(operand1 and operand2)
            else:
                stack.append(operand1 or operand2)
        else:
            stack.append(token)

    return stack[0]

class CauseEffectMapping:
    """
    A class for mapping between causes and effects with logical rules.

    Attributes:
        rules (list): A list of logical rules for cause-effect relationships.
    """
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        """
            Add a logical rule to the mapping.

        Args:
            rule (str): The logical rule as a string, including conditions and effects.
        """
        
        conditions, effects = rule.split(' THEN ')
        conditions = conditions[3:]
        effects = effects.split(' with probability P=')
        effect_outcomes = []
        for i in range(1, len(effects), 2):
            effect_conditions = effects[i - 1].split('EITHER ')[-1].split(', or ')
            probability = float(effects[i].split(',')[0])
            for effect_condition in effect_conditions:
                effect_causes = {cond.split('=')[0]: int(cond.split('=')[1]) for cond in effect_condition.split(' AND ') if '=' in cond}
                effect_outcomes.append((effect_causes, probability))
        self.rules.append((conditions, effect_outcomes))

    def evaluate_conditions(self, conditions, causes):
        """
        Evaluate logical conditions based on given causes.

        Args:
            conditions (str): The logical conditions as a string.
            causes (dict): A dictionary of known causes.

        Returns:
            bool: The result of evaluating the conditions with the given causes.
        """
        tokens = tokenize_conditions(conditions)
        for i in range(len(tokens)):
            if tokens[i] in causes:
                tokens[i] = causes[tokens[i]]
            elif '=' in tokens[i]:
                var, value = tokens[i].split('=')
                tokens[i] = causes.get(var) == int(value)
        return evaluate_logical_expression(tokens)

    def predict_forward(self, causes):
        """
        Predict effects based on given causes.

        Args:
            causes (dict): A dictionary of known causes.

        Returns:
            dict: A dictionary of predicted effects.
        """
        combined_effects = {}
        for conditions, effect_outcomes in self.rules:
            condition_evaluation_result = self.evaluate_conditions(conditions, causes)
            if condition_evaluation_result:
                for outcome, probability in effect_outcomes:
                    for k, v in outcome.items():
                        if k not in combined_effects or combined_effects[k] != v:
                            combined_effects[k] = v
        return combined_effects

    def predict_backward(self, effects):
        """
        Predict possible causes based on given effects.

        Args:
            effects (dict): A dictionary of known effects.

        Returns:
            dict: A dictionary of possible causes with associated probabilities.
        """
        possible_causes = {}
        for conditions, effect_outcomes in self.rules:
            for outcome, probability in effect_outcomes:
                if all(outcome.get(key) == value for key, value in effects.items() if key in outcome):
                    possible_causes[conditions] = possible_causes.get(conditions, 0) + probability
        total_probability = sum(possible_causes.values())
        possible_causes = {condition: prob / total_probability for condition, prob in possible_causes.items()}
        return possible_causes


# Test with complex outcomes
def test_logic():
    mapping_complex_outcomes = CauseEffectMapping()
    mapping_complex_outcomes.add_rule("IF A=1 OR D=1 THEN EITHER D=1 AND C=2 with probability P=0.3, or E=1 AND F=2 with probability P=0.7")
    mapping_complex_outcomes.add_rule("IF F=1 OR D=1 THEN EITHER D=1 AND C=2 with probability P=0.1, or A=1 AND D=2 with probability P=0.7")
    mapping_complex_outcomes.add_rule("IF A=1 AND D=1 THEN A=1 AND D=1 with probability P=0.9, or E=1 AND F=2 with probability P=0.1")

    initial_causes_complex = {'D': 1}
    predicted_effects_forward_complex = mapping_complex_outcomes.predict_forward(initial_causes_complex)

    predicted_effects_backward_complex = {'E': 1, 'F': 2}
    predicted_causes_backward_complex = mapping_complex_outcomes.predict_backward(initial_causes_complex)

    print(predicted_effects_forward_complex)
    print(predicted_causes_backward_complex)
