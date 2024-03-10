import json
import os
from transformers import pipeline

def summarize_comments(filepath_read):
    with open(filepath_read) as f:
        json_load = json.load(f)
    status_list = json_load["status_list"]
    review_list = add_summarize(json_load)
    return {"status_list": status_list, "review_list": review_list}

summarizer = pipeline("summarization")
def add_summarize(json_load):
    for review in json_load["review_list"]:
        review_comments = review["comment"]
        max_length = dynamic_max_length(review_comments)
        review_summarize = summarizer(review_comments, max_length, clean_up_tokenization_spaces=True)
        # 要約テキストを抽出して代入
        review['summarize'] = review_summarize[0]['summary_text']
    return json_load['review_list']
    
def dynamic_max_length(text, min_length=50, max_length=200):
    # 入力テキストの長さに応じてmax_lengthを調整
    length = len(text.split())  # 単語数で長さを計算
    dynamic_length = max(min_length, min(int(length * 0.5), max_length))
    return dynamic_length

filepath_read = '/Users/haruto-k/research/select_list/json_file/list_1/629766_comments_merge_list.json'
summarize_list = summarize_comments(filepath_read)
file_name = os.path.splitext(os.path.basename(filepath_read))[0].replace('_comments_merge_list', '')
filepath_write = '/Users/haruto-k/desktop/629766_summarizelist.json'
with open(filepath_write, 'w') as f:
    json.dump(summarize_list, f, indent=4)