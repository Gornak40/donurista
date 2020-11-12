#!/usr/bin/python3
from unqlite import UnQLite
from prettytable import PrettyTable


P = PrettyTable(['#', 'Fen', 'Depth', 'Move'])
db = UnQLite('donurista.db')
for i, (fen, info) in enumerate(db):
	info = info.decode('utf-8')
	depth, move = info.split(';')
	P.add_row([i + 1, fen, depth, move])
db.close()
print(P)