#
# The layout object defines the datastructures
# and parameters for the algorithm.
#
import numpy as np
from cdqforcelayout import qfnetwork
#import qfnetwork
from math import sqrt
from cdqforcelayout.qfields import repulsion_field, attraction_field, add_field, subtract_field, bias_fields
#from qfields import repulsion_field, attraction_field, add_field, subtract_field

import logging


logger = logging.getLogger(__name__)


class QFLayout:
    def __init__(self, qfnetwork, sparsity=30, r_radius=10, 
                        a_radius=10, r_scale=10, a_scale=5, center_attractor_scale=0.01,
                        initialize_coordinates="spiral", dtype=np.int16, directed_flow="not_enabled", 
                        directed_flow_bias=0.01):
        self.integer_type = dtype
        self.network = qfnetwork
        
        # this is now g_field, the variable names need to be updatated
        self.gameboard, center = self._make_gameboard(sparsity, center_attractor_scale)
        self.gameboard_mask = np.zeros(self.gameboard.shape, dtype=self.integer_type)

        if initialize_coordinates == "center":
            logger.debug("init at center")
            self.network.place_nodes_at_center(center)
        elif initialize_coordinates == "random":
            logger.debug("init random")
            self.network.place_nodes_randomly(self.gameboard.shape[0])
        elif initialize_coordinates == "spiral":
            logger.debug("init spiral")
            self.network.place_nodes_in_a_spiral(center)

        self.r_field = repulsion_field(r_radius, r_scale, self.integer_type, center_spike=True)
        
        # Three attraction fields are created in order to
        # scale attraction depending on node degree
        #
        self.a_field = attraction_field(a_radius, a_scale, self.integer_type)
        self.a_field_med = attraction_field(a_radius, a_scale*5, self.integer_type)
        self.a_field_high = attraction_field(a_radius, a_scale*10, self.integer_type)

        # If we are in directed flow mode, create two gameboard-size fields, the source bias 
        # and the target bias. These will be added to the gameboard to bias the 
        # placement of nodes with only outgoing edges to one side and nodes with only incoming
        # edges to the opposite side.
        #
        if directed_flow in ("top", "bottom", "left", "right"):
            self.directed_flow_mode = True
            self.sb_field, self.tb_field = bias_fields(self.gameboard.shape, self.integer_type, directed_flow, directed_flow_bias)
        else:
            self.directed_flow_mode = False

        # make a scratchpad board where we add all the attraction fields
        # and the use it to update the gameboard
        self.s_field = np.zeros(self.gameboard.shape, self.integer_type)

        # initialize the repulsion field and the mask
        for node in self.network.get_sorted_nodes():  
            add_field(self.r_field, self.gameboard, node["x"], node["y"])
            self.gameboard_mask[node["x"], node["y"]] = 1

    @classmethod
    def from_nicecx(cls, nicecx, **kwargs):
        return cls(qfnetwork.QFNetwork.from_nicecx(nicecx), **kwargs)

    #
    # return the g_field for the QFLayout
    #
    # This still uses the old name "gameboard" at the moment
    # 
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
        return board, center

    # update the position of one node
    def layout_one_node(self, node):
        # remove the node from the gameboard by subtracting it at its current location
        # also set that location of the gameboard_mask to zero
        subtract_field(self.r_field, self.gameboard, node['x'], node['y'])
        #self.gameboard[node['x'], node['y']] = 32768 # 
        #self.gameboard_mask[node['x'], node["y"]] = 0

        # clear the scratchpad
        self.s_field[...]=0
        # add the attractions to the scratchpad
        degree = node["degree"]   
        for adj_node_id in node['adj']:
            # add an a_field to the scratchpad field
            # at the position of the adjacent node
            # lower degree nodes have higher attractions
            adj_node = self.network.node_dict[adj_node_id]
            if degree == 1:
                add_field(self.a_field_high, self.s_field, adj_node["x"], adj_node["y"])
            elif degree < 5:
                add_field(self.a_field_med, self.s_field, adj_node["x"], adj_node["y"])
            else:
                add_field(self.a_field, self.s_field, adj_node["x"], adj_node["y"])

        # check if we are in directed_flow mode
        if self.directed_flow_mode is True and degree != 0:
            # if the out_degree of the node is zero, add the tb_field
            # (the node is only a target, bias its placement to the target side)
            if node["out_degree"] == 0:
                self.s_field += self.tb_field
            # if the in_degree of the node is zero and there is a sb_field
            # (the node is only a source, bias its placement to the source side)
            if node["in_degree"] == 0:
                self.s_field += self.sb_field

        # add s_field to the gameboard
        self.gameboard += self.s_field     
        
        # place the node at a mimima in the gameboard
        # argmin returns the index of the first location containing
        # the minimum value in a flattened version of the array
        # unravel_index turns the index back into the coordinates
        #
        destination = np.unravel_index(np.argmin(self.gameboard, axis=None), self.s_field.shape)
        node["x"] = destination[0]
        node["y"] = destination[1]            

        # add the node's repulsion field at the destination 
        add_field(self.r_field, self.gameboard, destination[0], destination[1])

        # subtract the s_field, leaving the gameboard with only the repulsion fields
        self.gameboard -= self.s_field


    def do_layout(self, rounds=1, node_size=40):
        node_list = self.network.get_sorted_nodes()
              
        # perform the rounds of layout
        # start = timer()
        for n in range(0, rounds):
            logger.debug('round ' + str(n))
            for node in node_list:
                #degree = node.get("degree")
                # only layout the degree 1 nodes on the last
                # round
                #if degree > 1 or n >= (rounds-1):
                self.layout_one_node(node)

        # end = timer()
        # print("layout time = ", end - start)
        return self.network.get_cx_layout(node_size=node_size)