# NOTE: THIS FILE IS NOT BEING USED!

# # existing strategies:
# residual distance
# lost time in traffic congestion
import numpy as np

# # other ideas
# prioritization of agents based on road capacities
# concentration of vehicles on congested roads
# time spent in congestion proportional to total free flow travel time
# even agent bids on urgency to arrive at their destinations
def allocate_anticip_never():
    def allocate_anticip(car, link):
        return False

    return allocate_anticip

def allocate_anticip_alway():
    def allocate_anticip(car, link):
        return True

    return allocate_anticip

def allocate_anticip_random():
    def allocate_anticip(car, link):
        return np.random.uniform() < 0.5

    return allocate_anticip

def allocate_anticip_by_distance(perc):
    def allocate_anticip(car, link):
        return np.random.uniform() < perc

    return allocate_anticip
