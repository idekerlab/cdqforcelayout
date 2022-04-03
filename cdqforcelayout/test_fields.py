import os
import sys
# import ndex2
# import json
from numpy import int32, int16
import seaborn as sns
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
this_dir = os.path.abspath('./')
sys.path.insert(0, this_dir)
this_parent_dir = os.path.abspath('../')
sys.path.insert(0, this_parent_dir)

from cdqforcelayout import qfields

right_sb_field, right_tb_field = qfields.bias_fields((100,100), dtype=int16, direction="right", bias=10)

plt.plot(right_tb_field[0])
plt.show()

sns.heatmap(right_tb_field)
plt.show()