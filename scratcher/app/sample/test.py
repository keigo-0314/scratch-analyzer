import sys
import json
import os
import csv
import glob
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # type: ignore

sys.path.append("../../")

from api import scratch_client
from api import drscratch_analyzer
import prjman
from prjman import ProjectManager
from collections import defaultdict

project_manager = ProjectManager(421943851)
print(str(project_manager.get_all_blocks_length()))
print(str(project_manager.get_blocks_length()))