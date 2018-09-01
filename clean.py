import os
import sys
from datetime import datetime
import zipfile
from pymongo import MongoClient # sudo pip3 install pymongo
import pytz # sudo pip3 install pytz

# 将棋クエストの古い棋譜を退避する
# 使用例 : python3 clean.py /home/loftkun/dev/nginx/html/quest/

# 新しい棋譜の閾値[sec] : 半年以内
NEW=float(60 * 60 * 24 * 365 * 0.5)

# 古い棋譜の閾値[sec] : 1年以上
OLD=float(60 * 60 * 24 * 365 * 1)

# 現在時刻[sec]
NOW=float(datetime.now().strftime('%s'))

# mongodb
#client = MongoClient('localhost', 27017)
user = ""
pwd  = ""
host = ""
client = MongoClient("mongodb://{}:{}@{}".format(user,pwd,host))
db = client.quest

# 時刻文字列パース
def iso_to_jstdt(iso_str):
    dt = None
    try:
        dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Tokyo"))
    except ValueError:
        try:
            dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            dt = dt.astimezone(pytz.timezone("Asia/Tokyo"))
        except ValueError:
            pass
    return dt

# db更新
def updateDB(user, game, kif):

	# DBからcollection取得
	# recordsをforで回すとカーソルが移動するため
	# ここで毎回取得する ( or 要 カーソルを先頭に移動)
	colname = "{}-{}".format(user, game)
	col = db[colname]
	records = col.find()
	
	updated = False
	for record in records:
		# DB上のcreatedから棋譜ファイル名用のcreatedを生成
		dt = iso_to_jstdt( record["created"] ) # ISO-8601 拡張フォーマット
		dt = dt.strftime('%Y%m%d_%H%M%S') # 棋譜ファイル名はこのフォーマット

		# game種別変更時の保守性を考え拡張子は考慮せず実装
		# 棋譜ファイル名( 拡張子なし )
		kifNameNoExt = "{}_{}_{}".format(user, game, dt) # "loftkun_shogi10_20180831_180005"のような文字列
		#print("kifNameNoExt={}".format(kifNameNoExt))

		# DBにあるはず
		if kif.find(kifNameNoExt) < 0:
			continue

		# あったので更新
		gameId = record["id"]	
		query = {'id':{ '$eq' : gameId}};
		value = { '$set' : { 'csaExists' : False } };
		col.update(query, value)

		updated = True
	return updated

# 退避
def move(quest, user, game, gamePath, kifList):
	# 全kifをzipにする
	zipPath = os.path.join(gamePath, "all.zip")

	# 参考
	# https://note.nkmk.me/python-zipfile/
	with zipfile.ZipFile(zipPath, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
		for kif in kifList:
			new_zip.write(kif)
			#print("add zip : {}".format(kif))
	#print ("[move] zip created   : {}".format(zipPath))

	# 古い棋譜を削除する
	for kif in kifList:
		# DB更新
		#result = updateDB("loftkun", "shogi10", "/home/loftkun/dev/nginx/html/quest/loftkun/shogi10/loftkun_shogi10_20180831_180005.csa")
		result = updateDB(user, game, kif)
		
		# 削除
		os.remove(kif)
		print("[move] DB updated={} : removed kif={}".format(result, kif))

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
	gamePath = os.path.join(quest, user, game)

	kifList = []
	kifs = os.listdir(gamePath)
	for kif in kifs:
		kifPath = os.path.join(quest, user, game, kif)
		if os.path.isdir(kifPath):
			print("{} is dir".format(kifPath))
			continue
		base, ext = os.path.splitext(kifPath)
		#print("base={} ext={}".format(base, ext))
		if ext == ".zip":
			#print("{} is zip".format(kifPath))
			continue
		kifList.append(kifPath)

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
	moveList = []
	for kif in kifList:
		mtime = os.stat(kif).st_mtime
		diff = NOW - mtime
		if diff < OLD:
			continue
		# 退避
		#print("{}/{} old : {}".format(user, game, kif))
		moveList.append(kif)

	if len(moveList) > 0:
		move(quest, user, game, gamePath, moveList)

	return len(moveList)

if __name__ == '__main__':
	if( len(sys.argv) != 2 ):
		print('usage : clean.py searchPATH')
		sys.exit()
	
	print("NOW={}".format(NOW))
	print("NEW={}".format(NEW))
	print("OLD={}".format(OLD))

	quest = sys.argv[1]
	users = os.listdir(quest)
	users.sort()

	totalMoveCnt = 0
	for user in users:
		# botは除外
		#if user.startswith(":"):
		#	continue
		path = os.path.join(quest, user)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		moveCnt = checkUser(quest, user)
		totalMoveCnt = totalMoveCnt + moveCnt
	print("totalMoveCnt = {}".format(totalMoveCnt))


