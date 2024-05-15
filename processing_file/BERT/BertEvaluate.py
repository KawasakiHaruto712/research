import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score
from torch.utils.data import DataLoader, Dataset

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

# 評価指標の計算
precision = precision_score(all_labels, all_preds)
recall = recall_score(all_labels, all_preds)
f1 = f1_score(all_labels, all_preds)

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
