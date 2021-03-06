import numpy as np
from math import sqrt
import logging


logger = logging.getLogger(__name__)


# Adding fields:
# The two fields are combined at an x-y offset, destructively modifying the target field
# It is neccessary to crop the added field to fit within the target field
def add_field(source_field, target_field, x, y, remove=False, show_node_dict=False):
    if show_node_dict: print("node_dict", x,y)
    target_x_max = target_field.shape[0] - 1
    target_y_max = target_field.shape[1] - 1
    source_x_max = source_field.shape[0] - 1
    source_y_max = source_field.shape[1] - 1
    #
    #   0.0 1.0 2.0
    #   0.1 1.1 2.1
    #   0.2 1.2 2.2
    #
    x_offset = int(source_field.shape[0]/2)
    y_offset = int(source_field.shape[1]/2)
    logger.debug("gb shape " + str(target_field.shape))
    logger.debug("rf offset " + str(x_offset) + ' ' + str(y_offset))
    target_top_x = x - x_offset
    target_top_y = y - y_offset
    target_bottom_x = x + x_offset
    target_bottom_y = y + y_offset
    logger.debug('gb target ' + str(target_top_x) +
                 ' ' + str(target_top_y) + ' ' +
                 str(target_bottom_x) + ' ' +
                 str(target_bottom_y))
    source_top_x = 0
    source_top_y = 0
    source_bottom_x = source_x_max
    source_bottom_y = source_y_max
    #print("rf source", source_top_x,source_top_y,source_bottom_x,source_bottom_y)
    # trim if source_field goes off board negative
    if target_top_x < 0:
        logger.debug("negative x")
        source_top_x = -target_top_x
        target_top_x = 0        
    if target_top_y < 0:
        logger.debug("negative y")
        source_top_y = -target_top_y
        target_top_y = 0
    # trim if source_field goes off board positive
    if target_bottom_x > target_x_max:
        dx = target_bottom_x - target_x_max
        logger.debug("positive x", dx)
        target_bottom_x = target_x_max
        source_bottom_x = source_x_max - dx
    if target_bottom_y > target_y_max:
        dy = target_bottom_y - target_y_max
        logger.debug("positive y " + str(dy))
        target_bottom_y = target_y_max
        source_bottom_y = source_y_max - dy
    logger.debug("adj gb target" + ' ' + str(target_top_x) + ' ' +
                 str(target_top_y) + ' ' +
                 str(target_bottom_x) + ' ' +
                 str(target_bottom_y))
    #print("adj rf source", source_top_x,source_top_y,source_bottom_x,source_bottom_y)
    #gameboard[target_top_x, target_top_y] = 1
    #gameboard[target_bottom_x, target_bottom_y] = 1
    # add the source_field to the target_field
    #print(target_field[target_top_x:target_bottom_x+1, target_top_y:target_bottom_y+1])
    #print(source_field[source_top_x:source_bottom_x+1, source_top_y:source_bottom_y+1])
    if remove:
        target_field[target_top_x:target_bottom_x+1, target_top_y:target_bottom_y+1] -= source_field[source_top_x:source_bottom_x+1, source_top_y:source_bottom_y+1]
    else:
        target_field[target_top_x:target_bottom_x+1, target_top_y:target_bottom_y+1] += source_field[source_top_x:source_bottom_x+1, source_top_y:source_bottom_y+1]

# wrapper for readability
def subtract_field(source_field, target_field, x, y, show_node_dict=False):
    add_field(source_field, target_field, x, y, remove=True, show_node_dict=show_node_dict)


def attraction_field(radius, scale, dtype):
    dimension = (2*radius)+1
    ef = np.zeros((dimension, dimension), dtype=dtype)
    energy = int(scale * radius)
    slope = energy/radius
    for x in range(0, dimension):
        dx = abs(radius - x)
        for y in range(0, dimension):
            dy = abs(radius - y)
            distance = sqrt(dx**2 + dy**2)
            ef[x,y] = -1 * energy if distance == 0 else min( 0, int((slope * distance) - energy))
    return ef

def repulsion_field(radius, scale, dtype, center_spike=False):
    dimension = (2*radius)+1
    ef = np.zeros((dimension, dimension), dtype=dtype)
    energy = int(scale * radius)
    center_energy = 1000 if center_spike == True else energy
    for x in range(0, dimension):
        dx = abs(radius - x)
        for y in range(0, dimension):
            dy = abs(radius - y)
            distance = sqrt(dx**2 + dy**2)
            #energy = 1000 if distance == 0 else int(scale * (abs(distance - radius)**2))
            ef[x,y] = center_energy if distance == 0 else int(energy / distance**2) + int(0.1 * (energy / distance))
    return ef
