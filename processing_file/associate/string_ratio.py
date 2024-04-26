from glob import glob
from tqdm import tqdm
import json

# 全体の紐付け割合の計算
def ratio_calculate(filepath_list):
    total_request = 0
    total_link = 0
    for filepath in tqdm(filepath_list):
        with open(filepath) as f:
            associate_file = json.load(f)
        link_ratio = associate_file['status_list']['link_ratio']
        number_request = associate_file['status_list']['number_request']
        number_link = link_ratio * number_request
        total_request += number_request
        total_link += number_link
    total_ratio = total_link / total_request
    return total_ratio

def main():
    filepath_read = '/Users/haruto-k/research/select_list/adjust_comments/json/*/*.json'
    filepath_list = glob(filepath_read)
    total_ratio = ratio_calculate(filepath_list)
    print(total_ratio)

if __name__ == "__main__":
    main()