import pandas as pd

checklist_path = "../../select_list/checkList/alradyStart/checklist.csv"
check_PR_num_path = "../../select_list/labeled_PRNumber.txt"

# チェックリストの読み込み
def read_checklist():

    # ラベル付したPRまでのチェックリストを抽出
    checklist = pd.read_csv(checklist_path, header=0)
    with open(check_PR_num_path) as PR_num_txt:
        textline = PR_num_txt.readlines()
    check_PR_num = float(textline[0])
    checklist = checklist[checklist["PRNumber"] <= check_PR_num]

    return checklist

def req_include(checklist):
    achieve = req = 0
    for _, checklist_row in checklist.iterrows():
        if checklist_row["修正確認"] != 1:
            continue
        if ("Code-Review+1" in checklist_row["comment"] or 
            "Looks good to me, but someone else must approve" in checklist_row["comment"] or
            "Code-Review+2" in checklist_row["comment"] or
            "Looks good to me, approved" in checklist_row["comment"]):
            achieve += 1
            if checklist_row["修正要求"] == 1:
                req += 1
    return achieve, req

def main():
    checklist = read_checklist()
    achieve, req = req_include(checklist)
    print(f"修正確認ラベルの数: {achieve}，修正確認に含まれる修正要求の数{req}，割合{req/achieve}")

if __name__ == "__main__":
    main()