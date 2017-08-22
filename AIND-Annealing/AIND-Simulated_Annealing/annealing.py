import numpy.random as random  # see numpy.random module
from math import e

alpha = 0.95
temperature=1e6

def simulated_annealing(problem, schedule):
    """The simulated annealing algorithm, a version of stochastic hill climbing
    where some downhill moves are allowed. Downhill moves are accepted readily
    early in the annealing schedule and then less often as time goes on. The
    schedule input determines the value of the temperature T as a function of
    time. [Norvig, AIMA Chapter 3]
    
    Parameters
    ----------
    problem : Problem
        An optimization problem, already initialized to a random starting state.
        The Problem class interface must implement a callable method
        "successors()" which returns states in the neighborhood of the current
        state, and a callable function "get_value()" which returns a fitness
        score for the state. (See the `TravelingSalesmanProblem` class below
        for details.)

    schedule : callable
        A function mapping time to "temperature". "Time" is equivalent in this
        case to the number of loop iterations.
    
    Returns
    -------
    Problem
        An approximate solution state of the optimization problem
        
    Notes
    -----
        (1) DO NOT include the MAKE-NODE line from the AIMA pseudocode

        (2) Modify the termination condition to return when the temperature
        falls below some reasonable minimum value (e.g., 1e-10) rather than
        testing for exact equality to zero
        
    See Also
    --------
    AIMA simulated_annealing() pseudocode
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Simulated-Annealing.md
    """     
    counter = 0
    solution = problem
    sol_value = solution.get_value()
    temp = schedule(counter)
    while(True):
        temp = schedule(counter)
        if temp == 0:
            return solution
        counter = counter + 1
        successors = solution.successors2()
       
        new_solution = random.choice(successors)    
        new_sol_value = new_solution.get_value()
        if new_sol_value >= sol_value or random.random() <= e ** ((new_sol_value-sol_value)/temp):
            solution = new_solution
            sol_value = new_sol_value
    return solution

def schedule(time):
    return (alpha ** time ) * temperature 