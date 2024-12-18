import json
import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from math import log
from tqdm import tqdm

# nltkの機能をダウンロード
nltk.download('punkt_tab')

# チェックリストの読み込み
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

    return checklist

def write_ngramidf(checklist):
    checklist = checklist.rename(columns={"修正要求": "human_classify", "予測": "BERT_classify"})

    ngram_name = ["uni-gram", "bi-gram", "tri-gram"]
    classify_name = ["human_classify", "BERT_classify"]

    for ngram_i in tqdm(range(len(ngram_name)), leave=False):
        for classify_i in range(len(classify_name)):

            # ラベルの有無毎にコメントのN-gramを格納
            category_ngram_comments = []
            for label_i in range(2):
                category_ngram_comments.append([])
                category_comments = [row["comment"] 
                                     for _, row in checklist.iterrows() 
                                     if row[classify_name[classify_i]] == (label_i + 1) % 2]
                for comment in category_comments:
                    ngram_comments = format_and_ngram(comment, ngram_i + 1)
                    category_ngram_comments[-1].append(ngram_comments)
            category_ngram_comments = [sum(category_list, []) for category_list in category_ngram_comments]

            # N-gramのコメントをTF-IDFで出力
            tfidf_comments = tfidf(category_ngram_comments)
            tfidf_comments.columns = ["修正要求", "非修正要求"]
            tfidf_comments.to_csv(
                ("../../select_list/checkList/N_gram/IDF/" + ngram_name[ngram_i] + "/" + classify_name[classify_i] + ".csv"), 
                encoding="utf_8_sig")

def format_and_ngram(comment, n):
    format_comment = format_doc(comment)
    ngram_comment = ngram(format_comment, n)
    return ngram_comment

def format_doc(doc):

    # コメントの前処理(不要語の削除，単語毎に区切る)
    lemma = nltk.WordNetLemmatizer()                                                          # レマタイザーのインスタンス化
    format_doc = re.sub(r"[^a-zA-Z0-9\-+]", " ", doc)                                         # 記号を削除する
    format_doc = format_doc.lower()                                                           # 全て小文字にする
    format_doc = nltk.word_tokenize(format_doc)                                               # トークナイズする
    format_doc = [word for word in format_doc if not word in set(stopwords.words("english"))] # ストップワードを削除
    format_doc = [lemma.lemmatize(word) for word in format_doc]                               # レマタイズの実行
    format_doc = " ".join(format_doc)                                                         # スペースで区切って配列を文字列に変換

    return format_doc

def ngram(doc, n):
    split_doc = doc.split()
    counts_of_words = len(split_doc)

    n_list = []
    for words_i in range(counts_of_words - n + 1):
        n_words= " ".join(split_doc[words_i: words_i + n])
        n_list.append(n_words)

    return n_list

def tfidf(docs):

    words = list(set(w for doc in docs for w in doc))
    words.sort()

    result = []
    for i in range(len(docs)):
        result.append([])
        d = docs[i]
        for j in range(len(words)):
            t = words[j]
            result[-1].append(tf(t, d) * idf(t, docs))
    return pd.DataFrame(result, columns=words).T

def tf(t, d):
    return d.count(t) / len(d)

def idf(t, docs):
    df = 0
    N = len(docs)
    for doc in docs:
        df += t in doc
    return log(N / df) + 1

def main():
    checklist = read_checklist()
    write_ngramidf(checklist)

if __name__ == "__main__":
    main()