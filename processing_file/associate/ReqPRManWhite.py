import numpy as np
import pandas as pd
from glob import glob
from pathlib import Path
from scipy.stats import mannwhitneyu
from tqdm import tqdm

# 変更提案の1日あたりの存在していた数を保存していたパスを定義
AllPRPath = '/Users/haruto-k/research/project/TaskDist/PR/*.csv'

# 修正要求の1日あたりの存在していた数を保存していたディレクトリを定義
AllReqPath = '/Users/haruto-k/research/project/TaskDist/Request/'

# 有意差の結果を保存するパスの定義
MWResultPath = '/Users/haruto-k/research/select_list/ReqPRMannWhite.csv'

# プロジェクト毎の1日あたりの変更提案数と修正要求数の分布の有意差を測定する関数
def MannWhite():

    # 有意差の結果を保存する変数の初期化
    MWResult_list = []

    # プロジェクトの数だけループ
    for PRPath in tqdm(glob(AllPRPath)):

        # 修正要求の情報が記述されたパスの定義
        ReqPath = AllReqPath + Path(PRPath).stem + '.csv'

        # 変更提案と修正要求の情報が記述されたファイルの読み込み
        PRData_df = pd.read_csv(PRPath, header=0)
        ReqData_df = pd.read_csv(ReqPath, header=0)

        # マンホイットニーのU検定を実行
        stat, pvalue = mannwhitneyu(PRData_df['PRSum'], ReqData_df['RequestSum'])

        # 効果量rを算出
        E = len(PRData_df['PRSum']) * len(ReqData_df['RequestSum']) / 2
        V = np.sqrt(len(PRData_df['PRSum']) * len(ReqData_df['RequestSum']) * (len(PRData_df['PRSum']) + len(ReqData_df['RequestSum']) + 1) / 12)
        Z = (stat - E) / V
        r = Z / np.sqrt(len(PRData_df['PRSum']) + len(ReqData_df['RequestSum']))

        # 有意差の結果を変数に保存
        MWResult_list.append({
            'Project': Path(PRPath).stem,
            'statistic': stat,
            'p-value': pvalue,
            'effect_size': r
        })

    # 有意差の結果を保存する変数を返す
    return pd.DataFrame(MWResult_list)

# メイン処理
def main():

    # プロジェクト毎の1日あたりの変更提案数と修正要求数の分布の有意差を測定する関数の呼び出し
    MWResult_df = MannWhite()

    # 有意差の結果をcsvに保存
    MWResult_df.to_csv(MWResultPath, index=False, encoding='utf_8_sig')

if __name__ == '__main__':
    main()