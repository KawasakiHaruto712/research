import json
import pandas as pd
from glob import glob
from pathlib import Path
from tqdm import tqdm

# PRの情報が記述されたファイルパスの定義
AllPRDataPath = '/Users/haruto-k/research/project/formatFile/*/*.json'

# レビューコメント数を記述したファイルパスの定義
RevComSumPath = '/Users/haruto-k/research/select_list/RevComSum.csv'

# レビューコメント数を算出する関数
def ReviewCommentCalculate():

    # レビューコメント数を保存する変数の初期化
    Nova, Neutron, Cinder, Horizon, Keystone, Swift, Glance = 0, 0, 0, 0, 0, 0, 0

    # PRの数だけループ
    for PRPath in tqdm(glob(AllPRDataPath)):

        # PRの情報が記述されたファイルの読み込み
        with open(PRPath, 'r') as PR_F:
            PRData = json.load(PR_F)

        # レビューコメント数を確認し，変数に保存
        if str(Path(PRPath).parent.name) == 'list_1':
            Cinder += len(PRData['messages'])
        elif str(Path(PRPath).parent.name) == 'list_2':
            Glance += len(PRData['messages'])
        elif str(Path(PRPath).parent.name) == 'list_3':
            Horizon += len(PRData['messages'])
        elif str(Path(PRPath).parent.name) == 'list_4':
            Keystone += len(PRData['messages'])
        elif str(Path(PRPath).parent.name) == 'list_5':
            Neutron += len(PRData['messages'])
        elif str(Path(PRPath).parent.name) == 'list_6':
            Nova += len(PRData['messages'])
        else:
            Swift += len(PRData['messages'])
    
    # レビューコメント数を変数に保存
    RevComSum_list = [{
        'Nova': Nova,
        'Neutron': Neutron,
        'Cinder': Cinder,
        'Horizon': Horizon,
        'Keystone': Keystone,
        'Swift': Swift,
        'Glance': Glance
    }]

    # レビューコメント数を保存した変数を返す
    return pd.DataFrame(RevComSum_list)

# メイン処理
def main():

    # レビューコメント数を算出する関数の呼び出し
    RevComSum_df = ReviewCommentCalculate()

    # レビューコメント数を保存した結果をcsvファイルに記述
    RevComSum_df.to_csv(RevComSumPath, index=False, encoding='utf_8_sig')

if __name__ == '__main__':
    main()