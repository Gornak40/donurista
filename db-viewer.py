#!/usr/bin/python3
from unqlite import UnQLite
from prettytable import PrettyTable
from argparse import ArgumentParser


def print_all():
	P = PrettyTable(['#', 'Fen', 'Depth', 'Move'])
	for i, (fen, info) in enumerate(db):
		info = info.decode('utf-8')
		depth, move = info.split(';')
		P.add_row([i + 1, fen, depth, move])
	print(P)


parser = ArgumentParser(description='Donurista quick DB viewer')
parser.add_argument('--all', '-a', action='store_const', help='print all positions (long time)', const=True, default=False)
db = UnQLite('new.db')
args = parser.parse_args()
if args.all:
	print_all()
else:
	print(len(db))
db.close()