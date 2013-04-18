#!/usr/bin/env python
from select import select
import socket,sys

HOST=''
try:
	PORT=int(sys.argv[1])
except:
	PORT=9000
serv=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serv.bind((HOST,PORT))

users={}
games={}

def run():
	global serv
	global games, users
	
	gamename=''
	enemy = None
	
	data,addr=serv.recvfrom(65536)
	
	print data
	
	com = data.split(' ')
	
	if com[0] == 'INIT':
		users[addr] = int(com[1])
	
	if com[0] == 'REQGAMENAME':
		if ' '.join(com[1:]) in games:
			serv.sendto("YES",(addr[0],users[addr]))
		else:
			serv.sendto("NO",(addr[0],users[addr]))
	
	if com[0] == 'INITGAME':
		gamename=' '.join(com[1:])
		if gamename not in games:
			games[gamename] = []
		else:
			serv.sendto("GAME ALREADY EXISTING",(addr[0],users[addr]))
	
	if com[0] == 'JOINGAME':
		gamename = ' '.join(com[1:])
		if len(games[gamename]) < 2:
			serv.sendto("JOINED GAME "+str(len(games[gamename])),(addr[0],users[addr]))
			games[gamename].append(addr)
		else:
			serv.sendto("GAME FULL",(addr[0],users[addr]))
		if len(games[gamename]) == 2:
			for i in games[gamename]:
				serv.sendto("GAMESTART", (i[0],i[1]))
		
	if com[0] == 'GAMEMOVE':
		gamename = ' '.join(com[1:])
		delim = '\t'
		move = gamename[gamename.find(delim)+len(delim):]
		gamename = gamename[:gamename.find(delim)]
		for i in games[gamename]:
			if i!=addr:
				enemy=i
		serv.sendto('MOVE '+move,(enemy[0],users[enemy]))
	if com[0] == 'LEFT':
		gamename=com[1]
		games[gamename].remove(addr)
	print games
if __name__ == '__main__':
	while True:
		run()
	serv.close()
