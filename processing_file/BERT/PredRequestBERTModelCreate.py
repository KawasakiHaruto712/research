import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

# 定数の定義
DATA_PATH = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
LABELS_PATH = '/Users/haruto-k/research/select_list/labeled_PRNumber.txt'
MODEL_NAME = 'bert-base-uncased'
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
    
    # ラベル済みPR数が記載されているファイルの読み込み
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
def train_and_evaluate(train_dataset, val_dataset):

    # BERTモデルの読み込み
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    training_args = TrainingArguments(
        output_dir='./RequestPredictModel',  # 結果出力先
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE_TRAIN,
        per_device_eval_batch_size=BATCH_SIZE_EVAL,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./CreageModelLogs',  # ログ出力先
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        no_cuda=True
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

# メイン処理
def main():

    # データの読み込みと前処理
    df = load_and_preprocess_data(DATA_PATH, LABELS_PATH)
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    
    # トレインとバリデーションに分割
    train_df, val_df = train_test_split(df, test_size=0.3, random_state=RANDOM_STATE)
    
    # データセットの作成
    train_dataset = CommentDataset(train_df['text'].tolist(), train_df['label'].tolist(), tokenizer)
    val_dataset = CommentDataset(val_df['text'].tolist(), val_df['label'].tolist(), tokenizer)

    # トレーニングと評価の実行
    train_and_evaluate(train_dataset, val_dataset)

if __name__ == "__main__":
    main()