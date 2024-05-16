import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score
from torch.utils.data import DataLoader, Dataset

def create_checkList(df, all_preds, all_labels):
    # 評価指標の計算
    precision = precision_score(all_labels, all_preds)
    recall = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)

    # 結果リストの作成
    checkList = []
    commentsList = df['text'].tolist()
    for commentsNumber in range(len(commentsList)):
        checkList.append({
            'comments': commentsList[commentsNumber],
            'correct': all_labels[commentsNumber],
            'prediction': all_preds[commentsNumber],
            'same': 1 if all_preds[commentsNumber] == all_labels[commentsNumber] else '',
            'precision': precision if commentsNumber == 0 else '',
            'recall': recall if commentsNumber == 0 else '',
            'f1': f1 if commentsNumber == 0 else ''
        })
    checkList_df = pd.DataFrame(checkList)
    return checkList_df

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
df = pd.read_csv('checkList_test.csv', header=None)
df.columns = ['text', 'label']

# トークナイザとモデルのロード
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
LabelModel_path = '/Users/haruto-k/research/processing_file/BERT/results/checkpoint-500'
model = BertForSequenceClassification.from_pretrained(LabelModel_path, num_labels=2)
model.eval()  # 評価モードに設定

# データセットの準備
test_dataset = CommentDataset(df['text'].tolist(), df['label'].tolist(), tokenizer)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# 予測
all_preds = []
all_labels = []
with torch.no_grad():
    for batch in test_loader:
        inputs = {k: v.to(model.device) for k, v in batch.items() if k != 'labels'}
        labels = batch['labels'].to(model.device)
        outputs = model(**inputs)
        preds = torch.argmax(outputs.logits, dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# 結果リストの書き込み
checkList_df = create_checkList(df, all_preds, all_labels)
filePath_write = '/Users/haruto-k/research/processing_file/BERT/checkList_results.csv'
checkList_df.to_csv(filePath_write, index = False)