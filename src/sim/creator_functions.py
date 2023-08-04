import numpy as np

class KalmanFilterCreate:
    def __init__(self, state_dim, observation_dim, A_ns, Q_ns, H_ns, R_ns, N=0, discount_factor=1.0):
        """
        Creates a Kalman filter function that can be used within the Flo Simulation Engine.

        Args:
            state_dim (int): Dimension of the state vector.
            observation_dim (int): Dimension of the observation vector.
            A_ns (str): Namespace for the state transition matrix.
            Q_ns (str): Namespace for the process noise covariance.
            H_ns (str): Namespace for the observation matrix.
            R_ns (str): Namespace for the measurement noise covariance.
            N (int): Number of timesteps to predict into the future. Default is 0.
            discount_factor (float): Time-discount factor for future predictions. Default is 1.0 (no discounting).
        """

        def kalman_filter(state, connected_states):
            # Unpack state variables
            current_estimate = state.get('current_estimate')
            P = state.get('P')

            # Get required inputs from connected states
            A = connected_states.get(A_ns)  # Dynamic transition matrix
            Q = connected_states.get(Q_ns)
            H = connected_states.get(H_ns, np.zeros((observation_dim, state_dim)))
            R = connected_states.get(R_ns)

            # Check dimensions
            if A.shape != (state_dim, state_dim) or Q.shape != (state_dim, state_dim) or R.shape != (observation_dim, observation_dim):
                raise ValueError("Inconsistent dimensions for A, Q, or R matrices.")

            # Prediction Step
            predicted_estimate = A @ current_estimate
            P = A @ P @ A.T + Q

            # Update Step
            for observation_namespace in connected_states:
                if 'observation' in observation_namespace:
                    observation = connected_states.get(observation_namespace)
                    if observation.shape[0] != observation_dim:
                        raise ValueError("Inconsistent observation dimension.")

                    y = observation - H @ predicted_estimate
                    S = H @ P @ H.T + R
                    K = P @ H.T @ np.linalg.inv(S)
                    updated_estimate = predicted_estimate + K @ y
                    P = (np.eye(state_dim) - K @ H) @ P

            # Future Prediction if N > 0
            future_state = state.copy()
            time_discounted_sum = np.zeros(state_dim)
            discount = 1.0
            for _ in range(N):
                future_state = kalman_filter(future_state, connected_states)
                if future_state is None:  # Reached a final state
                    break
                current_estimate_future = future_state['current_estimate']
                time_discounted_sum += discount * current_estimate_future
                discount *= discount_factor

            state['future_prediction'] = time_discounted_sum

            # Update state
            state['current_estimate'] = updated_estimate
            state['P'] = P

            return state

        self.kalman_filter = kalman_filter

    def get_filter_function(self):
        """Returns the Kalman filter function."""
        return self.kalman_filter


class ParticleFilterCreate:
    def __init__(self, state_dim, observation_dim, num_particles, transition_fn_ns, observation_fn_ns, N=0, discount_factor=1.0):
        """
        Creates a particle filter function that can be used within the Flo Simulation Engine.

        Args:
            state_dim (int): Dimension of the state vector.
            observation_dim (int): Dimension of the observation vector.
            num_particles (int): Number of particles in the filter.
            transition_fn_ns (str): Namespace for the transition function.
            observation_fn_ns (str): Namespace for the observation function.
            N (int): Number of timesteps to predict into the future. Default is 0.
            discount_factor (float): Time-discount factor for future predictions. Default is 1.0 (no discounting).
        """

        def particle_filter(state, connected_states):
            # Unpack state variables
            particles = state.get('particles')
            weights = state.get('weights')

            # Get required transition and observation functions from connected states
            transition_fn = connected_states.get(transition_fn_ns)
            observation_fn = connected_states.get(observation_fn_ns)

            # Resampling
            indices = np.random.choice(range(num_particles), size=num_particles, p=weights)
            particles = particles[indices]
            weights = np.ones(num_particles) / num_particles

            # Prediction Step
            for i in range(num_particles):
                particles[i] = transition_fn(particles[i])

            # Update Step
            for observation_namespace in connected_states:
                if 'observation' in observation_namespace:
                    observation = connected_states.get(observation_namespace)
                    if observation.shape[0] != observation_dim:
                        raise ValueError("Inconsistent observation dimension.")

                    # Update weights based on observation likelihood
                    for i in range(num_particles):
                        likelihood = observation_fn(particles[i], observation)
                        weights[i] *= likelihood

                    # Normalize weights
                    weights /= np.sum(weights)

            # Future Prediction if N > 0
            future_state = state.copy()
            time_discounted_sum = np.zeros(state_dim)
            discount = 1.0
            for _ in range(N):
                future_state = particle_filter(future_state, connected_states)
                if future_state is None:  # Reached a final state
                    break
                current_estimate_future = np.average(future_state['particles'], weights=future_state['weights'], axis=0)
                time_discounted_sum += discount * current_estimate_future
                discount *= discount_factor

            state['future_prediction'] = time_discounted_sum

            # Update state
            state['particles'] = particles
            state['weights'] = weights

            return state

        self.particle_filter = particle_filter

    def get_filter_function(self):
        """Returns the particle filter function."""
        return self.particle_filter
