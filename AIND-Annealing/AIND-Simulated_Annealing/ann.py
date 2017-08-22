# coding: utf-8

# # I. Introduction
# 
# ![Simulated Annealing](SA_animation.gif)
# As illustrated in the lectures, simulated annealing is a probablistic technique used for finding an approximate solution to an optimization problem.  In this exercise you will check your understanding by implementing [simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing) to solve the [Traveling Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem) (TSP) between US state capitals.  Briefly, the TSP is an optimization problem that seeks to find the shortest path passing through every city exactly once.  In our example the TSP path is defined to start and end in the same city (so the path is a closed loop).
# 
# Image Source: [Simulated Annealing - By Kingpin13 (Own work) [CC0], via Wikimedia Commons (Attribution not required)](https://commons.wikimedia.org/wiki/File:Hill_Climbing_with_Simulated_Annealing.gif)

# ## Overview
# 
# Students should read through the code, then:
# 
#   0. Implement the `simulated_annealing()` main loop function in Section II
#   0. Complete the `TravelingSalesmanProblem` class by implementing the `successors()` and `get_value()` methods in section III
#   0. Complete the `schedule()` function to define the temperature schedule in Section IV
#   0. Use the completed algorithm and problem description to experiment with simulated annealing to solve larger TSP instances on the map of US capitals

# In[1]:

import json

import numpy as np  # contains helpful math functions like numpy.exp()
import numpy.random as random  # see numpy.random module

# import random  # alternative to numpy.random module

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from TravelingSalesmanProblem import TravelingSalesmanProblem
from annealing import *

num_cities = 48

"""Read input data and define helper functions for visualization."""

# Map services and data available from U.S. Geological Survey, National Geospatial Program.
# Please go to http://www.usgs.gov/visual-id/credit_usgs.html for further information

# List of 30 US state capitals and corresponding coordinates on the map
with open('capitals.json', 'r') as capitals_file:
    capitals = json.load(capitals_file)
capitals_list = list(capitals.items())
def show_path(path, starting_city, w=12, h=8):
    """Plot a TSP path overlaid on a map of the US States & their capitals."""
    map = mpimg.imread("map.png")  # US States & Capitals map
    
    x, y = list(zip(*path))
    _, (x0, y0) = starting_city
    plt.plot(x0, y0, 'y*', markersize=15)  # y* = yellow star for starting point
    plt.plot(x + x[:1], y + y[:1])  # include the starting point at the end of path
    plt.axis("off")
    fig = plt.gcf()
    fig.set_size_inches([w, h])
    plt.show()
    plt.imshow(map)
    

## Construct an instance of the TravelingSalesmanProblem
#test_cities = [('DC', (11, 1)), ('SF', (0, 0)), ('PHX', (2, -3)), ('LA', (0, -4))]
#tsp = TravelingSalesmanProblem(test_cities)
#assert(tsp.path == test_cities)

## Test the successors() method -- no output means the test passed
#successor_paths = [x.path for x in tsp.successors()]
#assert(all(x in [[('LA', (0, -4)), ('SF', (0, 0)), ('PHX', (2, -3)), ('DC', (11, 1))],
#                 [('SF', (0, 0)), ('DC', (11, 1)), ('PHX', (2, -3)), ('LA', (0, -4))],
#                 [('DC', (11, 1)), ('PHX', (2, -3)), ('SF', (0, 0)), ('LA', (0, -4))],
#                 [('DC', (11, 1)), ('SF', (0, 0)), ('LA', (0, -4)), ('PHX', (2, -3))]]
#          for x in successor_paths))

## Test the get_value() method -- no output means the test passed
#assert(np.allclose(tsp.get_value(), -28.97, atol=1e-3))

