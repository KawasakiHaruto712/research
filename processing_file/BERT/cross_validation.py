import json
import torch
import pandas as pd
from sklearn.model_selection import KFold, train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm

# CSVファイルの読み込み
commentsLabel_csv_path = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
df = pd.read_csv(commentsLabel_csv_path, header=0)

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

# 5分割交差検証の設定
kf = KFold(n_splits=5, shuffle=True, random_state=712)
results = []
all_preds = []
all_indices = []

# 5分割交差検証の実行
for fold, (train_idx, test_idx) in enumerate(kf.split(df)):
    print(f'Fold {fold}')
    train_val_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

    # 訓練データと検証データに分割 (7:3 の比率で分割)
    train_df, val_df = train_test_split(train_val_df, test_size=3/10, random_state=712)

    # データセットの準備
    train_dataset = CommentDataset(train_df['text'].tolist(), train_df['label'].tolist(), tokenizer)
    val_dataset = CommentDataset(val_df['text'].tolist(), val_df['label'].tolist(), tokenizer)
    test_dataset = CommentDataset(test_df['text'].tolist(), test_df['label'].tolist(), tokenizer)

    # BERTモデルのロード
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

    # トレーニングの設定
    training_args = TrainingArguments(
        output_dir=f'./cross_validation/default/results_fold_{fold}',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f'./logs_fold_{fold}',
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

    # テストデータに対する予測
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    fold_preds = []
    model.eval()  # 評価モードに設定
    with torch.no_grad():
        for batch in tqdm(test_loader):
            inputs = {k: v.to(model.device) for k, v in batch.items() if k != 'labels'}
            outputs = model(**inputs)
            preds = torch.argmax(outputs.logits, dim=1)
            fold_preds.extend(preds.cpu().numpy())

    # 予測結果の保存
    all_preds.extend(fold_preds)
    all_indices.extend(test_idx.tolist())  # リストに変換して追加

    # 評価指標の計算
    precision = precision_score(test_df['label'], fold_preds)
    recall = recall_score(test_df['label'], fold_preds)
    f1 = f1_score(test_df['label'], fold_preds)

    results.append({
        'precision': precision,
        'recall': recall,
        'f1': f1
    })

# 結果の保存
results_df = pd.DataFrame(results)
sorted_index_preds = dict(sorted(zip(all_indices, all_preds)))
sorted_preds = [''] * len(df)
for dfRow in  range(len(df)):
    if dfRow in sorted_index_preds:
        sorted_preds[dfRow] = sorted_index_preds[dfRow]
    else:
        sorted_preds[dfRow] = '予測なし'  # 予測がない場合にデフォルト値を設定


# 元のデータフレームに予測結果を組み込む
df.insert(loc = 0, column='precision', value=results_df['precision'].median())
df.insert(loc = 1, column='recall', value=results_df['recall'].median())
df.insert(loc = 2, column='f1', value=results_df['f1'].median())
df.insert(loc = 12, column='予測', value=sorted_preds)
df = df.rename(columns={'text': 'comment', 'label': '修正要求'})

df.to_csv('/Users/haruto-k/research/select_list/checkList/alradyStart/checklist_result.csv', index=False, encoding='utf_8_sig')
results_df.to_csv('/Users/haruto-k/research/select_list/checkList/alradyStart/value/default.csv', index=False, encoding="utf_8_sig")