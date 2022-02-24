#
# A network data structure for layout and clustering 
# The set of nodes is indexed by id
# Each node is a dict that has (at least) these attributes:
# adjacent nodes
# node degree
# name
# the node dict is sorted by degree
# the edges are a pandas dataframe
import numpy as np
from operator import itemgetter
from random import randint


class QFNetwork:
 
    def __init__(self, edge_array, name="unnamed network") -> None:
        node_dict = {}
        for edge in edge_array:
            # print(edge[0], " ", edge[1])
            if edge[0] not in node_dict:
                node_dict[edge[0]] = {"adj":set()}
            node_dict[edge[0]]["adj"].add(edge[1])
            node_dict[edge[0]]["degree"] = len(node_dict[edge[0]]["adj"])
            if edge[1] not in node_dict:
                node_dict[edge[1]] = {"adj":set()}
            node_dict[edge[1]]["adj"].add(edge[0])
            node_dict[edge[1]]["degree"] = len(node_dict[edge[1]]["adj"])
    
    @classmethod
    def from_nicecx(cls, nicecx):
        edge_array = np.zeros((len(nicecx.get_edges()), 2), dtype=int)
        #print("edge array: ", edge_array.shape)
        i = 0
        for edge_id, edge in nicecx.get_edges():
            edge_array[i, 0] = edge["s"]
            edge_array[i, 1] = edge["t"]
            i += 1
        return cls(edge_array, name=nicecx.get_name())

    def get_sorted_nodes(self):
        # get the nodes as a list, sorted by degree, highest degree first
        return sorted(self.node_dict.values(), key=itemgetter('degree'), reverse=True)

    def place_nodes_randomly(self, dimension):
        # randomly place the nodes in the center of the board
        temp_board = np.zeros((dimension, dimension))
        center_left = round(dimension/4)
        center_right = dimension - center_left
        for node_id, node in self.node_dict.items():
            placed = False
            while not placed:
                x = randint(center_left, center_right)
                y = randint(center_left, center_right)
                if temp_board[x, y] == 0:
                    temp_board[x, y] = 1
                    placed = True
            node["x"] = x
            node["y"] = y

    def place_nodes_at_center(self, center):
        for node_id,node in self.node_dict.items():
            node["x"] = center
            node["y"] = center

    def get_cx_layout(self, node_dimension = 40):
        cx_layout = []
        for node_id, node in self.node_dict.items():
            cx_node = {"node": node_id,
                     "x": node["x"] * node_dimension,
                     "y": node["y"] * node_dimension}
            cx_layout.append(cx_node)
        return cx_layout

        
CY_VISUAL_PROPERTIES_ASPECT = 'cyVisualProperties'
"""
Name of aspect containing visual properties where
node size can be extracted
"""

def _get_node_size_from_cyvisual_properties(net_cx=None):
    """
    Gets node size from visual properties if it exists

    :param net_cx:
    :type net_cx: :py:class:`ndex2.nice_cx_network.NiceCXNetwork`
    :raises ValueError: If **net_cx** passed in is ``None``
    :return: Size of node as retrieved from cyVisualProperties
             aspect or None, if not found
    :rtype: float
    """
    if net_cx is None:
        raise ValueError('Network passed in cannot be None')
# TODO get help on using the logger
    v_props = net_cx.get_opaque_aspect(CY_VISUAL_PROPERTIES_ASPECT)
    if v_props is None:
        logger.debug('No ' + CY_VISUAL_PROPERTIES_ASPECT +
                     ' aspect found in network')
        return None
    for entry in v_props:
        if not entry['properties_of'] == 'nodes:default':
            continue
# TODO make this return an integer
        return max(float(entry['properties']['NODE_WIDTH']),
                   float(entry['properties']['NODE_HEIGHT']),
                   float(entry['properties']['NODE_SIZE']))
    return None
