import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# 予測結果のチェックリスト作成
def create_checkList(df, all_preds, all_labels):
    # 評価指標の計算
    precision = precision_score(all_labels, all_preds)
    recall = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)

    # 予測結果の追加，ヘッダの修正
    df.insert(loc = 0, column='precision', value=precision)
    df.insert(loc = 1, column='recall', value=recall)
    df.insert(loc = 2, column='f1', value=f1)
    df.insert(loc = 11, column='予測', value=all_preds)
    df = df.rename(columns={'text': 'comment', 'label': '修正要求'})
    return df

# データセットクラスの定義
class CommentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# データの読み込み
commentsLabel_csv_path = '/Users/haruto-k/research/select_list/chekList/alradyStart/checkList.csv'
df = pd.read_csv(commentsLabel_csv_path, header=0)

# 評価用にデータの変換
df = df.rename(columns={'comment': 'text', '修正要求': 'label'})
df['label'] = df['label'].replace('', '0').fillna(0).astype(int)

# モデル作成用に後半1割のPRを用いる
while True:
    try:
        labeled_PRNumber = int(input('PR that has been labeled: '))
        break
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
df = df[df['PRNumber'] > (labeled_PRNumber * 0.9)]
df = df[df['PRNumber'] <= labeled_PRNumber]

# トークナイザとモデルのロード
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
LabelModel_path = '/Users/haruto-k/research/processing_file/BERT/results'
model = BertForSequenceClassification.from_pretrained(LabelModel_path, num_labels=2)
model.eval()  # 評価モードに設定

# データセットの準備
test_dataset = CommentDataset(df['text'].tolist(), df['label'].tolist(), tokenizer)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# 予測
all_preds = []
all_labels = []
with torch.no_grad():
    for batch in tqdm(test_loader):
        inputs = {k: v.to(model.device) for k, v in batch.items() if k != 'labels'}
        labels = batch['labels'].to(model.device)
        outputs = model(**inputs)
        preds = torch.argmax(outputs.logits, dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# 結果リストの書き込み
checkList_df = create_checkList(df, all_preds, all_labels)
filePath_write = '/Users/haruto-k/research/select_list/chekList/alradyStart/recheckList_results.csv'
checkList_df.to_csv(filePath_write, index = False, encoding='utf_8_sig')