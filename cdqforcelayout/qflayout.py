#
# The layout object defines the datastructures
# and parameters for the algorithm.
#
import numpy as np
import qfnetwork
from math import sqrt
from qfields import repulsion_field, attraction_field, add_field, subtract_field
from timeit import default_timer as timer


class QFLayout:
    def __init__(self, qfnetwork, sparsity=30, r_radius=4, 
                        a_radius=10, r_scale=10, a_scale=5, center_attractor_scale=0.01,
                        initialize_coordinates=True, dtype=np.int16):
        self.integer_type = dtype
        self.network = qfnetwork
        self.gameboard = self._make_gameboard(sparsity, center_attractor_scale)
        self.r_field = repulsion_field(r_radius, r_scale, self.integer_type, center_spike=True)
        self.a_field = attraction_field(a_radius, a_scale, self.integer_type)
        self.a_field_med = attraction_field(a_radius, a_scale*5, self.integer_type)
        self.a_field_high = attraction_field(a_radius, a_scale*30, self.integer_type)
        # make a scratchpad board where we add all the attraction fields
        # and the use it to update the gameboard
        self.s_field = np.zeros(self.gameboard.shape, self.integer_type)


    @classmethod
    def from_nicecx(cls, nicecx, **kwargs):
        return cls(qfnetwork.QFNetwork.from_nicecx(nicecx), **kwargs)

    def _make_gameboard(self, sparsity, center_attractor_scale):
        radius = round(sqrt(self.network.get_nodecount() * sparsity))
        dimension = (2*radius)+1
        board = np.zeros((dimension, dimension), dtype=self.integer_type)
        # nodes are pulled towards the center of the gameboard
        # by giving the gameboard an attraction field at its center
        # the radius of the field is the distance from the center to the corners
        center = int(board.shape[0]/2)
        center_attractor_radius = int(sqrt(2 * center**2))
        add_field(attraction_field(center_attractor_radius, center_attractor_scale, self.integer_type),
              board,
              center, center)
        return board

    # update the position of one node
    def layout_one_node(self, node):
        # clear the scratchpad
        self.s_field[...]=0
        rank = len(list(node['adj']))     
        for adj_node_id in node['adj']:
            # if the adjacent node has coordinates,
            # add its attraction field to the scratchpad field
            adj_node = self.network.node_dict[adj_node_id]
            if adj_node.get("x"):
                if rank == 1:
                    add_field(self.a_field_high, self.s_field, adj_node["x"], adj_node["y"])
                elif rank < 5:
                    add_field(self.a_field_med, self.s_field, adj_node["x"], adj_node["y"])
                else:
                    add_field(self.a_field, self.s_field, adj_node["x"], adj_node["y"])
                
        # add s_field to the gameboard
        self.gameboard += self.s_field
        # if the node has coordinates
        # remove it from the gameboard by subtracting it at its current location
        if node.get("x"):
            subtract_field(self.r_field, self.gameboard, node['x'], node['y'])
        
        # select the destination
        # idea #1: choose a location with the minimum value
        # argmin returns the index of the first location containing the minimum value in a flattened 
        # version of the array
        # unravel_index turns the index back into the coordinates
        destination = np.unravel_index(np.argmin(self.gameboard, axis=None), self.s_field.shape)
        #print(node)
        #print("destination: ", destination)

        # add it at the destination
        add_field(self.r_field, self.gameboard, destination[0], destination[1])
        
        # subtract the s_field to revert the gameboard to just the repulsions
        self.gameboard -= self.s_field
        
        # update the node's coordinates
        node["x"] = destination[0]
        node["y"] = destination[1] 

    def do_layout(self, rounds=1):
        node_list = self.network.get_sorted_nodes()

        # if a node does not have coordinates, don't add its repulsion field
        for node in node_list:  
            if node.get("x"):
                add_field(self.r_field, self.gameboard, node["x"], node["y"])
                
        # perform the rounds of layout
        #start = timer()
        for n in range(0, rounds):
            # print("round ", n)
            for node in node_list:
                degree = node.get("degree")
                if n > 1 or degree > 1:
                    self.layout_one_node(node)

        #end = timer()
        #print("layout time = ", end - start)
        return self.network.get_cx_layout()