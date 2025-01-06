import json
import pandas as pd
import nltk
import re
import yaml
from nltk.corpus import stopwords
from tqdm import tqdm
from tqdm.contrib import tenumerate

# nltkの機能をダウンロード
nltk.download('punkt_tab')

def read_checklist():

    # ラベル付したPRまでのチェックリストを抽出
    checklist = pd.read_csv("../../select_list/checkList/alradyStart/checklist_result.csv", header=0)
    with open("../../select_list/labeled_PRNumber.txt") as PR_num_txt:
        textline = PR_num_txt.readlines()
    classify_PR_num = float(textline[0])
    checklist = checklist[checklist["PRNumber"] <= classify_PR_num]

    # botのコメントを削除するか選択
    bot_delete = input("botのコメントを削除する:y, 削除しない:n\n削除しますか？:")
    if bot_delete == "y":
        with open("../../project/botNames.json", 'r') as bot_names_json:
            bot_names = json.load(bot_names_json)
        bot_names_list = [bot["name"] for bot in bot_names]
        checklist = checklist[~checklist["author"].isin(bot_names_list)]

    # ラベルのコメントを削除するか選択
    label_delete = input("レビューラベル(定型文)は削除する:y, 削除しない:n\削除しますか？:")
    if label_delete == "y":
        with open("../../project/label_comments.yml") as label_yml:
            label_comments = yaml.safe_load(label_yml)
    # ラベルを削除(ラベルだけのコメントは削除)
    for label_com in label_comments:
        checklist["comment"] = checklist["comment"].str.replace(str(label_com), "", regex=True)
    checklist = checklist[~checklist["comment"].str.match(r'^\s*$')]

    return checklist

def write_ngram(checklist):
    checklist = checklist.rename(columns={"修正要求": "human", "予測": "BERT"})
    ngram_type_list = ["unigram", "bigram", "trigram"]
    classify_type_list = ["human", "BERT"]
    request_type_list = ["non_request", "request"]

    for ngram_i, ngram_type in tqdm(enumerate(ngram_type_list), leave=False, desc="N-gram", total=len(ngram_type_list)):
        ngram_results = {}  # 結果を保存する辞書
        
        for classify_type in tqdm(classify_type_list, leave=False, desc="human or BERT"):
            for request_i, request_type in enumerate(request_type_list):
                column_name = f"{classify_type}_{request_type}"
                
                # コメント毎にN-gramの保存
                comments_ngram, ngram_variations = ngram_division_of_checklist_comments(
                    checklist, (ngram_i+1), classify_type, request_i)
                
                # N-gramの頻出度合いを算出
                ngram_sum = ngram_frequecy_count(comments_ngram, ngram_variations)
                
                # 結果をペアにして保存
                results = list(zip(ngram_variations, ngram_sum))
                # 頻度でソート
                results.sort(key=lambda x: x[1], reverse=True)
                # 辞書に保存
                ngram_results[column_name] = results
        
        # データフレームに変換
        max_rows = max(len(v) for v in ngram_results.values())
        df_dict = {}
        for column, values in ngram_results.items():
            words, counts = zip(*values) if values else ([], [])
            # カラムに単語と頻度を別々に保存
            df_dict[f"{column}_word"] = list(words) + [''] * (max_rows - len(words))
            df_dict[f"{column}_count"] = list(counts) + [0] * (max_rows - len(counts))
        
        ngram_df = pd.DataFrame(df_dict)
        ngram_df.to_csv(f"../../select_list/checkList/N_gram/per_comment/{ngram_type}.csv",
                        index=False,
                        encoding="utf_8_sig")
        
def ngram_division_of_checklist_comments(checklist, n, classify_str, label_int):

    comments_ngram = []
    for _, checklist_row in checklist.iterrows():
        if checklist_row[classify_str] == label_int:
            format_comment = format_document(checklist_row["comment"])
            ngram_comment = ngram_document(n, format_comment)
            comments_ngram.append(ngram_comment)
    ngram_variations = list(set(sum(comments_ngram, [])))

    return comments_ngram, ngram_variations

def ngram_frequecy_count(comments_ngram, ngram_variations):

    ngram_sum = []
    for variations in ngram_variations:
        count = 0
        for comments in comments_ngram:
            if variations in comments:
                count += 1
        ngram_sum.append(count)
    
    return ngram_sum

def format_document(document):
    
    # コメントの前処理(不要語の削除，単語毎に区切る)
    lemma = nltk.WordNetLemmatizer()                                                                        # レマタイザーのインスタンス化
    format_document = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+|[^\s<>"]+\.[a-zA-Z]{2,}', " ", document)   # URLを削除
    format_document = re.sub(r"[^a-zA-Z]+", " ", format_document)                                           # 記号を削除
    format_document = format_document.lower()                                                               # 全て小文字
    format_document = re.sub(r"nova|neutron|cinder|horizon|keystone|swift|glance", " ", format_document)    # プロジェクト名を削除
    format_document = re.sub(r"openstack|ci", " ", format_document)                                         # その他不要コメントを削除
    format_document = nltk.word_tokenize(format_document)                                                   # トークナイズ
    format_document = [word for word in format_document if not word in set(stopwords.words("english"))]     # ストップワードを削除
    format_document = [lemma.lemmatize(word) for word in format_document]                                   # レマタイズの実行
    format_document = " ".join(format_document)                                                             # スペースで区切って配列を文字列に変換

    return format_document

def ngram_document(n, document):

    split_document = document.split()
    counts_of_words = len(split_document)

    ngram_document = []
    for words_i in range(counts_of_words - n + 1):
        ngram_words= " ".join(split_document[words_i: words_i + n])
        ngram_document.append(ngram_words)

    return ngram_document

def main():
    checklist = read_checklist()
    write_ngram(checklist)

if __name__ == "__main__":
    main()