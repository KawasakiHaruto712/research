import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

# CSVファイルの読み込み
df = pd.read_csv('/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv', header=0)

# データの前処理
df = df.rename(columns={'comment': 'text', '修正要求': 'label'})
df['label'] = df['label'].replace('', '0').fillna(0).astype(int)

# ラベル付けされているPR番号を読み込み
with open('/Users/haruto-k/research/select_list/labeled_PRNumber.txt') as f_txt:
    textLine = f_txt.readlines()
labeled_PRNumber = float(textLine[0])
df = df[df['PRNumber'] <= labeled_PRNumber]

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

# トークナイザのロード
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# ownerとauthorが一致する行は訓練，検証，予測に用いない
df = df[df['owner'] != df['author']]

# 訓練データと検証データに分割 (7:3 の比率で分割)
train_df, val_df = train_test_split(df, test_size=3/10, random_state=712)

# データセットの準備
train_dataset = CommentDataset(train_df['text'].tolist(), train_df['label'].tolist(), tokenizer)
val_dataset = CommentDataset(val_df['text'].tolist(), val_df['label'].tolist(), tokenizer)

# BERTモデルのロード
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# トレーニングの設定
training_args = TrainingArguments(
    output_dir=f'./BERTModelCreate/Ongoing',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir=f'./Logs',
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch"
)

# トレーナーの初期化
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# トレーニングと評価
trainer.train()

# モデルの保存
model.save_pretrained('./BERTModelCreate/Result/SaveModel')