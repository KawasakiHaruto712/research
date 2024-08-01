import json
import pandas as pd
import torch
from concurrent.futures import ProcessPoolExecutor
from Definition import RegardlessReviewer, SameReviewer
from glob import glob
from pathlib import Path
from tqdm import tqdm
from transformers import BertTokenizer, BertForSequenceClassification

# 修正確認コメント例とレビューコメントのデータセットのファイルパスの定義
AchieveCommentsFilePath = '/Users/haruto-k/research/project/AchieveComments.json'
FormatPRFilePath = '/Users/haruto-k/research/select_list/removal_bot/*/*.json'

# 事前に設定した定数
MODEL_NAME = 'bert-base-uncased'
MODEL_DIR = '/Users/haruto-k/research/processing_file/BERT/BERTModelCreate/Result/SaveModel'  # モデルが保存されているディレクトリ
MAX_LENGTH = 128

# モデルとトークナイザーのロード
Model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
Tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

# コメントデータを抽出する関数
def CommentDataExtract(CommentData):

    # 必要なコメントデータを抽出
    ExtractCommentData = {
        'Date': CommentData['date'],
        'AccountID': CommentData.get('author', {}).get('_account_id', ''),
        'CommentID': CommentData['id'],
        'Revision': CommentData['_revision_number'],
        'Author': CommentData.get('author', {}).get('name', ''),
        'Comment': CommentData['message']
    }

    # 抽出したコメントデータを返す
    return ExtractCommentData

# 修正確認のコメントを見つける関数
def FindAchieve(ReviewCommentsFile):

    # 修正確認コメントの定義ファイルの読み込み
    with open(AchieveCommentsFilePath, 'r') as AchieveFile:
        AchieveCommentsFile = json.load(AchieveFile)

    # 修正確認コメントの定義ファイルからコメントリストを抽出
    AchieveComments = [AchiveCommentItem['AchieveComments'] for AchiveCommentItem in AchieveCommentsFile]

    # 修正確認のコメントを保存するリストの初期化
    AchieveCommentsData = []

    # レビューコメント毎に紐づくか確認
    for CommentData in ReviewCommentsFile['messages']:

        # PR実装者によるコメントでないか確認
        if CommentData.get('author', {}).get('name', '') == ReviewCommentsFile.get('owner', {}).get('name', ''):

            # PR実装者のコメントは対象にしない
            continue

        # 修正確認コメントがコメント内に含まれていないか確認
        if not any(AchieveComment.lower() in CommentData['message'].lower() for AchieveComment in AchieveComments):
        
            # 修正確認コメントが含まれていないコメントは対象にしない
            continue
        
        # 修正確認を含むコメントの情報を保存
        AchieveCommentsData.append(CommentDataExtract(CommentData))

    # 修正確認コメント群のリストを返す
    return AchieveCommentsData

# 修正要求を見つける関数
def FindRequest(ReviewCommentsFile):

    # コメントデータの抽出
    CommentsData = ReviewCommentsFile['messages']
        
    # 修正要求を予測する関数の呼び出し
    PredictCommentData = [ReviewComment['message'] for ReviewComment in CommentsData]
    RequestPredictlist = PredictRequest(PredictCommentData)

    # 修正要求と予測されたコメントの情報を保存する変数の初期化
    RequestsCommentsData = []

    for RequestPredictClass, CommentData in zip(RequestPredictlist, CommentsData):

        # 修正要求のコメントでないか確認
        if RequestPredictClass != 1:
            continue

        # 実装者のコメントでないか確認
        if CommentData.get('author', {}).get('name', '') == CommentData.get('owner', {}).get('name', ''):
            continue

        RequestsCommentsData.append(CommentDataExtract(CommentData))
        
    # 修正要求と予測されたコメント群のリストを返す
    return RequestsCommentsData

# 修正確認コメントを定義に基づき紐づけるための関数
def DefinitionBasedAssociate(RequestsCommentData, AchieveCommentData):

    # 修正要求コメントと修正要求コメントが紐づいたかを表す変数の初期化
    AssociateRequest = RequestsCommentData

    # 修正要求の数だけ紐づくか確認
    for RequestCommentIndex in range(len(AssociateRequest)):
        
        # 各辞書に新しいキーを追加
        AssociateRequest[RequestCommentIndex]['同一検証者かつリビジョン更新後にコメント'] = SameReviewer.Associate(AssociateRequest[RequestCommentIndex], AchieveCommentData)
        AssociateRequest[RequestCommentIndex]['検証者は問わずリビジョン更新後にコメント'] = RegardlessReviewer.Associate(AssociateRequest[RequestCommentIndex], AchieveCommentData)

    # 修正要求コメントと修正要求コメントが紐づいたかを表す変数を返す
    return AssociateRequest

# 修正要求の予測をする関数
def PredictRequest(Comments):

    # コメントをトークナイズ
    Encoding = Tokenizer(Comments, truncation=True, padding='max_length', max_length=MAX_LENGTH, return_tensors='pt')
    
    # モデルを評価モードに設定
    Model.eval()

    # 推論を実行
    with torch.no_grad():
        Outputs = Model(**Encoding)
        RequestPredictlist = torch.argmax(Outputs.logits, dim=1).tolist()

    # 修正要求か否かを予測した結果を返す
    return RequestPredictlist

# 修正要求と修正確認を紐づける関数
def RequestAndAchieveAssociate(ReviewCommentsPath):

    # FormatFileの読み込み
    with open(ReviewCommentsPath, 'r') as Review_F:
        ReviewCommentsFile = json.load(Review_F)

    # 修正要求の予測を行う関数の呼び出し
    RequestsCommentsData = FindRequest(ReviewCommentsFile)

    # 修正確認のコメントを見つける関数の呼び出し
    AchieveCommentsData = FindAchieve(ReviewCommentsFile)

    # 修正要求と修正確認コメントを紐づける関数の呼び出し
    AssociateRequest = DefinitionBasedAssociate(RequestsCommentsData, AchieveCommentsData)

    # 出力するフォルダとファイル名の読み込み
    AssociateFolderName = Path(ReviewCommentsPath).parent.name
    AssociateFileName = Path(ReviewCommentsPath).stem

    # 出力するファイルパスの作成
    AssociateResultPath = '/Users/haruto-k/research/select_list/RequestAssociateAF/' + AssociateFolderName + '/' + AssociateFileName + '.csv'

    # 紐づけた結果の出力
    AssociateRequest_df = pd.DataFrame(AssociateRequest)
    AssociateRequest_df.to_csv(AssociateResultPath, index=False, encoding='utf_8_sig')

# メイン処理
def main():

    # パスを格納
    FormatPRFilePathList = glob(FormatPRFilePath)

    # ProcessPoolExecutorを使って並列処理
    with ProcessPoolExecutor() as executor:
        list(tqdm(executor.map(RequestAndAchieveAssociate, FormatPRFilePathList), total=len(FormatPRFilePath)))

if __name__ == "__main__":
    main()