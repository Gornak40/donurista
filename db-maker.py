#!/usr/bin/python3
from unqlite import UnQLite
dbr = UnQLite('donurista.db')
dbw = UnQLite('new.db')

for fen, info in dbr:
	info = info.decode('utf-8')
	fen = ' '.join(fen.split()[:-2])
	dbw[fen] = info
	print(fen)

dbr.close()
dbw.close()