#!/usr/bin/python3
import chess
import chess.engine
import logging
from pyfiglet import Figlet
from math import inf


class Times:
	def __init__(self, *args):
		args = list(args)
		self.kwargs = dict()
		for i in range(1, len(args), 2):
			self.kwargs[args[i - 1]] = float(args[i])

	def __getattr__(self, attr):
		return self.kwargs.get(attr)

	def get_limit(self, k=1):
		k *= 1e3
		if self.movetime:
			L = chess.engine.Limit(time=self.movetime / k)
		else:
			wtime, btime, winc, binc = self.wtime / k, self.btime / k, self.winc / k, self.binc / k
			L = chess.engine.Limit(white_clock=wtime, black_clock=btime, white_inc=winc, black_inc=binc)
		return L


class Info:
	def __init__(self, kwargs):
		self.kwargs = kwargs

	def __getattr__(self, attr):
		return self.kwargs.get(attr)

	def get_weight(self):
		score = self.score
		if score.is_mate():
			return inf
		score = int(str(score.relative))
		return score


class Donurista:
	def __init__(self, brpath, nnpath, bropt, nnopt):
		self.hello()
		self.brpath = brpath
		self.nnpath = nnpath
		self.bropt = bropt
		self.nnopt = nnopt
		self.ucinewgame()
		try:
			self.start()
		except KeyboardInterrupt:
			self.quit()

	def start(self):
		while True:
			inp = input()
			logging.info(inp)
			inp = inp.split()
			if not inp:
				continue
			com = inp.pop(0)
			func = self.func_book.get(com)
			if func is None:
				continue
			func(*inp)

	def quit(self, *args):
		print('\nGO TO SLEEP!')
		self.br.quit()
		self.nn.quit()
		exit()

	def uci(self, *args):
		print('id name Donurista')
		print('id author Gornak40')
		print('uciok')

	def isready(self, *args):
		print('readyok')

	def ucinewgame(self, *args):
		self.board = chess.Board()
		self.br_options = dict()
		self.nn_options = dict()
		self.br = chess.engine.SimpleEngine.popen_uci(self.brpath)
		self.nn = chess.engine.SimpleEngine.popen_uci(self.nnpath)
		self.prev_br = 0
		self.prev_nn = 0
		self.func_book = {
			'uci': self.uci,
			'isready': self.isready,
			'ucinewgame': self.ucinewgame,
			'position': self.position,
			'go': self.go,
			'quit': self.quit,
			'setoption': self.setoption
		}

	def position(self, *args):
		self.board = chess.Board()
		for pos in args:
			if pos != 'moves' and pos != 'startpos':
				self.board.push_san(pos)

	def go(self, *args):
		T = Times(*args)
		L = T.get_limit(3)
		info_br = self.analyse(self.br, L)
		info_nn = self.analyse(self.nn, L)
		score_br = info_br.get_weight()
		score_nn = info_nn.get_weight()
		dlt_br = score_br - self.prev_br
		dlt_nn = score_nn - self.prev_nn
		logging.info('[info br] ' + str(info_br.score))
		logging.info('[info nn] ' + str(info_nn.score))
		if dlt_br >= dlt_nn:
			move = self.best_move(self.br, L)
			self.show_info(info_br)
			logging.info('[go br]')
		else:
			move = self.best_move(self.nn, L)
			self.show_info(info_nn)
			logging.info('[go nn]')
		self.prev_br = score_br
		self.prev_nn = score_nn	
		self.board.push(move.move)
		print('bestmove {}'.format(move.move))

	def show_info(self, info):
		depth, seldepth, multipv = info.depth, info.seldepth, info.multipv
		score = 'cp ' + str(info.score.relative) if not info.score.is_mate() else 'mate ' + str(info.score.relative)[1:]
		nodes, nps, tbhits = info.nodes, info.nps, info.tbhits
		time = int(info.time * 1e3)
		print('info depth {} seldepth {} multipv {} score {} nodes {} nps {} tbhits {} time {}'.format(
			depth, seldepth, multipv, score, nodes, nps, tbhits, time))

	def analyse(self, eng, L):
		info = eng.analyse(self.board, L)
		return Info(info)

	def best_move(self, eng, L):
		move = eng.play(self.board, L)
		return move

	def setoption(self, *args):
		args = list(args)
		args.pop(0)
		name = ' '.join(args[:args.index('value')])
		value = ' '.join(args[args.index('value') + 1:])
		if value.isdigit():
			value = int(value)
		elif value == 'false':
			value = False
		elif value == 'true':
			value = True
		if name in self.bropt:
			self.br_options[name] = value
			self.br.configure(self.br_options)
			logging.info('[bropt] ' + name + ':' + str(value))
		if name in self.nnopt:
			self.nn_options[name] = value
			self.nn.configure(self.nn_options)
			logging.info('[nnopt] ' + name + ':' + str(value))

	def hello(self):
		F = Figlet()
		text = F.renderText('Donurista')
		print(text)


if __name__ == '__main__':
	logging.basicConfig(filename='donurista.log', level=logging.INFO)
	logging.info('Im running, bitch!')
	Donurista(brpath='/home/gornak40/chess/engines/CiChess', 
		nnpath='/home/gornak40/chess/engines/stockfish_20090216_x64_avx2',
		bropt={'Hash', 'Threads', 'Move Overhead', 'SyzygyPath'}, 
		nnopt={'Hash', 'Threads', 'Move Overhead', 'SyzygyPath'})