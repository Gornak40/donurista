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

	def uci(self, inp):
		print('id name Donurista')
		print('id author Gornak40')
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
	Donurista(brpath='/home/gornak40/chess/engines/CiChess_NNUE.sh',
		dbpath='/home/gornak40/chess/engines/donurista.db')