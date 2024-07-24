from Definition import RegardlessReviewer, SameReviewer
from glob import glob
from pathlib import Path
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import json
import pandas as pd
import torch

# 定数の定義
AchieveCommentsFilePath = '/Users/haruto-k/research/project/AchieveComments.json'
FormatPRFilePath = '/Users/haruto-k/research/select_list/removal_bot/*/*.json'
PredictRequestModelPath = '/Users/haruto-k/research/BERT/hoge/hoge'

# 修正確認のコメントを見つける関数
def FindAchieve(FormatPRFile):

    # 修正確認コメントファイルの読み込み
    with open(AchieveCommentsFilePath, 'r') as AchieveFile:
        AchieveCommentsFile = json.load(AchieveFile)

    # 修正確認のコメントを保存するリストの初期化
    AchieveCommentsData = []

    # レビューコメント毎に紐づくか確認
    for CommentData in FormatPRFile['messages']:

        # PR実装者によるコメントでないかの確認
        if CommentData.get('author', {}).get('name', '') == FormatPRFile['owner']['name']:

            # PR実装者のコメントは対象にしない
            break

        # 修正確認コメントがコメント内に含まれているか確認
        if not any(str(CommentData['message']).lower in str(AchieveComment).lower() for AchieveComment in AchieveCommentsFile['AchieveComments']):
        
            # 修正確認コメントが含まれていないコメントは対象にしない
            break
        
        # 修正確認コメントがコメント内に含まれている
        else:

            # 修正要求と予測されたコメントの情報を保存
            AchieveCommentsData.append({
                'Date': CommentData['date'],
                'AccountID': CommentData.get('author', {}).get('_account_id', ''),
                'CommentID': CommentData.get('author', {}).get('id', ''),
                'Revision': CommentData['_revision_number'],
                'Author': CommentData.get('author', {}).get('name', ''),
                'Comment': CommentData['message']
            })

    # 修正確認コメント群のリストを返す
    return AchieveCommentsData

# 修正要求の予測を行う関数
def FindRequest(FormatPRFile):

    # BERTで作成したモデルのロード
    tokenizer = AutoTokenizer.from_pretrained(PredictRequestModelPath)
    PredictRequestModel = AutoModelForSequenceClassification.from_pretrained(PredictRequestModelPath)

    # 修正要求の予測結果をコメントを保存するリストの初期化
    RequestsCommentsData = []

    # レビューコメント毎に修正要求か否かを予測
    for CommentData in FormatPRFile['messages']:
        
        # PR実装者によるコメントでないかの確認
        if CommentData.get('author', {}).get('name', '') == FormatPRFile['owner']['name']:

            # PR実装者のコメントは対象にしない
            break

        # PR実装者以外のコメント
        else:

            # コメントをトークナイズ
            TokenizedComment = tokenizer(CommentData['message'], return_tensors="pt", truncation=True, max_length=512)

            # 推論の実行
            with torch.no_grad():
                ModelOutPuts = PredictRequestModel(TokenizedComment)
            
            # 確率を計算
            RequestProb = torch.nn.functional.softmax(ModelOutPuts.logits, dim=-1)

            # 予測結果を取得(0: 修正要求でない， 1: 修正要求)
            RequestPredictClass = torch.argmax(RequestProb).item()

            # 修正要求か否かを判定
            if RequestPredictClass == 0:

                # 修正要求でないときは対象にしない
                break
            
            # 修正要求のコメント
            else:

                # 修正要求と予測されたコメントの情報を保存
                RequestsCommentsData.append({
                    'Date': CommentData['date'],
                    'AccountID': CommentData.get('author', {}).get('_account_id', ''),
                    'CommentID': CommentData.get('author', {}).get('id', ''),
                    'Revision': CommentData['_revision_number'],
                    'Author': CommentData.get('author', {}).get('name', ''),
                    'Comment': CommentData['message']
                })

    # 修正要求と予測されたコメント群のリストを返す
    return RequestsCommentsData

# 修正確認コメントを定義に基づき紐づけるための関数
def DefinitionBasedAssociate(RequestsCommentData, AchieveCommentData):

    # 修正要求コメントと修正要求コメントが紐づいたかを表す変数の初期化
    AssociateRequest_df = RequestsCommentData

    # 修正要求の数だけ紐づくか確認
    for index in AssociateRequest_df:
        
        # 修正要求と紐づいているかを保存
        AssociateRequest_df[index].append({
            '同一検証者かつリビジョン更新後にコメント': SameReviewer.Associate(AssociateRequest_df[index], AchieveCommentData),
            '検証者は問わずリビジョン更新後にコメント': RegardlessReviewer.Associate(AssociateRequest_df[index], AchieveCommentData)
        })
    
    # 修正要求コメントと修正要求コメントが紐づいたかを表す変数を返す
    return AssociateRequest_df
        

# 修正要求と修正確認を紐づける関数
def RequestAndAchieveAssociate(FormatPRFilePath):

    # FormatFileの読み込み
    with open(FormatPRFilePath, 'r') as FormatFile:
        FormatPRFile = json.load(FormatFile)

    # 修正要求の予測を行う関数の呼び出し
    RequestsCommentsData = FindRequest(FormatPRFile)

    # 修正確認のコメントを見つける関数の呼び出し
    AchieveCommentsData = FindAchieve(FormatPRFile)

    # 修正要求と修正確認コメントを紐づける関数の呼び出し
    AssociateRequest_df = DefinitionBasedAssociate(RequestsCommentsData, AchieveCommentsData)

    # 修正要求コメントの情報と紐づいたかどうかを表す情報を表す変数を返す
    return AssociateRequest_df

# メイン処理
def main():

    # 研究で対象としている全PRを抽出する
    FormatPRFilePathList = glob(FormatPRFilePath)

    # 一つずつPRを処理する
    for FormatPRFilePath in tqdm(FormatPRFilePathList):

        # 修正要求を紐づけるための関数の呼び出し
        AssociateRequest_df = RequestAndAchieveAssociate(FormatPRFilePath)

        # 出力するフォルダとファイル名の読み込み
        AssociateFolderName = Path(FormatPRFilePath).parent.name
        AssociateFileName = Path(FormatPRFilePath).stem

        # 出力するファイルパスの作成
        AssociateResultPath = '/Users/haruto-k/research/select_list/RequestAssociate' + AssociateFolderName + '/' + AssociateFileName + '/.json'

        # 紐づけた結果の出力
        AssociateRequest_df.to_csv(AssociateResultPath, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    main()