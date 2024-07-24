# 同一検証者がリビジョン更新後にコメント記述しているか確認
def Associate(RequestCommentData, AchieveCommentsData):
    
    # 紐づいたコメントのIDを
    AssociateCommentsID = ''

    # 修正確認コメントの数だけ紐づくか確認
    for AchieveCommentData in AchieveCommentsData:

        # 同一検証者によるコメントか確認
        if RequestCommentData['Author'] != AchieveCommentData['Author']:
            break

        # 同一検証者によるコメント
        else:

            # リビジョン更新後のコメントか確認
            if RequestCommentData['Revision'] >= AchieveCommentData['Revision']:
                break
            
            # リビジョン更新後のコメント
            else:
                AssociateCommentsID += ', ' + AchieveCommentData['CommentId']

    # 紐づいたコメントのIDを返す
    return AssociateCommentsID