from time import time
from math import pi, sin, asin, cos
from random import random

def decide(chance):
    return random() < chance

def scale_to(val, curr_min, curr_max, new_min, new_max):
    old_range = curr_max - curr_min
    new_range = new_max - new_min
    return (((val - curr_min) * new_range) / old_range) + new_min

def sin_osc(freq, min_val, max_val, time_offset=0):
    t = time() + time_offset
    t = t * pi * 2 * freq
    val = sin(t)
    return scale_to(val, -1, 1, min_val, max_val)

def tri_osc(freq, min_val, max_val, time_offset=0):
    t = time() + time_offset
    t = t * pi * 2 * freq
    val = asin(cos(t))
    return scale_to(val, -pi/2, pi/2, min_val, max_val)