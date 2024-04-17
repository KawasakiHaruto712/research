from glob import glob
from pathlib import Path
import json

# 全体の紐付け割合の計算
def ratio_calculate(filepath_list):
    for filepath in filepath_list:
        with open(filepath) as f:
            associate_file = json.load(f)
        link_ratio = associate_file['status_list']['link_ratio']
        number_request = associate_file['status_list']['number_request']
        if link_ratio > 0.4 and number_request >= 10 and number_request < 20:
            p_file = Path(filepath)
            print('[' + p_file.stem + ', ' + p_file.parent.name + ']')
    return total_ratio

filepath_read = '/Users/haruto-k/research/select_list/adjust_comments/*/*.json'
filepath_list = glob(filepath_read)
total_ratio = ratio_calculate(filepath_list)
print(total_ratio)