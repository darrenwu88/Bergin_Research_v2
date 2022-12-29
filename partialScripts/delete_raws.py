import os
import glob 

PATH = r"/Users/darrenwu/Bergin_Research"
joined_files = os.path.join(PATH, "8143*.csv")
joined_list = glob.glob(joined_files)

for file in joined_list:
    os.remove(file)