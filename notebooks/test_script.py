import os
import sys
import ndex2
import json
from numpy import int32, int16
import seaborn
import matplotlib.pyplot as plt

# the sys.path.insert enables invocation of this
# script from this directory and allows usage the other
# modules in this cdqforcelayout package
#
# WARNING: If cdqforcelayout is pip installed and this
#          script is called, this script may use
#          the installed modules instead of these.
#          YOU HAVE BEEN WARNED
#
sys.path.insert(0, os.path.abspath('../'))

#from cdqforcelayout import qflayout

import qflayout_nb
NDEXUSER = "dexterpratt"
NDEXPASSWORD = "cytoscaperules"
SERVER = "http://www.ndexbio.org"

def upload_network(cx_network):
    url = cx_network.upload_to(SERVER, NDEXUSER, NDEXPASSWORD)
    url = url.split('/')[-1]
    print("Network's URL (click to view!): " + SERVER + "/viewer/networks/" + url)

def load_test_cx(filename):
    parent_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    path = os.path.join(parent_dir, "tests", "data", filename)
    return ndex2.create_nice_cx_from_file(path)

parent_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
ncipid_path = os.path.join(parent_dir, "tests", "ncipid")
ncipid_files = [f for f in os.listdir(ncipid_path) if os.path.isfile(os.path.join(ncipid_path, f))]
ncipid_networks = []
for filename in ncipid_files:
    filepath = os.path.join(ncipid_path, filename)
    ncipid_networks.append(ndex2.create_nice_cx_from_file(filepath))

print(ncipid_files)#
#upload_network(ncipid_networks[0])

def layout(network):
    qfl = qflayout_nb.QFLayout.from_nicecx(network,initialize_coordinates="spiral", sparsity=30, r_radius=10, 
                        a_radius=40, r_scale=7, a_scale=5, center_attractor_scale=0.02, dtype=int16)
    # seaborn.heatmap(qfl.gameboard)
    # plt.show()
    new_layout = qfl.do_layout(rounds=3)
    network.set_opaque_aspect(ndex2.constants.CARTESIAN_LAYOUT_ASPECT, new_layout)

layout(ncipid_networks[2])
upload_network(ncipid_networks[2])