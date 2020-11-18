#!/usr/bin/python3
from subprocess import Popen, PIPE
from pyfiglet import Figlet
import logging
from chess import Board
from unqlite import UnQLite
from time import time


class Info:
	def __init__(self, info):
		self.info = info
		self.args = info.split()

	def __getattr__(self, attr):
		if attr not in self.args:
			return None
		val = self.args[self.args.index(attr) + 1]
		if val.isdigit():
			val = int(val)
		return val

	def __str__(self):
		return self.info


class Engine:
	def __init__(self, path):
		self.path = path
		self.eng = Popen(path, universal_newlines=True, stdin=PIPE, stdout=PIPE)

	def __del__(self):
		self.eng.kill()

	def write(self, com):
		if not self.eng.stdin:
			raise BrokenPipeError
		self.eng.stdin.write(f'{com}\n')
		self.eng.stdin.flush()

	def readline(self):
		if not self.eng.stdout:
			raise BrokenPipeError
		return self.eng.stdout.readline().strip()

	def isready(self):
		self.write('isready')
		while True:
			if self.readline() == 'readyok':
				return

	def readfor(self, func):
		res = list()
		while True:
			text = self.readline()
			res.append(text)
			if func(text):
				return res


class Donurista:
	def __init__(self, brpath, dbpath):
		self.br = Engine(brpath)
		# fucking cute chess
		self.br.write('setoption name Threads value 3')
		self.br.write('setoption name Hash value 4096')
		# fucking cute chess
		self.db = UnQLite(dbpath)
		self.board = Board()
		self.func_book = {
			'uci': self.uci,
			'isready': self.isready,
			'go': self.go,
			'quit': self.quit,
			'position': self.position
		}
		self.hello()
		try:
			self.start()
		except KeyboardInterrupt:
			self.quit(None)

	def simple(self, inp):
		self.br.write(inp)

	def uci(self, inp): # TODO: normal options
		print('id name Donurista')
		print('id author Gornak40')
		print('option name Debug Log File type string default') 
		print('option name Contempt type spin default 24 min -100 max 100')
		print('option name Analysis Contempt type combo default Both var Off var White var Black var Both')
		print('option name Threads type spin default 1 min 1 max 512')
		print('option name Hash type spin default 16 min 1 max 33554432')
		print('option name Clear Hash type button')
		print('option name Ponder type check default false')
		print('option name MultiPV type spin default 1 min 1 max 500')
		print('option name Skill Level type spin default 20 min 0 max 20')
		print('option name Move Overhead type spin default 10 min 0 max 5000')
		print('option name Slow Mover type spin default 100 min 10 max 1000')
		print('option name nodestime type spin default 0 min 0 max 10000')
		print('option name UCI_Chess960 type check default false')
		print('option name UCI_AnalyseMode type check default false')
		print('option name UCI_LimitStrength type check default false')
		print('option name UCI_Elo type spin default 1350 min 1350 max 2850')
		print('option name UCI_ShowWDL type check default false')
		print('option name SyzygyPath type string default <empty>')
		print('option name SyzygyProbeDepth type spin default 1 min 1 max 100')
		print('option name Syzygy50MoveRule type check default true')
		print('option name SyzygyProbeLimit type spin default 7 min 0 max 7')
		print('option name Use NNUE type check default true')
		print('option name EvalFile type string default nn-82215d0fd0df.nnue')
		print('uciok')

	def isready(self, inp):
		print('readyok')

	def is_cached(self): # TODO: ARGS MODIFICATION
		return False

	def write_db(self, info, bestmove):
		data = f'{info.depth};{bestmove.bestmove}'
		with self.db.transaction():
			self.db[self.board.fen()] = data

	def go(self, inp):
		fen = self.board.fen()
		db_depth = 0
		T = time()
		if fen in self.db:
			logging.info('[+] update db') # testing feature
			db_depth, db_move = self.db[fen].decode('utf-8').split(';')
			db_depth = int(db_depth)
			if self.is_cached():
				print('info smart cache moves')
				print(f'bestmove {db_move}')
				return
		T = time() - T
		logging.info(f'[+] db timing {T}')
		self.br.write(inp)
		br_pred = self.br.readfor(lambda x: 'bestmove' in x)
		info = Info(br_pred[-2])
		bestmove = Info(br_pred[-1])
		if info.depth > db_depth:
			self.write_db(info, bestmove)
		logging.info(f'[+] db size {len(self.db)}')
		print(info)
		print(bestmove)

	def position(self, inp):
		self.br.write(inp)
		self.board = Board()
		for token in inp.split():
			if token in {'startpos', 'position', 'moves'}:
				continue
			self.board.push_san(token)

	def start(self):
		while True:
			inp = input()
			if not inp:
				continue
			logging.info(inp)
			com = inp.split()[0]
			func = self.func_book.get(com, self.simple)
			self.br.isready()
			func(inp)

	def hello(self):
		F = Figlet()
		text = F.renderText('Donurista')
		print(text)

	def quit(self, inp):
		logging.info('[+] ENGINE TERMINATED')
		del self.br
		self.db.close()
		exit(0)


if __name__ == '__main__':
	logging.basicConfig(filename='donurista.log', level=logging.INFO)
	logging.info('[+] ENGINE STARTED')
	Donurista(brpath='/home/gornak40/chess/engines/stockfish_20090216_x64_avx2',
		dbpath='/home/gornak40/chess/engines/donurista.db')