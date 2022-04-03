import os
import sys
import ndex2
#import json
from numpy import int32, int16
import seaborn as sns
import matplotlib.pyplot as plt

# This is a simple script for
# experimenting with the layout

# the sys.path.insert enables invocation of this
# script from this directory and allows usage the other
# modules in this cdqforcelayout package
#
# WARNING: If cdqforcelayout is pip installed and this
#          script is called, this script may use
#          the installed modules instead of these.
#          YOU HAVE BEEN WARNED
#
this_dir = os.path.abspath('./')
print("this_dir = " + this_dir)
this_dir_parent = os.path.abspath('../')
print("this_dir_parent = " + this_dir_parent)
sys.path.insert(0, this_dir)
sys.path.insert(0, this_dir_parent)
# for p in sys.path:
#    print(p)

from cdqforcelayout import qflayout

NDEXUSER = "dexterpratt"
NDEXPASSWORD = "cytoscaperules"
SERVER = "http://www.ndexbio.org"

def upload_network(cx_network):
    url = cx_network.upload_to(SERVER, NDEXUSER, NDEXPASSWORD)
    url = url.split('/')[-1]
    print("Network's URL (click to view!): " + SERVER + "/viewer/networks/" + url)

nci_pid_tcr_signaling_uuid = "0c2862fa-6196-11e5-8ac5-06603eb7f303"
sonic_hedgehog_uuid = "cfd3528f-a7a4-11eb-9e72-0ac135e8bacf"
nest_uuid = "60112105-f853-11e9-bb65-0ac135e8bacf"
string_hc_uuid = "275bd84e-3d18-11e8-a935-0ac135e8bacf"
cptac_genomic_instability_uuid = "d121e661-4cfc-11e9-9f06-0ac135e8bacf"
qf_test_2_uuid = "25e5dca6-8eec-11ec-b3be-0ac135e8bacf"

test_uuid = "2495c9db-aa29-11ec-b3be-0ac135e8bacf" # innate immune response signor
#test_uuid = '246aac04-6195-11e5-8ac5-06603eb7f303' # smad23 signalling nci-pid
network = ndex2.create_nice_cx_from_server(SERVER, uuid=test_uuid)
network.print_summary()

def layout(network):
    qfl = qflayout.QFLayout.from_nicecx(network, sparsity=10, r_radius=10,
                        a_radius=40, r_scale=9, a_scale=5, 
                        center_attractor_scale=5, dtype=int16, 
                        directed_flow="bottom", directed_flow_bias=500)
    # seaborn.heatmap(qfl.gameboard)
    # plt.show()
    new_layout = qfl.do_layout(rounds=40, node_size=55)
    sns.heatmap(qfl.gameboard)
    plt.show()
    #sns.heatmap(qfl.sb_field)
    #plt.show()
    #sns.heatmap(qfl.sb_field + qfl.gameboard)
    #plt.show()
    network.set_opaque_aspect(ndex2.constants.CARTESIAN_LAYOUT_ASPECT, new_layout)

layout(network)
upload_network(network)