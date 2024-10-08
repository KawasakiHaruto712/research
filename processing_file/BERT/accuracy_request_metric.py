import pandas as pd

checklist_path = "../../select_list/checkList/alradyStart/checklist_result.csv"
check_PR_num_path = "../../select_list/labeled_PRNumber.txt"
request_metric_accuracy_path = "../../select_list/checkList/alradyStart/request_metric_accuracy.csv"

def read_checklist():
    checklist = pd.read_csv(checklist_path, header=0)
    with open(check_PR_num_path) as PR_num_txt:
        textline = PR_num_txt.readlines()
    
    check_PR_num = float(textline[0])
    checklist = checklist[checklist["PRNumber"] <= check_PR_num]
    return checklist

def accuracy_metric(checklist):
    true_improve_sum = true_refact_sum = true_outside_code_sum = true_bug_sum = true_typo_sum = 0
    pred_improve_sum = pred_refact_sum = pred_outside_code_sum = pred_bug_sum = pred_typo_sum = 0
    for _, checklist_row in checklist.iterrows():
        if checklist_row["レビューアによるコード追加要求"] == 1 or checklist_row["レビューアによるコード改善要求"] == 1:
            true_improve_sum += 1
            if checklist_row["予測"] == 1:
                pred_improve_sum += 1
        if checklist_row["リファクタリング"] == 1 or checklist_row["コード整形，コメントアウト修正"] == 1:
            true_refact_sum += 1
            if checklist_row["予測"] == 1:
                pred_refact_sum += 1
        if checklist_row["コード外の修正，改善"] == 1:
            true_outside_code_sum += 1
            if checklist_row["予測"]:
                pred_outside_code_sum += 1
        if checklist_row["バグ修正要求"] == 1:
            true_bug_sum += 1
            if checklist_row["予測"] == 1:
                pred_bug_sum += 1
        if checklist_row["typo"] == 1:
            true_typo_sum += 1
            if checklist_row["予測"]:
                pred_typo_sum += 1

    request_metric_accracy = [{
        f"機能改善({true_improve_sum}件)": pred_improve_sum / true_improve_sum,
        f"リファクタリング/コード整形({true_refact_sum}件)": pred_refact_sum / true_refact_sum,
        f"コード外の修正({true_outside_code_sum}件)": pred_outside_code_sum / true_outside_code_sum,
        f"バグ修正({true_bug_sum}件)": pred_bug_sum / true_bug_sum,
        f"typo({true_typo_sum}件)": pred_typo_sum / true_typo_sum
    }]
    return pd.DataFrame(request_metric_accracy)

def main():
    checklist = read_checklist()
    request_metric_accracy_df = accuracy_metric(checklist)
    request_metric_accracy_df.to_csv(request_metric_accuracy_path, index=False, encoding="utf_8_sig")

if __name__ == "__main__":
    main()