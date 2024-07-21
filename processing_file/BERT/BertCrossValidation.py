import torch
import pandas as pd
from sklearn.model_selection import KFold, train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm

# 定数の定義
DATA_PATH = '/work/research/select_list/checkList/alradyStart/checkList.csv'
LABELS_PATH = '/work/research/processing_file/BERT/labeled_PRNumber.txt'
RESULT_PATH = '/work/research/select_list/checkList/alradyStart/checkList_result.csv'
MODEL_NAME = 'bert-base-uncased'
N_SPLITS = 10
RANDOM_STATE = 712
MAX_LENGTH = 128
BATCH_SIZE_TRAIN = 8
BATCH_SIZE_EVAL = 16
NUM_EPOCHS = 3

# CSVファイルの読み込みと前処理
def load_and_preprocess_data(data_path, labels_path):
    df = pd.read_csv(data_path, header=0)
    df = df.rename(columns={'comment': 'text', '修正要求': 'label'})
    df['label'] = df['label'].replace('', '0').fillna(0).astype(int)
    
    # ラベルファイルの読み込み
    with open(labels_path) as f_txt:
        textLine = f_txt.readlines()
    labeled_PRNumber = float(textLine[0])
    
    # PRNumberがlabeled_PRNumber以下のデータのみを使用
    df = df[df['PRNumber'] <= labeled_PRNumber]
    
    return df

# データセットクラスの定義
class CommentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=MAX_LENGTH)
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# トレーニングと評価を実行する関数
def train_and_evaluate(train_dataset, val_dataset, test_dataset, fold):
    # BERTモデルの読み込み
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    training_args = TrainingArguments(
        output_dir=f'./results/results_fold_{fold}',  # 結果出力先
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE_TRAIN,
        per_device_eval_batch_size=BATCH_SIZE_EVAL,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f'./logs_fold_{fold}',  # ログ出力先
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch"
    )
    # トレーナーの設定
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )
    # トレーニングの実行
    trainer.train()
    
    # テストデータローダーの作成
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE_EVAL, shuffle=False)
    fold_preds = []
    model.eval()
    # テストデータでの予測
    with torch.no_grad():
        for batch in tqdm(test_loader):
            inputs = {k: v.to(model.device) for k, v in batch.items() if k != 'labels'}
            outputs = model(**inputs)
            preds = torch.argmax(outputs.logits, dim=1)
            fold_preds.extend(preds.cpu().numpy())
    
    return fold_preds

# メイン処理
def main():
    # データの読み込みと前処理
    df = load_and_preprocess_data(DATA_PATH, LABELS_PATH)
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    
    # PRNumberごとにデータを分割
    pr_numbers = df['PRNumber'].unique()
    kf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    
    results = []
    all_preds = []
    all_indices = []

    # 各フォールドごとに処理
    for fold, (train_val_idx, test_idx) in enumerate(kf.split(pr_numbers)):
        print(f'Fold {fold+1}')
        
        # トレイン・バリデーションとテストに分割
        train_val_pr_numbers = pr_numbers[train_val_idx]
        test_pr_numbers = pr_numbers[test_idx]

        train_val_df = df[df['PRNumber'].isin(train_val_pr_numbers)]
        test_df = df[df['PRNumber'].isin(test_pr_numbers)]

        # オーナーと著者が異なるデータのみを使用
        train_val_df = train_val_df[train_val_df['owner'] != train_val_df['author']]
        test_df = test_df[test_df['owner'] != test_df['author']]
        
        # トレインとバリデーションに分割
        train_pr_numbers, val_pr_numbers = train_test_split(train_val_pr_numbers, test_size=1/9, random_state=RANDOM_STATE)
        
        train_df = train_val_df[train_val_df['PRNumber'].isin(train_pr_numbers)]
        val_df = train_val_df[train_val_df['PRNumber'].isin(val_pr_numbers)]
        
        # データセットの作成
        train_dataset = CommentDataset(train_df['text'].tolist(), train_df['label'].tolist(), tokenizer)
        val_dataset = CommentDataset(val_df['text'].tolist(), val_df['label'].tolist(), tokenizer)
        test_dataset = CommentDataset(test_df['text'].tolist(), test_df['label'].tolist(), tokenizer)

        # トレーニングと評価の実行
        fold_preds = train_and_evaluate(train_dataset, val_dataset, test_dataset, fold)
        
        all_preds.extend(fold_preds)
        all_indices.extend(test_df.index.tolist())

        # 精度、再現率、F1スコアの計算
        precision = precision_score(test_df['label'], fold_preds)
        recall = recall_score(test_df['label'], fold_preds)
        f1 = f1_score(test_df['label'], fold_preds)

        results.append({
            'precision': precision,
            'recall': recall,
            'f1': f1
        })
    
    # 結果のデータフレーム作成
    results_df = pd.DataFrame(results)
    sorted_index_preds = dict(sorted(zip(all_indices, all_preds)))
    sorted_preds = [''] * len(df)
    for dfRow in range(len(df)):
        if dfRow in sorted_index_preds:
            sorted_preds[dfRow] = sorted_index_preds[dfRow]
    
    # 結果の追加と保存
    df.insert(loc=0, column='precision', value=results_df['precision'].mean())
    df.insert(loc=1, column='recall', value=results_df['recall'].mean())
    df.insert(loc=2, column='f1', value=results_df['f1'].mean())
    df.insert(loc=12, column='予測', value=sorted_preds)
    df = df.rename(columns={'text': 'comment', 'label': '修正要求'})
    
    # オーナーと著者が同じ場合のデータをNAに設定
    df.loc[df['owner'] == df['author'], '予測'] = pd.NA
    df.loc[df['owner'] == df['author'], '修正要求'] = pd.NA
    
    df.to_csv(RESULT_PATH, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    main()