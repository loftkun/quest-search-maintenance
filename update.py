import os
import sys
from datetime import datetime
import zipfile
from pymongo import MongoClient # sudo pip3 install pymongo
import pytz # sudo pip3 install pytz

# クエストのDBを更新する
# 使用例 : python3 update.py /home/loftkun/dev/nginx/html/quest/

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

# ユーザ処理
def checkUser(quest, user):
	totalUpdateCnt = 0
	games = os.listdir(os.path.join(quest, user))
	for game in games:
		path = os.path.join(quest, user, game)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		updatedCnt = checkGame(quest, user, game)
		print("{} : updated {} records.".format(os.path.join(quest, user, game), updatedCnt))

		totalUpdateCnt = totalUpdateCnt + updatedCnt
	return totalUpdateCnt

# ゲーム処理
def checkGame(quest, user, game):
	print("{}/{} start".format(user, game))
	gamePath = os.path.join(quest, user, game)

	# 全棋譜
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

	# コレクション
	colname = "{}-{}".format(user, game)
	col = db[colname]
	records = col.find()
	updatedCnt = 0
	for record in records:
		# DB上のcreatedから棋譜ファイル名用のcreatedを生成
		dt = iso_to_jstdt( record["created"] ) # ISO-8601 拡張フォーマット
		dt = dt.strftime('%Y%m%d_%H%M%S') # 棋譜ファイル名はこのフォーマット

		# game種別変更時の保守性を考え拡張子は考慮せず実装
		# 棋譜ファイル名( 拡張子なし )
		kifNameNoExt = "{}_{}_{}".format(user, game, dt) # "loftkun_shogi10_20180831_180005"のような文字列
		#print("kifNameNoExt={}".format(kifNameNoExt))

		find = False
		for kif in kifList:
			if kif.find(kifNameNoExt) > 0:
				find = True
				break

		if "csaExists" in record:
			csaExists = record["csaExists"]
			if find == csaExists:
				continue

		# 更新
		# csaExistsがない場合は新規追加となる
		gameId = record["id"]
		query = {'id':{ '$eq' : gameId}};
		value = { '$set' : { 'csaExists' : find } };
		col.update(query, value)

		updatedCnt = updatedCnt + 1
	return updatedCnt

if __name__ == '__main__':
	if( len(sys.argv) != 2 ):
		print('usage : clean.py searchPATH')
		sys.exit()
	
	quest = sys.argv[1]
	users = os.listdir(quest)
	users.sort()

	totalUpdateCnt = 0
	for user in users:
		# botは除外
		#if user.startswith(":"):
		#	continue
		path = os.path.join(quest, user)
		if not os.path.isdir(path):
			print("{} is not dir".format(path))
			continue
		updateCnt = checkUser(quest, user)
		totalUpdateCnt = totalUpdateCnt + updateCnt
	print("totalUpdateCnt = {}".format(totalUpdateCnt))