## ## IV. Define the Temperature Schedule
## 
## The most common temperature schedule is simple exponential decay:
## $T(t) = \alpha^t T_0$
## 
## (Note that this is equivalent to the incremental form $T_{i+1} = \alpha T_i$, but implementing that form is slightly 
## more complicated because you need to preserve state between calls.)
## 
## In most cases, the valid range for temperature $T_0$ can be very high (e.g., 1e8 or higher), and the _decay parameter_ $\alpha$ 
## should be close to, but less than 1.0 (e.g., 0.95 or 0.99).  Think about the ways these parameters effect the simulated annealing function.  
## Try experimenting with both parameters to see how it changes runtime and the quality of solutions.
## 
## You can also experiment with other schedule functions -- linear, quadratic, etc.  Think about the ways that changing the form of the temperature 
## schedule changes the behavior and results of the simulated annealing function.

## In[ ]:

## These are presented as globals so that the signature of schedule()
## matches what is shown in the AIMA textbook; you could alternatively
## define them within the schedule function, use a closure to limit
## their scope, or define an object if you would prefer not to use
## global variables
#alpha = 0.95
#temperature=1e4

# ### Testing the Temperature Schedule
# The following tests should validate the temperature schedule function and perform a simple test of the simulated annealing function to solve a small TSP test case

# In[ ]:

# test the schedule() function -- no output means that the tests passed
#assert(np.allclose(alpha, 0.95, atol=1e-3))
#assert(np.allclose(schedule(0), temperature, atol=1e-3))
#assert(np.allclose(schedule(10), 5987.3694, atol=1e-3))


# In[ ]:

# Failure implies that the initial path of the test case has been changed
#assert(tsp.path == [('DC', (11, 1)), ('SF', (0, 0)), ('PHX', (2, -3)), ('LA', (0, -4))])
#result = simulated_annealing(tsp, schedule)
#print("Initial score: {}\nStarting Path: {!s}".format(tsp.get_value(), tsp.path))
#print("Final score: {}\nFinal Path: {!s}".format(result.get_value(), result.path))
#assert(tsp.path != result.path)
#assert(result.get_value() > tsp.get_value())


# ## V. Run Simulated Annealing on a Larger TSP
# Now we are ready to solve a TSP on a bigger problem instance by finding a shortest-path circuit through several of the US state capitals.
# 
# You can increase the `num_cities` parameter up to 30 to experiment with increasingly larger domains.  Try running the solver repeatedly -- how stable are the results?

# In[ ]:

# Create the problem instance and plot the initial state

capitals_tsp = TravelingSalesmanProblem(capitals_list[:num_cities])
starting_city = capitals_list[0]
print("Initial path value: {:.2f}".format(-capitals_tsp.get_value()))
minim = None
for i in range(10):
    print ('---->{0}'.format(i))
        
    #print(capitals_list[:num_cities])  # The start/end point is indicated with a yellow star
    #show_path(capitals_tsp.coords, starting_city)

    result = simulated_annealing(capitals_tsp, schedule)
    print("Final path length: {:.2f}".format(-result.get_value()))
    if minim == None or minim.get_value() < result.get_value():
        minim = result    
print("Final path length: {:.2f}".format(-minim.get_value()))
show_path(minim.coords, starting_city)

v = input("press it")

# ### Experiments (Optional)
# Here are some ideas for additional experiments with various settings and parameters once you've completed the lab.
# 
# - Change the number of cities in the final map (between 10 and 30).  How are your results affected?  Why?
# - Change the alpha and temperature parameters.  How do they affect the results?
# - Use a different schedule function (something other than exponential decay).  Is the algorithm still effective?
# - Use a different successors function; e.g., generate successors of a state by swapping _any_ pair of cities in the path, rather than only adjacent cities.  Try defining your own successor function.  What effect does the change have?
# - Use a different distance metric for get_value (e.g., we used the L2-norm (Euclidean distance), try the L1-norm (manhattan distance) or L$\infty$-norm (uniform norm)
# 
# Share and discuss your results with others in the forums!
