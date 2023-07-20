# Flo Simulation Engine

The Flo Simulation engine implements a set of classes and functions that can be used together to simulate any kind of system. For usage see this document as well as the unit tests found in `test.py`.

## Engine Architecture

### The Environment
The overall container for the simulation is the `Environment` object.

```python
e = Environment()
```

The simulation can be moved a step forward with `Environment.tick()`

```python
e = Environment()
e.tick()
```

The `tick` method represents a forward step of the Environment and is not related to time. Time itself can be simulated within the Environment using the simulation functions.

The Environment can be made to trace the internal state (that is the StateNode namespace and the Function namespace) by calling the `start_trace` method. It can be stopped by using the `stop_trace` method. By default the environment will trace each tick to a directory by the name `./trace`. This can be overriden by passing the first argument into environment with a custom trace location:

```python
e = Environment('/some/other/path')
```


### Namespaces

A `Namespace` is a logical heirachy of related names. Namespaces are used internally by the environment and externally when functions request related state. A *Namespace* looks like this:

    physiology.blood.glucose

The sub namespace *blood* may contain other namespaces such as:

    physiology.blood.platelets

Each complete *Namespace* can have a single item attached to it. The item is an arbitary Python object. A namespace can also be queries for groups, pulling out all items within the group. For example searching for *physiology.blood* will return both *glucose* and *platelets*.

### StateNode

A `StateNode` is the atomic representation of state within an Environment. I.e. all operations on state is done with StateNodes. A `StateNode` itself has a collection of key-valye paired variables within it. Generally, StateNodes are created for you by the environment when you create a function.

### Functions

Functions form the core of the actual simulation. A function wraps a plain Python function of the form:

```python
def name(state, connected_states):
```

Here the `state` refers to mutable state that is attached to the function. Any changes to state is visible as soon as it is made to any other function requesting that state (through *Namespaces*, more on that later). The `connected_state` is a copy of connected states that the function is requesting. Changes to these states will be discarded after the function is run.

In other words, a function can only change its own `state`. A plain Python function with the appropriate signature can be attached to the environment like so:

```python
e = Environment()
sTime = e.add_function(func_time, 'physics.time', ['physics.speed'])
```

The first parameter to the `add_function` method is the plain Python function that will be used as a callback. The second parameter is the `Namespace` of the state that the function will be allowed to change. the third parameter is an array of namespaces that the function requires to do it's internal calculations.

The return value of the `add_function` method is a `StateNode` that represents the internal state of the function. The `StateNode` can be used for initialization of required key-value pairs before the first call to `tick`.

```python
    sTime = e.add_function(func_time, 'physics.time', ['physics.speed'])
    sTime.set('second_length', 1.0)
```

Once a function is added to the environment, it will be called at each `tick`. It will recieve a mutable version of it's own state (as defined by the namespace) and a list of copies of state from other functions.

```python
def func_time(state, connected_states):
    s = connected_states.pop()
    ls = s.get('lightspeed')

    t = 1 * (1 - ls)
    state.set('second_length', t)
```

### Probes
Probes allow external calling code to recieve updates on a specific key-value within a specified namespaced `StateNode`.

A probe callback function has the form:

```python
def probe_time(second_length):
    print("Second Relative Length: {0}".format(second_length))
```

The single parameter is the parameter that is requested during the `Probe` registration.

```python
e = Environment()
...
e.add_probe("physics.time", "second_length", probe_time)
```

The first parameter refers to the namespace of the `StateNode` that the `Probe` is interested in. The second parameter refers to the key within the `StateNode` and the last parameter is the callback that will recieve the value.

The probe function will be called once per `tick` with the current value of the requested key.

### Injectors

Injectors perform the opposite functionality of a Probe, in that they allow an external caller to set the value of a key within a given namespaced `StateNode`. For example, an `Injector` can be used to update the number of cups of coffee a simulated person has had. Together with `Probes`, `Injectors` can be used to read-modify values after a `tick`.

An injector is created within an `Environment` by calling the `get_injector` method.

```python
e = Environment()
i = e.get_injector("physics.speed", "lightspeed")
```

The first parameter is the `Namespace` of the `StateNode` that is being targeted. The second parameter is the key within the `StateNode` that can is being modified. The key must exist prior to be used with an `Injector`.

Now later on during the execution of code external to the `Environment`, the injector can be called with a new value of it's target:

```python
i.set(2.0)
```

Each *{namespace, key}* pair may have a unique injector. If the same *{namespace, key}* pair is used for more than a single injector then the one created last will be used.

### Call Order

When `tick` is called on an `Environment` object it goes through the following steps in order:

1. If trace is enabled, traces the state to the trace directory.
2. Iterates through the functions.
3. Gets state and connected states for the funcions using namespaces.
4. Executes the functions with the states.
5. Calls the probes with the values.
6. Adds injected values into states.

It's important to remember that `Probes` are called before `Injector` values are injected back into the environment. This means that state can be read by `Probes` and action taken through `Injectors`.

## Function types
### Softmax function for path choosing ie decision making
In our simulation, we use a customized softmax function to represent the decision-making process of choosing a path. Each element in the state vector represents a decision or path, identified by a path_ID. The state vector is transformed into a decision probability vector by applying our softmax function. The probability associated with each decision or path is used to determine the path to take.

Here is the updated softmax_function pulling epsilon, w, w0, D, and S from the state namespace:
```python
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
```
```python
def f(a_j, beta_j, D):
    # Placeholder function, should be  f(\cdot )>0. Change in belief resulting in a decrease in suffering
    x=a_j + beta_j + D
    return np.exp(x) - 1

def g(a_j, beta_j, S):
    # Placeholder function, should be g(\cdot )>0. Change in belief resulting in an increase in satisfaction
    x=a_j + beta_j + S
    return  1 / (np.exp(x) - 1)

def h(a_j, beta_j, D):
    # Placeholder function, should be h(\cdot )>0.  Change in belief resulting in an increase in suffering
    x=a_j + beta_j + D
    return np.exp(x) - 1

def l(a_j, beta_j, S):
    # Placeholder function, should be l(\cdot )>0. Change in belief resulting in an increase in satisfaction
    x=a_j + beta_j + S
    return  1 / (np.exp(x) - 1)
```

