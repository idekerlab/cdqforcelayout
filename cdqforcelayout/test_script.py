import os
import sys
import ndex2
import json
import qflayout

NDEXUSER = "dexterpratt"
NDEXPASSWORD = "cytoscaperules"
SERVER = "http://www.ndexbio.org"

def upload_network(cx_network):
    url = cx_network.upload_to(SERVER, NDEXUSER, NDEXPASSWORD)
    url = url.split('/')[-1]
    print("Network's URL (click to view!): " + SERVER + "/viewer/networks/" + url)

def load_test_cx(filename):
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "tests", "data", filename)
    return ndex2.create_nice_cx_from_file(path)

test_network_files = ["test_nectin_adhesion.cx"]
test_networks = []
for filename in test_network_files:
    test_networks.append(load_test_cx(filename))

qfl = qflayout.QFLayout.from_nicecx(test_networks[0],initialize_coordinates="center", sparsity=30, r_radius=10, 
                        a_radius=20, r_scale=7, a_scale=5, center_attractor_scale=0.02)
new_layout = qfl.do_layout(rounds=10)
test_networks[0].set_opaque_aspect(ndex2.constants.CARTESIAN_LAYOUT_ASPECT, new_layout)
upload_network(test_networks[0])