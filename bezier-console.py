#!/usr/bin/env python 
# -*- coding: utf-8 -*-

################################################################################
# Besier-console is a "console" comands based extension to create besier paths 
# with exact dimensions.
#
# Syntax:
#	command[; command]
# Command:
#	type  [parameters]; 
#	Types:
#		a (arc)	
#		l (line)
#		h (hline)
#		v (vline)
#		m (move)
#	Parameters :
#		l - length
#		a - angle
#		x,y - coordinates
#		all values are relative if the case is lover to use absolute coordinates use upper case.
################################################################################

from csp import CSP, CSPsubpath
from points import P
from math import *
import inkex
import re
import sys
import traceback
from biarc import Arc, Line

def warn(s) :
	if bezier_console.options.silent : return
	s = str(s)
	inkex.errormsg(s+"\n")		
	
def error(s) :
	if bezier_console.options.silent : return
	s = str(s)
	inkex.errormsg(s+"\n")		
	sys.exit()

class BezierConsole(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("", "--string",					action="store", type="string", 		dest="s", default="",					help="Draw string")
		self.OptionParser.add_option("", "--silent",					action="store", type="inkbool", 	dest="silent", default=True,				help="Do not show an errors, usable for live preview")
		self.OptionParser.add_option("",   "--units",					action="store", type="float", 		dest="units", default="3.543307",		help="Units scale")		
	def get_line_xy(self,x,y,a,l) :
		x1,y1 = self.p.x,self.p.y
		#warn((x,y,a,l))
		if x==None : 
			if y != None :
				if a!=None : 
					a = tan(a)
					if abs(a)>16331778728300000 :
						return P(x1,y)
					if a == 0 : 
						error("Bad param a=0 for y defined line. Command: %s"%self.command)
					return x1+(y-y1)/a,y
				elif l!=None :
					try :
						x = sqrt(l**2 - (y-y1)**2)	
					except :
						error("Bad params, l to small. Command: %s"%self.command)	
					return P(x,y)	
				else :
					return P(x1,y)
								
			else : 
				if a!=None and l!=None :
					return  self.p+P(cos(a),sin(a))*l 
		else : 
			if y!=None :
				return P(x,y)
			else :
				if a!=None :
					a = tan(a)
					if abs(a)>16331778728300000 :
						error("Bad param a=pi/2 for x defined line. Command: %s"%self.command)
					else: 
						return x, a*(x-x1) + y1 
						
				elif l!=None :
					try :
						y = sqrt(l**2 - (x-x1)**2)	
					except :
						error("Bad params, l to small. Command: %s"%self.command)	
				else : 
					return P(x,y1)	
					
		error("""Bad params for the line. Command: %s\n
					x = %s,
					y = %s,
					a = %s,
					l = %s
				"""%(self.command,x,y,a,l))						
		
	def draw_line(self,x,y,a,l) : 
		p1 = self.get_line_xy(x,y,a,l)
		self.path.join( CSP([[[self.p,self.p,self.p],[p1,p1,p1]]]) )
		

	def move_to(self,x,y,a,l) :
		p1 = self.get_line_xy(x,y,a,l)
		self.path.items.append(CSPSubpath([[p1,p1,p1]])) 

	def arc_on_two_points_and_slope(self,st,end,slope) :
		# find the center 
		m = (end - st)/2
		n = slope.ccw()
		# get the intersection of lines throught st and m normal to slope and st-end line
		l1 = Line(st,st+n)
		l2 = Line(st+m,st+m+m.ccw())
		p = l1.intersect(l2,True) 
		if len(p)!=1 : 
			warn((p,l1,l2,slope))
			error("Bad parameters for arc on two points. Command: %s"%self.command)
		c = p[0]
		a = (st-c).cross(slope)
		return Arc(st,end,c,a)		 
		
	def get_arg_comb(self,s,args):
		s = list(s)
		args = {"x":x,"y":y,"a":a,"r":r,"i":i,"j":j,"l":l}
		for i in args:
			if (args[i] == None and i in s or
			    args[i] != None and i not in s) :
			    return False
		return True	
		
	def get_arc_param(self,x,y,a,r,i,j,l) :
		st = self.p
		c = None
		# asume not enought params use slope. 
		if x !=None or y!=None:
			# using two points and slope.
			end = P(x if x!=None else self.p.x, y if y!=None else self.p.y)
			return self.arc_on_two_points_and_slope(self.p,end,self.slope)
		
		if a != None :
			if l !=None : 
				r = l/a/2
			if r != None :
				c = self.p+self.slope.ccw()*r
			if i != None or j != None : 	
				c = P(i if i!=None else self.p.x, j if j!=None else self.p.y)
			if c != None :	
				end = (self.p - c).rotate(a) + c
				return self.arc_on_two_points_and_slope(self.p,end,self.slope)
		
		if l != None :
			if i != None or j != None : 	
				c = P(i if i!=None else self.p.x, j if j!=None else self.p.y)
				r = (self.p - c).mag()
			if r != None :
				a = l/r/2
				return self.get_arc_param(None, None, a, r, None, None, None)
		
		error("To few parametersfor arc. Command: %s"%self.command) 

		
	def draw_arc(self,x,y,a,r,i,j,l) :
		st = self.p
		arc = self.get_arc_param(x,y,a,r,i,j,l)
		#warn(arc)
		self.path.join(arc.to_csp())
		
	def parse_command(self, command) :
		if command.strip() == "" : return
		self.command = command
		r = re.match("\s*([almhvALMHV]?)\s*((\s*[alxyrijdALXYRIJD]\s*\-?[\d\.]+)*)\s*", command) 
		if not r: 
			error("Cannot parse command: \"%s\""% command)
			
		r = re.match("\s*([almhvALMHV])\s*([alxyrijdALXYRIJD].*)", command)
		if r :
			warn(r.groups())
			t, command = r.groups()
		else :
			t = self.last_command
		 
		# parse the parameters 
		x,y,a,l,r,i,j = None, None, None, None, None, None, None
		try:
			self.slope = self.path.slope(-1,-1,1)
		except: 
			self.slope = P(1.,0.)	
		for p in re.findall("([alxyrijALXYRIJ])\s*(\-?\d*\.?\d*)", command) :
			#warn(p)				
			p = list(p)
			if p[0] == "A" : a = -float(p[1])/180*pi
			elif p[0] == "a" : a = self.slope.angle() -float(p[1])/180*pi
			else :	p[1] = float(p[1])*self.options.units
			if   p[0] == "x" : x = self.p.x + p[1]
			elif p[0] == "X" : x = p[1]
			elif p[0] == "y" : y = self.p.y - p[1]
			elif p[0] == "Y" : y = - p[1]
			elif p[0] == "i" : i = self.p.x + p[1]
			elif p[0] == "I" : I = p[1]
			elif p[0] == "j" : j = self.p.y - p[1]
			elif p[0] == "J" : J = -p[1]
			elif p[0] in ("r","R") : r = p[1]
			elif p[0] in ("d","D") : r = p[1]/2
			elif p[0] in ("l","L") : l = p[1]
			
		# exec command
		if t in ("l","L") : self.draw_line(x,y,a,l)
		if t in ("a","A") : self.draw_arc(x,y,a,r,i,j,l)
		if t in ("m","M") : self.move_to(x,y,a,l)
		self.last_command = t

	def effect(self) :
		if self.options.silent :
			try :
				self.run()
			except :
				pass
		else :
			self.run()
			
	def run(self) :		
			s = self.options.s.split(";")
			node = None
			
			if len(self.selected) > 0 :
				node = self.selected.itervalues().next()
				if node.tag == '{http://www.w3.org/2000/svg}path' :
					self.path = CSP(node)
				else : 
					error("Select a path or select nothing to create new path!")
		
			try :
				self.p = self.path.items[-1].points[-1][1]
			except :
				self.path = CSP( [[[P(self.view_center),P(self.view_center),P(self.view_center)]]], clean=False)
				self.p = self.path.items[-1].points[-1][1]
				
			self.last_command = None
			for a in s :
				self.parse_command(a)
				try :
					self.p = self.path.items[-1].points[-1][1]
				except :
					pass

			if node == None : self.path.draw(group = self.current_layer) 
			else :	node.set("d",self.path.to_string())
		
		
bezier_console = BezierConsole()
bezier_console.affect()					

