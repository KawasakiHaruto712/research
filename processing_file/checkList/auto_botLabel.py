from glob import glob
from tqdm import tqdm
import csv

def label_bots(checkList):
    labeled_checkList = [checkList[0] + ['bot']] # 新しいリストを作成し，bot列を作成
    for row in tqdm(checkList[1:]):
        new_row = row[:] # 元のリストをコピー
        author = str(row[6]).strip().lower()
        comment = str(row[7]).strip().lower()

        if author.endswith('ci'): # authorの最後の文字がCIか
            new_row.append(1)
        elif 'build' in comment: # コメントにbuildが含まれているか
            new_row.append(1)
        else:
            new_row.append('')
        labeled_checkList.append(new_row)
    return labeled_checkList

def main():
    # チェックリストの読み込み
    filePath_read = '/Users/haruto-k/research/select_list/checkList.csv'
    with open(filePath_read, 'r') as readFile:
        checkList = list(csv.reader(readFile))
    labeled_checkList = label_bots(checkList)
    filePath_write = '/Users/haruto-k/research/select_list/checkList.csv'
    with open(filePath_write, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(labeled_checkList)

if __name__ == "__main__":
    main()