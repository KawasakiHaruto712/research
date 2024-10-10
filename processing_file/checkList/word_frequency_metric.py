import json
import pandas as pd
import nltk
import re
from collections import Counter
from nltk.corpus import stopwords
from tqdm import tqdm

# nltkの機能をダウンロード
nltk.download('punkt_tab')

# 定数の設定
bot_names_path = "../../project/botNames.json"
checklist_path = "../../select_list/checkList/AlradyStartBeforeCode/CheckListResult.csv"
check_PR_num_path = "../../select_list/labeled_PRNumber.txt"
uni_gram_path = "../../select_list/checkList/N_gram/metric/unigram.csv"
bi_gram_path = "../../select_list/checkList/N_gram/metric/bigram.csv"
tri_gram_path = "../../select_list/checkList/N_gram/metric/trigram.csv"

# チェックリストの読み込み
def read_checklist():

    # ラベル付したPRまでのチェックリストを抽出
    checklist = pd.read_csv(checklist_path, header=0)
    with open(check_PR_num_path) as PR_num_txt:
        textline = PR_num_txt.readlines()
    check_PR_num = float(textline[0])
    checklist = checklist[checklist["PRNumber"] <= check_PR_num]

    # botのコメントの削除
    # with open(bot_names_path, 'r') as bot_names_json:
    #     bot_names = json.load(bot_names_json)
    # bot_names_list = [bot["name"] for bot in bot_names]
    # checklist = checklist[~checklist["author"].isin(bot_names_list)]

    return checklist

# レビューコメントをカテゴリー毎に分類
def categorize_com(checklist):

    # コメントのカテゴリー毎のラベルを格納する変数の初期化
    name_cate = ["機能改善", "リファクタリング/コード整形", "コード外の修正", "バグ", "typo"]

    # レビューコメントをカテゴリー毎に分類
    improve_com = [row["comment"] for _, row in checklist.iterrows() if row["レビューアによるコード追加要求"] == 1 or row["レビューアによるコード改善要求"] == 1] # 機能改善
    refact_com = [row["comment"] for _, row in checklist.iterrows() if row["リファクタリング"] == 1 or row["コード整形，コメントアウト修正"] == 1] # リファクタリング/コード整形
    outside_code_com = [row["comment"] for _, row in checklist.iterrows() if row["コード外の修正，改善"] == 1] # コード外の修正
    bug_com = [row["comment"] for _, row in checklist.iterrows() if row["バグ修正要求"] == 1] # バグ修正
    typo_com = [row["comment"] for _, row in checklist.iterrows() if row["typo"] == 1] # typo
    com_cate = [improve_com, refact_com, outside_code_com, bug_com, typo_com]

    return name_cate, com_cate

# 単語の出現回数の算出
def count_word(name_cate, com_cate):

    # 結果を格納するための辞書を初期化
    uni_count = {cate: [] for cate in name_cate}
    bi_count = {cate: [] for cate in name_cate}
    tri_count = {cate: [] for cate in name_cate}

    # コメントのラベルの種類毎にループ(種類毎の単語の出現回数を算出)
    for com_cate_num, comments in enumerate(com_cate):

        # レマタイザーのインスタンス化
        lemma = nltk.WordNetLemmatizer()

        # コメントの前処理
        # format_com = [com for com in comments if not re.search(r"^Uploaded\spatch\sset\s[0-9]+\.", com)] # アップロードメッセージは処理しない
        format_com = [re.sub(r"^Patch\sSet\s[0-9]+:*", "", com) for com in comments] # パッチセット番号の情報を削除
        format_com = [re.sub(r"[^a-zA-Z0-9\-+]", " ", com) for com in format_com] # 記号を削除する
        format_com = [com.lower() for com in format_com] # 全て小文字にする
        format_com = [nltk.word_tokenize(com) for com in format_com] # トークナイズする
        format_com = [[word for word in com if not word in set(stopwords.words("english"))] for com in format_com] # ストップワードを削除
        format_com = [[lemma.lemmatize(word) for word in com] for com in format_com] # レマタイズの実行

        high_num_n_gram = n_gram_com(format_com) # コメントにおいてN-gramを用いて単語の出現回数を算出

        # N-gramの結果を格納
        uni_count[name_cate[com_cate_num]] = high_num_n_gram[0]
        bi_count[name_cate[com_cate_num]] = high_num_n_gram[1]
        tri_count[name_cate[com_cate_num]] = high_num_n_gram[2]
    
    # N-gramの結果をデータフレーム型に変換
    uni_count_df = pd.DataFrame(uni_count)
    bi_count_df = pd.DataFrame(bi_count)
    tri_count_df = pd.DataFrame(tri_count)

    return uni_count_df, bi_count_df, tri_count_df

# コメントにおいてN-gramを用いて単語の出現回数を算出
def n_gram_com(format_com):

    # N-gramの結果の上位件数を格納する変数の初期化
    high_num_n_gram = []

    # コメントにおいてN-gramの結果を算出
    for n_gram_num in range(1, 4):

        # N-gramの結果を格納する変数の初期化
        n_gram = []

        # コメント毎にN-gramを用いる
        for com in format_com:
            n_gram.extend(tuple(com[i:i+n_gram_num]) for i in range(len(com)-n_gram_num+1))
        
        # 頻出したN-gramの結果の内上位20件を抽出
        com_count = Counter(n_gram)
        high_num_n_gram.append(com_count.most_common(20))

    return high_num_n_gram

# メイン処理
def main():
    
    # チェックリストの読み込み
    checklist = read_checklist()

    # レビューコメントをカテゴリー毎に分類
    name_cate, com_cate = categorize_com(checklist)

    # 単語の出現回数の算出
    uni_count_df, bi_count_df, tri_count_df = count_word(name_cate, com_cate)

    # 単語の出現回数の出力
    uni_count_df.to_csv(uni_gram_path, index=False, encoding="utf_8_sig")
    bi_count_df.to_csv(bi_gram_path, index=False, encoding="utf_8_sig")
    tri_count_df.to_csv(tri_gram_path, index=False, encoding="utf_8_sig")

if __name__ == '__main__':
    main()