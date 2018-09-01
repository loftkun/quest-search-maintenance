import os
import sys
from datetime import datetime
import shutil
import numpy as np

# 将棋クエストの棋譜を数える
# 使用例 : python3 count.py /home/loftkun/dev/nginx/html/quest/

# 新しい棋譜の閾値[sec] : 半年以内
NEW=float(60 * 60 * 24 * 365 * 0.5)

# 古い棋譜の閾値[sec] : 1年以上
OLD=float(60 * 60 * 24 * 365 * 1)

# 現在時刻[sec]
NOW=float(datetime.now().strftime('%s'))

# ユーザ処理
def checkUser(quest, user):
	total = np.array(( 0, 0, 0 ))
	games = os.listdir(os.path.join(quest, user))
	for game in games:
		path = os.path.join(quest, user, game)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		userInfo = checkGame(quest, user, game)
		print("{}\t{}\t{}\t{}".format(os.path.join(quest, user, game), userInfo[0], userInfo[1], userInfo[2]))
		total = total + userInfo
	return total

# ゲーム処理
def checkGame(quest, user, game):
	#print("{}/{} start".format(user, game))
	path = os.path.join(quest, user, game)

	kifList = []
	kifs = os.listdir(path)
	for kif in kifs:
		path = os.path.join(quest, user, game, kif)
		if os.path.isdir(path):
			print("{} is dir".format(path))
			continue
		kifList.append(path)

	# 更新時刻の降順ソート。つまり新しい順
	kifList.sort(key=os.path.getmtime, reverse=True)

	# 新しい棋譜を数える
	newCnt = 0
	oldCnt = 0
	totalCnt = 0
	for kif in kifList:
		mtime = os.stat(kif).st_mtime
		diff = NOW - mtime
		if diff < NEW:
			newCnt = newCnt + 1
		if diff > OLD:		
			oldCnt = oldCnt + 1
		totalCnt = totalCnt + 1
	return np.array(( newCnt, oldCnt, totalCnt ))

if __name__ == '__main__':
	if( len(sys.argv) != 2 ):
		print('usage : clean.py path')
		sys.exit()
	
	print("NOW={}".format(NOW))
	print("NEW={}".format(NEW))
	print("OLD={}".format(OLD))

	quest = sys.argv[1]
	users = os.listdir(quest)
	users.sort()
	print("user num={}".format(len(users)))

	cnt = 0
	total = np.array(( 0, 0, 0 ))
	for user in users:
		# botは除外
		# if user.startswith(":"):
		#	continue
		path = os.path.join(quest, user)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		userInfo = checkUser(quest, user)
		total = total + userInfo

		cnt = cnt + 1
		#if cnt > 100:
		#	break
	print("user={} total = {}".format(cnt, total))


