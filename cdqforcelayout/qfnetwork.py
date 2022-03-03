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
import logging


logger = logging.getLogger(__name__)


class QFNetwork:
 
    def __init__(self, edge_array, name="unnamed network") -> None:
        self.node_dict = {}
        for edge in edge_array:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(str(edge[0]) + ' ' + str(edge[1]))
            if edge[0] not in self.node_dict:
                self.node_dict[edge[0]] = {"adj":set()}
            self.node_dict[edge[0]]["adj"].add(edge[1])
            self.node_dict[edge[0]]["degree"] = len(self.node_dict[edge[0]]["adj"])
            if edge[1] not in self.node_dict:
                self.node_dict[edge[1]] = {"adj":set()}
            self.node_dict[edge[1]]["adj"].add(edge[0])
            self.node_dict[edge[1]]["degree"] = len(self.node_dict[edge[1]]["adj"])
    
    @classmethod
    def from_nicecx(cls, nicecx):
        edge_array = np.zeros((len(nicecx.get_edges()), 2), dtype=int)
        logger.debug("edge array: " + str(edge_array.shape))
        i = 0
        for edge_id, edge in nicecx.get_edges():
            edge_array[i, 0] = edge["s"]
            edge_array[i, 1] = edge["t"]
            i += 1
        return cls(edge_array, name=nicecx.get_name())

    def get_sorted_nodes(self):
        # get the nodes as a list, sorted by degree, highest degree first
        return sorted(self.node_dict.values(), key=itemgetter('degree'), reverse=True)

    def get_nodecount(self):
        return len(self.node_dict.values())

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
        for node_id, node in self.node_dict.items():
            node["x"] = center
            node["y"] = center

    def get_cx_layout(self, node_dimension=40):
        cx_layout = []
        for node_id, node in self.node_dict.items():
            logger.debug('nodeid: ' + str(node_id) + ' node: ' + str(node))
            cx_node = {"node": int(node_id),
                       "x": int(node["x"] * node_dimension),
                       "y": int(node["y"] * node_dimension)}
            cx_layout.append(cx_node)
        return cx_layout
