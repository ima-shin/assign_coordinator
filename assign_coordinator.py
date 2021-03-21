from ctypes import windll, Structure, wintypes, byref
from collections import OrderedDict
import sys
import time
import random

random.seed(202103)

GOAL_TAPE_POS = 100

"""
幹事（とか）をちょっとギークな感じで決めたい時に使ってください
"""
class AssignCoordinator(object):

	def __init__(self, member_list):
		# メンバー名のリスト
		self.member_names = member_list
		# 初期値
		self.members_dict = OrderedDict()
		for name in self.member_names:
			self.members_dict[name] = 0

		# 優勝者（番号）
		self.winner = 0

		self.l_list = []

		# メンバー数
		self.member_length = len(self.member_names)
		# 始点x
		self.start_x_pos = max(map(lambda n: len(n), self.member_names)) * 2 + 2

		# カーソル設定インスタンス
		self.cursor_info = CursorUtil()
		# 実行終了後にターミナルの設定をもとに戻すために使用
		self.__default_info = self.cursor_info.ConsoleScreenBufferInfo()
		self.cursor_info.console_info(self.cursor_info.STDOUT_HANDLE, byref(self.__default_info))

	"""初期化"""
	def init_terminal(self):
		sys.stdout.write("\n\n\t\t\t\t\t\t\033[34m幹事\033[31m決め\033[32mレーーーース\033[0m\n\n")
		# sys.stdout.write("\033[34mWHICH \033[31mIS \033[32mTHE \033[35mFASTEST \033[36mPERSON?\033[0m\n\n")

		# 名前のラインアップ
		for name in self.member_names:
			sys.stdout.write(f"{name}\r\033[{self.start_x_pos}C|")
			sys.stdout.write(f"\033[{GOAL_TAPE_POS}C\033[33m|\n\033[0m")

		# エンターキー押下で開始
		sys.stdout.write("\n")
		# sys.stdout.write(input("PRESS ENTER TO START(q to quit)"))
		pressed_key = input("PRESS ENTER TO START(q to quit)")
		if pressed_key == 'q':
			sys.exit(0)
		sys.stdout.write("\033[1A\r\033[0K")

		# 3秒カウントダウン
		for i in reversed(range(0, 4)):
			sys.stdout.write(f"\r{i}")
			time.sleep(1.0)
		sys.stdout.write("\rGO!!!")

	"""乱数を使用してカウントアップ"""
	def start_counting_up(self):
		sys.stdout.write(f"\033[{self.member_length + 1}A")
		while True:
			num = random.randint(0, self.member_length - 1)
			self.l_list.append(num)
			self.members_dict[self.member_names[num]] += 1

			if self.update_terminal(num):
				break

		# 最終行(GO!!!)に移動
		sys.stdout.write(f"\r\033[{self.member_length + 2}B")
		sys.stdout.write(f"\rGOAL!!!\n")
		time.sleep(0.5)

	"""ターミナルの表示を更新"""
	def update_terminal(self, num):
		# 0と1が両方とも"1行下に移動"になっちゃうので、0の場合はそもそも移動しないことにする
		if num > 0:
			sys.stdout.write(f"\033[{num}B")
		sys.stdout.write(f"\r\033[{self.start_x_pos + 1 + self.members_dict[self.member_names[num]]}C=")
		sys.stdout.flush()

		# ゴールテープを切ったら修了
		if self.members_dict[self.member_names[num]] >= GOAL_TAPE_POS:
			self.winner = num
			sys.stdout.write(f"\r\033[33m{self.member_names[num]}\033[0m")
			sys.stdout.write(f"\033[{num}A")
			return True

		if num > 0:
			sys.stdout.write(f"\033[{num}A")

		time.sleep(0.01)

		return False

	"""実行"""
	def run(self):
		try:
			self.init_terminal()
			self.start_counting_up()
			sys.stdout.write(f"\n次の幹事は \033[33m{self.member_names[self.winner]}\033[0m さんに決定しました!!よろしくお願いします!")
			sys.stdout.write("\n\n")

		finally:
			# 設定を初期状態に戻す
			self.cursor_info.set_color(color=self.__default_info.wAttributes)

"""カーソル設定"""
class CursorUtil(object):

	def __init__(self):
		kernel = windll.kernel32
		self.STDOUT_HANDLE = kernel.GetStdHandle(-11)
		self._console_info = kernel.GetConsoleScreenBufferInfo
		self._attribute_info = kernel.SetConsoleTextAttribute

		# コマンドプロンプトのANSI有効化
		kernel.SetConsoleMode(self.STDOUT_HANDLE, 7)

	class ConsoleScreenBufferInfo(Structure):
		_fields_ = [
			("dwSize", wintypes._COORD),
			("dwCursorPosition", wintypes._COORD),
			("wAttributes", wintypes.WORD),
			("srWindow", wintypes.SMALL_RECT),
			("dwMaximumWindowSize", wintypes._COORD)
		]

	@property
	def console_info(self):
		return self._console_info

	@property
	def attribute_info(self):
		return self._attribute_info

	def set_color(self, color):
		self.attribute_info(self.STDOUT_HANDLE, color)


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="幹事決めレース")

	parser.add_argument("members", help="カンマ区切りでメンバーを入力")
	args = parser.parse_args()
	members = args.members.split(',')
	members = list(map(lambda y: y.strip(), members))

	assign_coordinator = AssignCoordinator(member_list=members)
	assign_coordinator.run()
