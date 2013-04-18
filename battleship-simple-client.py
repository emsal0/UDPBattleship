#!/usr/bin/env python
from fltk import *
import socket, sys

class Battleship(Fl_Window):
	def __init__(self,x,y,w,h,label,gn):
		Fl_Window.__init__(self,x,y,w,h,label)
		#self.can = False
		self.state = "placing"
		self.csock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.BPORT=9999
		while True:
			try:
				self.csock.bind(('',self.BPORT))
				break
			except:
				self.BPORT+=1
		self.host = sys.argv[1]
		self.port = int(sys.argv[2])
		self.enemy_arr=[]
		self.my_arr=[]
		self.gamename=gn.strip()

		self.placements = []
		
		self.ships = []
		self.csock.sendto("INIT "+str(self.BPORT), (self.host,self.port))
		self.csock.sendto("REQGAMENAME "+self.gamename, (self.host,self.port))
		self.begin()
		
		for enemy_y in range(10):
			for enemy_x in range(10):
				self.enemy_arr.append(Fl_Button(25+20*enemy_x,25+20*enemy_y,20,20))
				self.enemy_arr[-1].callback(self.attack)
		
		for my_y in range(10):
			for my_x in range(10):
				self.my_arr.append(Fl_Button(25+20*my_x,25+240+20*my_y,20,20))
				self.my_arr[-1].callback(self.place)
		
		self.end()
		self.cfd = self.csock.fileno()
		Fl.add_fd(self.cfd,self.receive_data)
		#self.callback(self.close)
		
	def attack(self,w):
		print self.can, self.state
		if self.can == True and self.state == "attacking":
			ind = self.enemy_arr.index(w)
			self.csock.sendto("GAMEMOVE "+self.gamename+"\t"+str(ind),(self.host,self.port))
			self.state = "sitting"
			

	def place(self,w):
		if self.state == "placing":
			ind = self.my_arr.index(w)
			if self.ships.__len__() < 17:
				if w.color() != FL_BLUE:
					self.ships.append(ind)
					w.color(FL_BLUE)	
				else:
					pass
				if self.ships.__len__() == 17:
					self.state="waiting"
					self.csock.sendto("JOINGAME "+self.gamename.strip(),(self.host,self.port))

					
	def receive_data(self,fd):
		self.data,self.d=self.csock.recvfrom(65536)
		print self.data
		com = self.data.split(' ')
		
		if self.data in ["YES", "NO"]:
			if self.data=="NO":
				self.csock.sendto("INITGAME "+self.gamename.strip(),(self.host,self.port))
			
		if ' '.join(self.data.split(' ')[:2]) == "JOINED GAME":
			if self.data.split(' ')[2] == '0':
				self.state = "attacking"
			else:
				self.state = "sitting"
			print self.state, self.can
		if self.data == 'GAMESTART':
			self.can = True
		if com[0] == "MOVE":
			if self.can == True:
				if com[1] not in ["HIT", "MISSED"]:
					num = int(com[1])
					if self.my_arr[num].color() == FL_BLUE:
						self.my_arr[num].color(FL_RED)
						self.my_arr[num].deactivate()
						self.csock.sendto("GAMEMOVE "+self.gamename+"\t"+"HIT "+str(num), (self.host,self.port))
					else:
						self.my_arr[num].color(FL_BLACK)
						self.csock.sendto("GAMEMOVE "+self.gamename+"\t"+"MISSED "+str(num), (self.host,self.port))
					self.state = "attacking"
					self.my_arr[num].redraw()
				else:
					csq = int(com[2])
					if com[1] == "MISSED":
						self.enemy_arr[csq].color(FL_BLACK)
					elif com[1] == "HIT":
						self.enemy_arr[csq].color(FL_RED)
						self.enemy_arr[csq].deactivate()
					self.state = "sitting"
					self.enemy_arr[csq].redraw()
		print self.can

	def close(self,w):
		try:
			self.csock.sendto("LEFT "+self.gamename,(self.host,self.port))
		except:
			pass
		self.csock.close()
		w.hide()
		Fl_Window.__del__(self)

ss = Battleship(0,0,250,475,"Ss", sys.argv[3])
ss.show()
Fl.run()
