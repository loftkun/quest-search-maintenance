import os
import sys
from datetime import datetime
import shutil

# 将棋クエストの古い棋譜を退避する
# 使用例 : python3 clean.py /home/loftkun/dev/clean/ /home/loftkun/dev/nginx/html/quest/

# 退避先
MOVE_PATH=""

# 退避ディレクトリ名
MOVE_DIR_NAME="moved"

# 新しい棋譜の閾値[sec] : 半年以内
NEW=float(60 * 60 * 24 * 365 * 0.5)

# 古い棋譜の閾値[sec] : 1年以上
OLD=float(60 * 60 * 24 * 365 * 1)

# 現在時刻[sec]
NOW=float(datetime.now().strftime('%s'))

# 退避
def move(user, game, kif):
	path = os.path.join(MOVE_PATH, MOVE_DIR_NAME, user, game)
	if not os.path.isdir(path):
		os.makedirs(path)
	#shutil.move(kif, os.path.join(path, kif))

# ユーザ処理
def checkUser(quest, user):
	totalMoveCnt = 0
	games = os.listdir(os.path.join(quest, user))
	for game in games:
		path = os.path.join(quest, user, game)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		moveCnt = checkGame(quest, user, game)
		if moveCnt:
			print("{} : moved {} kif.".format(os.path.join(quest, user, game),moveCnt))
		totalMoveCnt = totalMoveCnt + moveCnt
	return totalMoveCnt

# ゲーム処理
def checkGame(quest, user, game):
	print("{}/{} start".format(user, game))
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

	# 新しい棋譜が1つでもあるユーザは対象外
	for kif in kifList:
		mtime = os.stat(kif).st_mtime
		diff = NOW - mtime
		if diff < NEW:
			# 新しい棋譜があるので以降の処理不要
			print("{}/{} has new kif. ( mtime={} kif={} )".format(user, game, mtime, kif))
			return 0

	# 新しい棋譜はないので古い退避を退避する
	moveCnt = 0
	for kif in kifList:
		mtime = os.stat(kif).st_mtime
		diff = NOW - mtime
		if diff < OLD:
			continue
		# 退避
		print("{}/{} move {}".format(user, game, kif))
		move(user, game, kif)	
		moveCnt = moveCnt + 1
	return moveCnt

if __name__ == '__main__':
	if( len(sys.argv) != 3 ):
		print('usage : clean.py MOVE_PATH searchPATH')
		sys.exit()
	
	print("NOW={}".format(NOW))
	print("NEW={}".format(NEW))
	print("OLD={}".format(OLD))

	MOVE_PATH = sys.argv[1]

	quest = sys.argv[2]
	users = os.listdir(quest)
	users.sort()

	totalMoveCnt = 0
	for user in users:
		# botは除外
		if user.startswith(":"):
			continue
		path = os.path.join(quest, user)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		moveCnt = checkUser(quest, user)
		totalMoveCnt = totalMoveCnt + moveCnt
	print("totalMoveCnt = {}".format(totalMoveCnt))


