# 検証者問わずリビジョン更新後にコメント記述しているか確認
def Associate(RequestCommentData, AchieveCommentsData):

    # 紐づいたコメントのIDを
    AssociateCommentsID = ''

    # 修正確認コメントの数だけ紐づくか確認
    for AchieveCommentData in AchieveCommentsData:

        # リビジョン更新後のコメントか確認
        if AchieveCommentData['Revision'] <= RequestCommentData['Revision']:
            
            # リビジョン更新前のコメントは対象にしない
            continue

        # 一つ目に紐づいたコメントか確認
        if AssociateCommentsID == '':

            # 紐づいたコメントのIDを保存
            AssociateCommentsID += AchieveCommentData['CommentID']

            # 次の修正確認コメントの確認に移る
            continue

        # 二つ目以降に紐づいたコメントのIDを保存
        AssociateCommentsID += ', ' + AchieveCommentData['CommentID']

    # 紐づいたコメントのIDを返す
    return AssociateCommentsID