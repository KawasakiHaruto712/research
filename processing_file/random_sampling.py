from glob import glob
from pathlib import Path
import pandas as pd
import random

def name_extract(filepath_list):
    name_list = []
    for filepath in filepath_list:
        p_file = Path(filepath)
        folder_name = p_file.parent.name
        file_name = p_file.stem
        name_list.append([folder_name, file_name])
    return name_list

filepath_read = '/Users/haruto-k/research/project/formatFile/*/*.json'
filepath_list = glob(filepath_read)
random.shuffle(filepath_list)
name_list = name_extract(filepath_list)
filepath_write = '/Users/haruto-k/research/select_list/visual_inspection.csv'
df = pd.DataFrame(name_list, columns = ['folder', 'file'])
df.to_csv(filepath_write, index = False)