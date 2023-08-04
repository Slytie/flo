def perceptual_prediction(state, connected_states):
    """
    Calculate the Bayesian probabilities for a batch of sensorial vectors V and classify them based on the form with the highest Bayesian probability.

    Args:
        state (dict): A dictionary representing the state of the system. The keys should include 'V', 'paradigm_activation',
            'P_potentiality_given_form', 'P_form_given_context', 'means', 'covariances', 'weights', 'distance_cutoff', and 'weights_activation'.
        connected_states (list): A list of states that are connected to the current state. Not used in this function.

    Modifies:
        state: Adds the key 'bayesian_probabilities' to the state dictionary with the calculated Bayesian probabilities as its value.

    Returns:
        None
    """
    # Extract parameters from the state dictionary
    V = state['V']  # batch of sensorial vectors
    A_t = state['paradigm_activation']  # current paradigm activation states for each form
    P_potentiality_given_form = state['P_potentiality_given_form']  # P(potentiality|form) for each form
    P_form_given_context = state['P_form_given_context']  # P(form|context) for each form
    means = state['means']  # means of the GMM
    covariances = state['covariances']  # covariances of the GMM
    weights = state['weights']  # weights of the GMM
    distance_cutoff = state['distance_cutoff']  # distance cutoff
    w1, w2, w3 = state['weights_activation']  # weights for updating the paradigm activation state

    bayesian_probabilities = []
    for v in V:
        # Calculate Bayesian probability for each form
        P_H_E_form = []
        for i in range(len(means)):
            # Update paradigm activation state
            A_t_plus_1 = w1 * A_t[i] + w2 * P_form_given_context[i] + w3 * P_potentiality_given_form[i]
            state['paradigm_activation'][i] = A_t_plus_1

            # Prior probability
            P_H = A_t_plus_1

            # Likelihood
            P_E_H = multivariate_normal.pdf(v, mean=means[i], cov=covariances[i])

            # Total probability of evidence
            P_E = np.sum([weight * multivariate_normal.pdf(v, mean=mean, cov=cov) for weight, mean, cov in zip(weights, means, covariances) if np.linalg.norm(v - mean) <= distance_cutoff])

            # Bayes' theorem
            P_H_E = P_E_H * P_H / P_E

            P_H_E_form.append(P_H_E)

        # Classify the vector based on the form with the highest Bayesian probability
        classification = np.argmax(P_H_E_form)
        bayesian_probabilities.append((v, classification))

    # Update the state dictionary with the calculated Bayesian probabilities
    state['bayesian_probabilities'] = bayesian_probabilities


def softmax_function(state, connected_states):
    # Retrieve the path_IDs
    path_IDs = state.get('path_IDs')

    # Retrieve the additional state variables
    epsilon = state.get('global.epsilon')  # The global energy of the agent
    w0 = state.get('global.w0')  # The total work difference required for the current path and not changing path.
    D = state.get('global.D')  # The global suffering of the agent
    S = state.get('global.S')  # The global satisfaction of the agent

    # For each path_ID, retrieve its attributes, combine them, and put them into the state vector
    state_vector = []
    for path_ID in path_IDs:
        attributes = state.get_connected_states('paradigm_ID.' + str(path_ID))
        w = state.get('path.' + str(path_ID) + '.w')  # The total work required for the specific path

        # Calculate F, G, H, L
        F = sum([f(a_j, beta_j, D) for a_j, beta_j in attributes])  # The total change in beliefs resulting in a decrease in suffering for the different paradigms. beta_j is the change in beliefs for the jth paradigm. a_j is the paradigm activation level for the jth paradigm.
        G = sum([g(a_j, beta_j, S) for a_j, beta_j in attributes])  # The total change in beliefs resulting in an increase in satisfaction for the different paradigms 
        H = sum([h(a_j, beta_j, D) for a_j, beta_j in attributes])  # The total change in beliefs resulting in an increase in suffering for the different paradigms 
        L = sum([l(a_j, beta_j, S) for a_j, beta_j in attributes])  # The total change in beliefs resulting in a decrease in satisfaction for the different paradigms. 
        
        # Calculate d_+ and d_-
        d_plus = F+G  # Desire to have the positive consequences, ie decrease in suffering and increase in satisfaction
        d_minus = H+L  # Desire not to have the negative consequences, ie increase in suffering, decrease in satisfaction
        
        # Calculate s_i
        s_i = epsilon / (w + w0) * (d_plus - d_minus)  # Energy divided by work multiplied by the difference in desire and aversion of the choice
        
        state_vector.append(s_i)

    # Convert the state vector to a numpy array
    state_vector = np.array(state_vector)

    # Apply the softmax function
    softmax_vector = np.exp(state_vector) / np.sum(np.exp(state_vector))

    # Update the state
    state.set('state_vector', softmax_vector.tolist())

from sklearn.mixture import GaussianMixture

def generate_test_gmm_and_data(n_components=3, random_state=0):
    """
    Generate a test Gaussian Mixture Model and test data.

    Args:
        n_components (int, optional): The number of mixture components. Defaults to 3.
        random_state (int, optional): Determines random number generation for reproducibility. Defaults to 0.

    Returns:
        gmm (GaussianMixture): The generated Gaussian Mixture Model.
        state (dict): A dictionary with the test data as state variables.
    """
    # Create a Gaussian Mixture Model
    gmm = GaussianMixture(n_components=n_components, random_state=random_state)
    gmm.means_ = np.array([[0, 0], [1, 1], [2, 2]])
    gmm.covariances_ = np.array([[[1, 0], [0, 1]], [[1, 0], [0, 1]], [[1, 0], [0, 1]]])
    gmm.weights_ = np.array([0.3, 0.4, 0.3])
    gmm.precisions_cholesky_ = np.linalg.cholesky(np.linalg.inv(gmm.covariances_))

    # Generate test data
    state = dict()
    state['V'] = np.random.rand(2)  # sensorial vector
    state['paradigm_activation'] = np.random.rand()  # current paradigm activation state
    state['P_potentiality_given_form'] = np.random.normal(np.sqrt(5), 1)  # P(potentiality|form) from a Gaussian distribution
    state['P_form_given_context'] = np.random.rand()  # P(form|context) randomly generated for now
    state['means'] = gmm.means_
    state['covariances'] = gmm.covariances_
    state['weights'] = gmm.weights_
    state['distance_cutoff'] = 2.0
    state['weights_activation'] = np.array([0.3, 0.4, 0.3])  # weights for updating the paradigm activation state

    return gmm, state

