import pandas as pd

checklist_path = "../../select_list/checkList/alradyStart/checklist.csv"
check_PR_num_path = "../../select_list/labeled_PRNumber.txt"
code_label_sum_path = "../../select_list/checkList/alradyStart/code_label_sum.csv"

def read_checklist():
    checklist = pd.read_csv(checklist_path, header=0)
    with open(check_PR_num_path) as PR_num_txt:
        textline = PR_num_txt.readlines()
    
    check_PR_num = float(textline[0])
    checklist = checklist[checklist["PRNumber"] <= check_PR_num]
    return checklist

def count_code_label(checklist):
    minus_2_sum = minus_1_sum = plus_1_sum = plus_2_sum = 0
    for _, checklist_row in checklist.iterrows():
        if "Code-Review-2" in checklist_row["comment"] or "Do not submit" in checklist_row["comment"]:
            minus_2_sum += 1
        if "Code-Review-1" in checklist_row["comment"] or "I would prefer that you didn't merge this" in checklist_row["comment"]:
            minus_1_sum += 1
        if "Code-Review+1" in checklist_row["comment"] or "Looks good to me, but someone else must approve" in checklist_row["comment"]:
            plus_1_sum += 1
        if "Code-Review+2" in checklist_row["comment"] or "Looks good to me (core reviewer)" in checklist_row["comment"]:
            plus_2_sum += 1
    code_label_sum = [{
        "Code-Review-2の数": minus_2_sum,
        "Code-Review-1の数": minus_1_sum,
        "Code-Review+1の数": plus_1_sum,
        "Code-Review+2の数": plus_2_sum
    }]
    return pd.DataFrame(code_label_sum)

def main():
    checklist = read_checklist()
    code_label_sum_df = count_code_label(checklist)
    code_label_sum_df.to_csv(code_label_sum_path, index=False, encoding="utf_8_sig")

if __name__ == "__main__":
    main()