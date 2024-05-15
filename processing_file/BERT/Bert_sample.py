import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset, DataLoader

# CSVファイルの読み込み
commentsLabel_csv_path = '/Users/haruto-k/research/processing_file/BERT/checkList.csv'
df = pd.read_csv(commentsLabel_csv_path, header=None)
df.columns = ['text', 'label']

# データセットの分割
train_texts, val_texts, train_labels, val_labels = train_test_split(df['text'], df['label'], test_size=1/9)

# トークナイザのロード
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# データセットクラスの定義
class CommentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(texts.tolist(), truncation=True, padding=True, max_length=128)
        self.labels = labels.tolist()

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# データセットの準備
train_dataset = CommentDataset(train_texts, train_labels, tokenizer)
val_dataset = CommentDataset(val_texts, val_labels, tokenizer)

# BERTモデルのロード
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# トレーニングの設定
training_args = TrainingArguments(
    output_dir='./results',          # 出力ディレクトリ
    num_train_epochs=3,              # トレーニングエポック数
    per_device_train_batch_size=8,   # バッチサイズ
    per_device_eval_batch_size=16,   # 評価時のバッチサイズ
    warmup_steps=500,                # ウォームアップステップ数
    weight_decay=0.01,               # 重み減衰
    logging_dir='./logs',            # ログディレクトリ
    logging_steps=10,
)

# トレーナーの初期化
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# トレーニング開始
trainer.train()
