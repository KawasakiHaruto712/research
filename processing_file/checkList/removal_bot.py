from glob import glob
from tqdm import tqdm
from pathlib import Path
import json

def removal_messages(filePath):
    with open(filePath) as rf:
        reviewFile = json.load(rf)
    botNames_filePath = '/Users/haruto-k/research/project/botNames.json'
    with open(botNames_filePath) as bf:
        botNames = json.load(bf)
    removal = 0

    i = len(reviewFile['messages']) - 1
    while i >= 0:
        for bot in botNames:
            if reviewFile['messages'][i].get('author', {}).get('name', '').lower() == bot:
                del reviewFile['messages'][i]
                i -= 1
                break
        i -= 1
    if not reviewFile['messages']:
        removal = 1
    return removal, reviewFile

def main():
    filePath_read = '/Users/haruto-k/research/project/formatFile/*/*.json'
    filePath_list = glob(filePath_read)
    for filePath in tqdm(filePath_list):
        removal, reviewFile = removal_messages(filePath)
        if removal != 1:
            p_file = Path(filePath)
            folderName = p_file.parent.name
            fileName = p_file.stem
            filePath_write = '/Users/haruto-k/research/select_list/removal_bot/' + folderName + '/' + fileName + '.json'
            with open(filePath_write, 'w') as f:
                json.dump(reviewFile, f, indent=4)

if __name__ == "__main__":
    main()