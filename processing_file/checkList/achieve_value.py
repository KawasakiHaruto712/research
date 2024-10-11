import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

checklist_path = "../../select_list/checkList/alradyStart/checklist.csv"
check_PR_num_path = "../../select_list/labeled_PRNumber.txt"
achieve_value_path = "../../select_list/checkList/alradyStart/achieve_value.csv"

# チェックリストの読み込み
def read_checklist():

    # ラベル付したPRまでのチェックリストを抽出
    checklist = pd.read_csv(checklist_path, header=0)
    with open(check_PR_num_path) as PR_num_txt:
        textline = PR_num_txt.readlines()
    check_PR_num = float(textline[0])
    checklist = checklist[checklist["PRNumber"] <= check_PR_num]

    return checklist

def cal_achieve_value(checklist):
    true = []
    pred = []
    for _, checklist_row in checklist.iterrows():
        if checklist_row["修正確認"] == 1:
            true.append(1)
        else:
            true.append(0)
        if ("Code-Review+2" in checklist_row["comment"] or
            "Code-Review+1" in checklist_row["comment"] or
            "lgtm" in checklist_row["comment"].lower() or
            "looks good" in checklist_row["comment"].lower() or
            "looks ok" in checklist_row["comment"].lower()):
            pred.append(1)
        else:
            pred.append(0)
    precision = precision_score(true, pred)
    recall = recall_score(true, pred)
    f1 = f1_score(true, pred)

    achieve_value = [{
        'precision': precision,
        'recall': recall,
        'f1': f1
    }]
    return pd.DataFrame(achieve_value)

def main():
    checklist = read_checklist()
    achieve_value_df = cal_achieve_value(checklist)
    achieve_value_df.to_csv(achieve_value_path, index=False, encoding="utf_8_sig")

if __name__ == "__main__":
    main()