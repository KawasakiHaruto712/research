from glob import glob
from tqdm import tqdm
import json
import os

def make_tasklist(filepath):
    with open(filepath) as f:
        json_load = json.load(f)
    status_list = json_load["status_list"]
    review_list = extract_task(json_load)
    return {"status_list": status_list, "review_list": review_list}

def extract_task(json_load):
    reviewer_name = []
    extract_comments = []
    for review in json_load["review_list"]:
        comment = review["comment"].casefold()
        if "lgtm" in comment or "looks good to me" in comment:
            if review["reviewer"] not in reviewer_name:
                reviewer_name.append(review["reviewer"])
    for reviewer in reviewer_name:
        for review in json_load["review_list"]:
            if reviewer == review["reviewer"]:
                extract_comments.append(review)
    return extract_comments

file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    filepath_read = '/Users/haruto-k/research/select_list/json_file/' + file_cate[i] +'/*.json'
    filepath_list = glob(filepath_read)
    for filepath in filepath_list:
        tasklist = make_tasklist(filepath)
        file_name = os.path.splitext(os.path.basename(filepath))[0].replace('_comments_merge_list', '')
        filepath_write = '/Users/haruto-k/research/select_list/task/json_file/' + file_cate[i] + '/' + file_name + '_tasklist.json'
        with open(filepath_write, 'w') as f:
            json.dump(tasklist, f, indent=4)