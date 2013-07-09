from points import P
from math import *
import inkex
from csp import CSP, CSPsubpath
pi2 = pi*2

################################################################################
###		Biarc classes - Arc, Line and Biarc
################################################################################
class Arc():
	def __init__(self,st,end,c,a,r=None) :
		#debugger.add_debugger_to_class(self.__class__)
		# a - arc's angle, it's not defining actual angle before now, but defines direction so it's value does not mather matters only the sign.
		if st.__class__ == P :  st = st.to_list()
		if end.__class__ == P : end = end.to_list()
		if c.__class__ == P :   c = c.to_list()
		self.st = P(st)
		self.end = P(end)
		self.c = P(c)
		if r == None : self.r = (P(st)-P(c)).mag()
		else: self.r = r
		self.a = ( (self.st-self.c).angle() - (self.end-self.c).angle() ) % pi2
		if a>0 : self.a -= pi2
		self.a *= -1.
		self.cp = (self.st-self.c).rot(self.a/2)+self.c # central point of an arc

	def __repr__(self) :
		return "Arc: s%s e%s c%s r%.2f a%.2f (l=%.3f) " % (self.st,self.end,self.c,self.r,self.a,self.length())

	def copy(self) :
		return Arc(self.st,self.end,self.c,self.a,self.r)	

	def to_csp(self) :
		# Taken from cubicsuperpath's ArcToCsp	
		O = self.c
		sectors = int(abs(self.a)*2/pi)+1
		da = self.a/sectors
		v = 4*tan(da/4)/3
		angle = (self.st-self.c).angle()
		cspsubpath = CSPsubpath()
		for i in range(sectors+1) :
			c,s = cos(angle)*self.r, sin(angle)*self.r
			v1=P([O.x+c - (-v)*s,	O.y+s + (-v)*c])
			pt=P([O.x+c,			O.y+s])
			v2=P([O.x+c - v*s,		O.y+s + v*c])
			cspsubpath.points.append([v1,pt,v2])
			angle += da 
		cspsubpath.points[0][0] = cspsubpath.points[0][1].copy()
		cspsubpath.points[-1][2] = cspsubpath.points[-1][1].copy()
		csp = CSP()	
		csp.items.append(cspsubpath)
		return csp 
		
	def rebuild(self,st=None,end=None,c=None,a=None,r=None) : 
		if st==None: st=self.st
		if end==None: end=self.end
		if c==None: c=self.c
		if a==None: a=self.a
		if r==None: r=self.r
		self.__init__(st,end,c,a,r)

	def get_t_at_point(self, p, y=None) :
		if y!=None : p = P(p,y)
		if not self.point_inside_angle(p) : return -1.
		return abs( acos( (self.st-self.c).dot((p-self.c))/(self.r**2) )/pi ) # consuming all arcs les than 180 deg

		
	def point_inside_angle(self,p,y=None) :  # TODO need to be done faster! 
		if y!=None : p = P(p,y)
		if (p-self.c).l2() != self.r**2 :  # p is not on the arc, lets move it there
			p = self.c+(p-self.c).unit()*self.r
		warn( (self.cp-self.c).dot(p-self.c),self.r**2, (self.cp-self.c).dot(p-self.c)/self.r**2)
		try:
			abs(  acos( (self.cp-self.c).dot(p-self.c) /self.r**2  )  )  <  abs(self.a/2)
		except :
			self.draw()
			return True	 
		return abs(  acos( (self.cp-self.c).dot(p-self.c) /self.r**2  )  )  <  abs(self.a/2) 

	def bounds(self) : 
		# first get bounds of start/end 
		x1,y1, x2,y2 =  ( min(self.st.x,self.end.x),min(self.st.y,self.end.y),
						  max(self.st.x,self.end.x),max(self.st.y,self.end.y) )
		# Then check 0,pi/2,pi and 2pi angles. 
		if self.point_Gde_angle(self.c+P(0,self.r)) :
			y2 = max(y2, self.c.y+self.r)
		if self.point_inside_angle(self.c+P(0,-self.r)) :
			y1 = min(y1, self.c.y-self.r)
		if self.point_inside_angle(self.c+P(-self.r,0)) :
			x1 = min(x1, self.c.x-self.r)
		if self.point_inside_angle(self.c+P(self.r,0)) :
			x2 = max(x2, self.c.x+self.r)
		return x1,y1, x2,y2

	def head(self,p):
		self.rebuild(end=p)

	def tail(self,p):
		self.rebuild(st=p)

	def offset(self, r):
		oldr = self.r
		if self.a>0 :
			self.r = self.r + r
		else :
			self.r = self.r - r
		
		if self.r != 0 :
			self.st = self.c + (self.st-self.c)*self.r/oldr
			self.end = self.c + (self.end-self.c)*self.r/oldr
		self.rebuild()	
			
	def length(self):
		return abs(self.a*self.r)
	

	def draw(self, group=None, style=None, layer=None, transform=None, num = 0, reverse_angle = None, color=None, width=None):
		layer, group, transform, reverse_angle = gcodetools.get_preview_group(layer, group, transform)
		st = P(gcodetools.transform(self.st.to_list(), layer, True))
		c = P(gcodetools.transform(self.c.to_list(), layer, True))
		a = self.a * reverse_angle
		r = (st-c)
		a_st = ((st-c).angle()-pi/2)%(pi*2)+pi/2
		r = r.mag()
		if a>0:
			a_end = a_st+a
			reverse=False
		else: 
			a_end = a_st
			a_st = a_st+a
			reverse=True
		
		attr = {
				'style': get_style("biarc", i=num, name=style, reverse=reverse, width=width, color=color),
				 inkex.addNS('cx','sodipodi'):		str(c.x),
				 inkex.addNS('cy','sodipodi'):		str(c.y),
				 inkex.addNS('rx','sodipodi'):		str(r),
				 inkex.addNS('ry','sodipodi'):		str(r),
				 inkex.addNS('start','sodipodi'):	str(a_st),
				 inkex.addNS('end','sodipodi'):		str(a_end),
				 inkex.addNS('open','sodipodi'):	'true',
				 inkex.addNS('type','sodipodi'):	'arc',
				 "gcodetools": "Preview %s"%self,
				}	
		if transform != [] :
			attr["transform"] = transform	
		inkex.etree.SubElement(	group, inkex.addNS('path','svg'), attr)
	
	def check_intersection(self, points): 
		res = []
 		for p in points :
 			if self.point_inside_angle(p) :
 				res.append(p)
		return res		
		
	def intersect(self,b) :
		if b.__class__ == Line :
			return b.intersect(self)
		else : 
			# taken from http://paulbourke.net/geometry/2circle/
			if (self.st-b.st).l2()<1e-10 and (self.end-b.end).l2()<1e-10 : return [self.st,self.end]
			r0 = self.r 
			r1 = b.r
			P0 = self.c
			P1 = b.c
			d2 = (P0-P1).l2() 
			d = sqrt(d2)
			if d>r0+r1  or r0+r1<=0 or d2<(r0-r1)**2 :
				return []
			if d2==0 and r0==r1 :
				return self.check_intersection( b.check_intersection(
					[self.st, self.end, b.st, b.end] ) )
			if d == r0+r1  :
				return self.check_intersection( b.check_intersection(
								[P0 + (P1 - P0)*r0/(r0+r1)]  ) )
			else: 
				a = (r0**2 - r1**2 + d2)/(2.*d)
				P2 = P0 + a*(P1-P0)/d
				h = r0**2-a**2
				h = sqrt(h) if h>0 else 0. 
				return self.check_intersection(b.check_intersection( [
							P([P2.x+h*(P1.y-P0.y)/d, P2.y-h*(P1.x-P0.x)/d]),
							P([P2.x-h*(P1.y-P0.y)/d, P2.y+h*(P1.x-P0.x)/d]),
						] ))

	def point_d2(self, p):
		if self.point_inside_angle(p) :
			l = (p-self.c).mag()
			if l == 0 : return self.r**2
			else : return ((p-self.c)*(1 - self.r/l)).l2()
		else :
			return min( (p-self.st).l2(), (p-self.end).l2() )	

				
				
			
class Line():

	def __init__(self,st,end):
		#debugger.add_debugger_to_class(self.__class__)
		if st.__class__ == P :  st = st.to_list()
		if end.__class__ == P :	end = end.to_list()
		self.st = P(st)
		self.end = P(end)
		self.l = self.length() 
		if self.l != 0 :
			self.n = ((self.end-self.st)/self.l).ccw()
		else: 
			self.n = [0,1]
	
	def get_t_at_point(self,p) :
		if self.st.x-self.end.x != 0 :
			return (self.st.x-p.x)/(self.st.x-self.end.x)
		else :
			return (self.st.y-p.y)/(self.st.y-self.end.y)
			
	def __repr__(self) :
		return "Line: %s %s (l=.3%f) " % (self.st,self.end,self.l)
				
	def copy(self) : 
		return Line(self.st,self.end)
	
	def rebuild(self,st=None,end=None) : 
		if st==None: st=self.st
		if end==None: end=self.end
		self.__init__(st,end)
	
	def bounds(self) :
		return  ( min(self.st.x,self.end.x),min(self.st.y,self.end.y),
				  max(self.st.x,self.end.x),max(self.st.y,self.end.y) )
	
	def head(self,p):
		self.rebuild(end=p)

	def tail(self,p):
		self.rebuild(st=p)

	def offset(self, r):
		self.st -= self.n*r
		self.end -= self.n*r
		self.rebuild()
		
	def l2(self): return (self.st-self.end).l2()
	def length(self): return (self.st-self.end).mag()
	
	def draw(self, group=None, style=None, layer=None, transform=None, num = 0, reverse_angle = None, color = None, width=None) :
		layer, group, transform, reverse_angle = gcodetools.get_preview_group(layer, group, transform, reverse_angle)
		st = gcodetools.transform(self.st.to_list(), layer, True)
		end = gcodetools.transform(self.end.to_list(), layer, True)

		attr = {	'style': get_style('line', name=style, width=width, color=color),
					'd':'M %s,%s L %s,%s' % (st[0],st[1],end[0],end[1]),
					"gcodetools": "Preview %s"%self,
				}
		if transform != [] :
			attr["transform"] = transform		
		inkex.etree.SubElement(	group, inkex.addNS('path','svg'),  attr	)
	
	def intersect(self,b, false_intersection = False) :
		if b.__class__ == Line :
			if self.l < 10e-8 or b.l < 10e-8 : return []
			v1 = self.end - self.st
			v2 = b.end - b.st
			x = v1.x*v2.y - v2.x*v1.y 
			if x == 0 :
				# lines are parallel
				res = []

				if (self.st.x-b.st.x)*v1.y - (self.st.y-b.st.y)*v1.x  == 0:
					# lines are the same
					if v1.x != 0 :
						if 0<=(self.st.x-b.st.x)/v2.x<=1 :  res.append(self.st)
						if 0<=(self.end.x-b.st.x)/v2.x<=1 :  res.append(self.end)
						if 0<=(b.st.x-self.st.x)/v1.x<=1 :  res.append(b.st)
						if 0<=(b.end.x-b.st.x)/v1.x<=1 :  res.append(b.end)
					else :
						if 0<=(self.st.y-b.st.y)/v2.y<=1 :  res.append(self.st)
						if 0<=(self.end.y-b.st.y)/v2.y<=1 :  res.append(self.end)
						if 0<=(b.st.y-self.st.y)/v1.y<=1 :  res.append(b.st)
						if 0<=(b.end.y-b.st.y)/v1.y<=1 :  res.append(b.end)
				return res
			else :
				t1 = ( v2.x*(self.st.y-b.st.y) - v2.y*(self.st.x-b.st.x) ) / x
				t2 = ( v1.x*(self.st.y-b.st.y) - v1.y*(self.st.x-b.st.x) ) / x
				
				if 0<=t1<=1 and 0<=t2<=1 or false_intersection : return [ self.st+v1*t1 ]	
				else : return []					
		else: 
			# taken from http://mathworld.wolfram.com/Circle-LineIntersection.html
			x1 = self.st.x - b.c.x
			x2 = self.end.x - b.c.x
			y1 = self.st.y - b.c.y
			y2 = self.end.y - b.c.y
			dx = x2-x1
			dy = y2-y1
			D = x1*y2-x2*y1
			dr = dx*dx+dy*dy
			descr = b.r**2*dr-D*D
			if descr<0 : return []
			if descr==0 : return self.check_intersection(b.check_intersection([ P([D*dy/dr+b.c.x,-D*dx/dr+b.c.y]) ]))
			sign = -1. if dy<0 else 1.
			descr = sqrt(descr)
			points = [
						 P( [ (D*dy+sign*dx*descr)/dr+b.c.x, (-D*dx+abs(dy)*descr)/dr+b.c.y ] ), 
						 P( [ (D*dy-sign*dx*descr)/dr+b.c.x, (-D*dx-abs(dy)*descr)/dr+b.c.y ] )
					]
			if false_intersection :
				return points
			else: 
				return self.check_intersection(b.check_intersection( points ))
							

	def check_intersection(self, points):
		res = []
		for p in points :
			if ((self.st.x-1e-7<=p.x<=self.end.x+1e-7 or self.end.x-1e-7<=p.x<=self.st.x+1e-7)
				and 
				(self.st.y-1e-7<=p.y<=self.end.y+1e-7 or self.end.y-1e-7<=p.y<=self.st.y+1e-7)) :
			   		res.append(p)
		return res
	
	def point_d2(self, p) : 
		w0 = p - self.st
		v = self.end - self.st
		c1 = w0.dot(v)
		if c1 <= 0 :
			return w0.l2()
		c2 = v.dot(v)
		if c2 <= c1 :	
			return (p-self.end).l2()
			
		return ((self.st+c1/c2*v)-p).l2()


class Biarc_Bounds_Tree_Node:
	def __init__(self,i,x1,y1,x2,y2,l,r, item=None) :
		if x1<x2 : 
			self.x1 = x1
			self.x2 = x2
		else :
			self.x1 = x2
			self.x2 = x1
		if y1<y2 : 
			self.y1 = y1
			self.y2 = y2
		else :
			self.y1 = y2
			self.y2 = y1
		self.l = l
		self.r = r
		self.i = i
		self.item = item
		
	def intersect(self, b) :
		return not ( b.x1 > self.x2 or self.x1 > b.x2 or  
				  b.y1 > self.y2 or self.y1 > b.y2 )
	
	def point_inside(self, p): 
		return self.x1<=p.x<=self.x2 and self.y1<=p.y<=self.y2
					
	def point_d2(self, p) :
		pa = [P(self.x1,self.y1), P(self.x2,self.y1), P(self.x2,self.y2), P(self.x1,self.y2)]
		mind = 1e100
		maxd = 0.
		for pl in pa :
			l = (p-pl).l2()
			if l>maxd :	maxd = l
			
		if self.point_inside(p) : mind = 0
		else :
			for i in range(len(pa)) :
				l = Line(pa[i-1],pa[i]).point_d2(p)
				if l<mind : mind = l

		return mind, maxd
				
class Biarc:
	def __init__(self, items=None):
		#debugger.add_debugger_to_class(self.__class__)
		if items == None :
			self.items = []
		else: 	
			self.items = items
		self.bounds_tree = []
		
	def copy(self) :
		b = Biarc()
		for it in self.items :
			b.items.append([])
			for i in it :
				b.items[-1].append(i.copy())
		return b		
	
	def point_inside(self, p) :
		self.close()
		points = []
		for subitems in self.items :
			for item in subitems :
				if (item.st-p).l2<1e-10 : return True
				points.append( [1e100 if p.x-item.st.x == 0 else (item.st.y-p.y)/(item.st.x-p.x),item.st])
		points.sort()
		a = None 
		for i,j in zip(points,points[1:]) :
			if i[0]!=j[0] :
				a = (i[0]+j[0])/2
				break 
		if a==None : return False		
		mx = max([i[1].x for i in points])+10
		l = Line(p,(mx,mx*a))
		count = 0		
		for subitems in self.items :
			for item in subitems :
				p = l.intersect(item)
				if debugger.get_debug_level("point inside"):
					[draw_pointer(p,size=.5, width=.1, text="x") for i in p ]
				if item.__class__==Arc and len(p)==1 and abs(l.n.dot(p[0]-item.c))<1e-10 : count +=2 # touches intem at tangent point.
				else : count += len(p)
		if debugger.get_debug_level("point inside") :
			if count%2==1 :		
				warn(l)
				l.draw(width=.1, color="red")
			else :
				l.draw(width=.1, color="blue")	
			draw_pointer(l.st,color="red",size=10	)
			draw_pointer(l.end,color="blue", size=10)
			draw_pointer(l.st,color="blue", size=10, text=count)		
		return count
	
	
	def point_d2_recursion(self, a, p, mind,maxd) : 
		# returns (exit,d)
		mind2, maxd2 = a.point_d2(p)
		if maxd2<mind : return maxd2
		if mind2>maxd : return mind2
		
		if a.r != None : 
			d = self.point_d2_recursion(a.r, p, mind,maxd )
			if d<mind : return d
		if a.l != None :
			d1 = self.point_d2_recursion(a.l, p, mind,maxd )
			if d1<mind : return d1
		if a.r != None and a.l != None : 
			return min(d,d1)
		# we are at the bottom. and we are in the bounds so:
		#draw_pointer([a.item.st,p], figure="line", color="blue")
		return a.item.point_d2(p)
		

	def point_d2(self, p, mind,maxd) :
		d = 1e100	
		for a in self.bounds_tree :
			d1 = self.point_d2_recursion(a, p, mind,maxd)
			if d1<mind : return d1 
			else : d = min(d,d1)
			#maxd = min(d, maxd)
		return d	
			
	
	def rebuild_bounds_tree(self) :
		""" Bounds tree is needed to increase biarcs intersection speed
			Tree is firstly bounds of subcurves as roots, then binary tree of their elements."""
		self.bounds_tree = []
		self.tree_len = 0
		def create_tree(i,j,k) :
			if i!=j : 
				node = Biarc_Bounds_Tree_Node (
						-1,0,0,0,0,
						create_tree(i,int(floor((i+j)*.5)),k),
						create_tree(int(floor((i+j)*.5)+1),j,k)
					)
				self.tree_len += 1	
				node.x1 = min(node.l.x1, node.r.x1)
				node.y1 = min(node.l.y1, node.r.y1)
				node.x2 = max(node.l.x2, node.r.x2)
				node.y2 = max(node.l.y2, node.r.y2)
				#node.i = "%s - %s"%(i,j) # only for debug
				return node
			else : 
				self.tree_len += 1
				x1,y1, x2,y2 = self.items[k][i].bounds()
				return Biarc_Bounds_Tree_Node (i,x1,y1,x2,y2,None,None, item = self.items[k][i])		
		for i in range(len(self.items)) :
			self.bounds_tree.append( create_tree(0,len(self.items[i])-1,i) ) 	
	
	def intersect_bounds_trees_recursion(self,a,b, selfintersect, depth = 0) :
		if a.intersect(b) : 
			intersect = []
			if a.l == None and a.r == None and b.l == None and b.r == None : 
				if selfintersect and a.i == b.i : return []
				return [[a.i,b.i]]
			if depth % 2 or b.l == None and b.r == None : 
				if a.r != None : 
					intersect += self.intersect_bounds_trees_recursion(a.r,b,selfintersect,depth+1)
				if a.l != None : 
					intersect += self.intersect_bounds_trees_recursion(a.l,b,selfintersect,depth+1)
			if not depth % 2 or a.l == None and a.r == None : 
				if b.l != None : 
					intersect += self.intersect_bounds_trees_recursion(a,b.l,selfintersect,depth+1)
				if b.r != None : 
					intersect += self.intersect_bounds_trees_recursion(a,b.r,selfintersect,depth+1)
			return intersect
		else : return []
	

	def intersect_bounds_trees(self, b) :
		selfintersect =  b == self
		bounds_intersect = []
		for i in range(len(self.items)) : 
			for j in range(len(b.items)) :
				intersect = self.intersect_bounds_trees_recursion(self.bounds_tree[i],b.bounds_tree[j], selfintersect and i==j)
				if intersect != [] :
					bounds_intersect.append([i, j, intersect])
		return bounds_intersect


	def intersect(self,b = None) :
		if b == None : b = self
		selfintersect = b==self  
		
		# rebuild bounds trees, just in case
#		self.rebuild_bounds_tree()
#		if not selfintersect : b.rebuild_bounds_tree()
		
		# get the intersections
		bounds_int = self.intersect_bounds_trees(b)
		res = []
		for int_ in bounds_int :
			i,j,intersect = int_
			for bound in intersect : 
				if debugger.get_debug_level("bounds") :
					self.draw_bounds(self.items[i][bound[0]])
					b.draw_bounds(b.items[j][bound[1]])
				if selfintersect and i == j and bound[0] == bound[1] : continue # same items
				points = self.items[i][bound[0]].intersect(b.items[j][bound[1]])
				for p in points :
					if selfintersect and (	i == j
								 and ( bound[0] == (bound[1] + 1) % len(self.items[i]) and (p-self.items[i][bound[0]].st).l2()<1e-10 
								 		or
								 		bound[1] == (bound[0] + 1) % len(self.items[i]) and (p-self.items[i][bound[0]].end).l2()<1e-10  )	
							): continue # intersection at the start*end
					res.append([i,j,bound[0],bound[1],p])
		return res

	def split_by_points(self, points_) :
		# points are usualy intersection points [i,j,i1,j1,(x,y)] so we'll need only i,i1,(x,y)
		points = {}
		for i,j,i1,j1,p in points_ : 
			if i not in points : points[i] = [] 
			points[i].append([i1,self.items[i][i1].get_t_at_point(p),p])
		items = []
		for i in range(len(self.items)) :
			if i not in points : 
				items.append(self.items[i])
			else :
				points[i].sort()
				si = self.items[i]
				j0, last_p = 0, None
				for j,t,p in points[i] :
					items.append( si[j0:j] )
					items[-1].append(si[j].copy())
					items[-1][-1].head(p)
#					draw_pointer([items[-1][-1].st,items[-1][-1].end],figure="line",text="%s"%items[-1][-1])
					if last_p!=None :
#						draw_pointer([items[-1][0].st,items[-1][0].end],figure="line",text="%s--- %s"%(items[-1][0],last_p))
						items[-1][0].tail(last_p)
#						draw_pointer([items[-1][0].st,items[-1][0].end],figure="line",text="%s--- %s"%(items[-1][0],last_p))
					last_p = p
					j0 = j
				items.append(si[j0:])
				if last_p!=None : 
					items[-1][0].tail(last_p)
#					draw_pointer([items[-1][0].st,items[-1][0].end],figure="line",text="%s"%items[-1][0])
				
		self.items = items		
											
				
	def draw_bounds(self, item=None) :
		if item == None :
			for subitems in self.items :
				for item in subitems : 
					x1,y1,x2,y2 = item.bounds()
					draw_pointer([x1,y1, x2,y1, x2,y2, x1,y2, x1,y1], layer=gcodetools.layers[-1], color="red",figure="line")
		else :	
			x1,y1,x2,y2 = item.bounds()
			draw_pointer([x1,y1, x2,y1, x2,y2, x1,y2, x1,y1], layer=gcodetools.layers[-1], color="red",figure="line")

	
	def l(self) : 
		return sum([ sum([i.length() for i in subitems]) for subitems in self.items ])
	
	
	def close(self) :
		for subitems in self.items:
			if (subitems[0].st-subitems[-1].end).l2()>10e-10 :
				subitems.append(Line(subitems[-1].end,subitems[0].st))
	
	def check_close(self) :
		for subitems in self.items:
			for i in range(len(subitems)) :
				if (subitems[i].st-subitems[i-1].end).l2()>1e-6 : 
					draw_pointer(subitems[i].st, color="blue",figure="cross",width=3,text=_("break %f"%(subitems[i].st-subitems[i-1].end).l2()))
					draw_pointer(subitems[i-1].end, color="blue",figure="cross",width=3,text=_("break %f")%(subitems[i].st-subitems[i-1].end).l2())
	
	def check(self, check_close = True) :
		for subitems in self.items :
			for i in subitems :
				if i.__class__ == Arc :
					if ((i.st-i.c).rot(i.a)+i.c-i.end).l2()>1e-8 : 
						i.draw(color="red",width=5)
						draw_pointer(i.st, text="Bad Arc %s"%i)
		if check_close : self.check_close()
				
	
	def clean(self) :			
		# clean biarc from 0 length elements.
		
		i = 0
		while i<len(self.items) :
			j = 0
			closed = self.items[i][0].st.near(self.items[i][-1].end)
			while j<len(self.items[i]) :
				item = self.items[i][j]
				if ( item.__class__==Line and item.l<1e-3 or
					 item.__class__==Arc and abs(item.r)<1e-3 or
					 (item.st-item.end).l2()<1e-5   )  :
					 		if not closed and j==0 : 
					 			self.items[i][j+1].rebuild(st=self.items[i][j].st)
					 		else: 
					 			self.items[i][j-1].rebuild(end=self.items[i][j].end)
							self.items[i][j:j+1] = []
							continue
				j += 1		
			if self.items[i]==[] :
				self.items[i:i+1] = []
				continue
			i += 1	
	
	def offset_items(self,r) :
		for subitems in self.items :
			for item in subitems :
				item.offset(r)
		self.clean()
		self.connect(r)
		
		
	def offset(self,r, tolerance = 0.0001) :
		self.close()
		self.check()
		self.clean()
		orig = self.copy()

		self.offset_items(r)
		self.check()	

		self.rebuild_bounds_tree()
		self.split_by_points(self.intersect(self))

		self.clean()
#		self.draw(width=.1)
#		return 

		orig.rebuild_bounds_tree()
		i = 0
		while i<len(self.items):
			items = self.items[i]
			if len(items) == 1:  
				if items[0].__class__ == Line :
					p = (items[0].end+items[0].st)*.5
				else : 	
					p = items[0].cp 
			elif len(items) > 1 : 
				p = items[1].st
			d =	orig.point_d2(p,r**2-tolerance,r**2+tolerance)		
			if abs(d-r**2)>tolerance : 
				if debugger.get_debug_level("Offset clip") : 
						draw_pointer(p, figure="cross", width=.1, size=1., color="purple", text="Offset clip on a distance d=%s at r=%.4f"%(sqrt(d),r))
						items[0].draw(color="red", width=.1)
				self.items[i:i+1] = []					
				continue
			i += 1		
				
		self.connect_subitems()		
		self.clean()		

#		orig.draw(width=.1)
		self.draw(width=.1)

	def connect_subitems(self) :
		joined = True
		while joined :	
			joined = False
			i = 0
			while i<len(self.items) :
				j = i+1
				while j<len(self.items) :
					if (self.items[i][-1].end-self.items[j][0].st).l2()<1e-6 : 
						self.items[i] += self.items[j]
						self.items[j:j+1] = []
						joined = True
						continue 
					if (self.items[j][-1].end-self.items[i][0].st).l2()<1e-6 : 
						self.items[i] = self.items[j] + self.items[i]
						self.items[j:j+1] = []
						joined = True
						continue
					j += 1	
				i += 1		
					

	def connect_items_with_arc(self, a, b, r) :
		# get normals
		if a.__class__ == Line : nst = a.n
		else : nst = (a.end-a.c)/a.r
		if b.__class__ == Line : nend = b.n
		else : nend = (b.st-b.c)/b.r

		# get center
		if a.__class__ == Line : c = a.end+a.n*r
		elif b.__class__ == Line : c = b.st+b.n*r
		else:
			c = a.end + (a.end - a.c)*r/a.r*(1. if a.a < 0 else -1.)
		# get angle sign
		ang = -1. if  (a.end-c).cross(b.st-c)<0 else  1.
		if abs(ang) <= 1e-10 : return None
		# return arc
#		draw_pointer([a.end,c,b.st], layer=gcodetools.layers[-1], color="orange", figure="line")
		return Arc(a.end, b.st, c, ang)
		
		
	def connect(self, r):				
		for subitems in self.items :
			i = 0
			while i < len(subitems) :
				a,b = subitems[i],subitems[(i+1)%len(subitems)]
				if (a.end-b.st).l2()<1e-10:
					if a.__class__==Line :
						a.__init__(a.st,b.st)
					else :
						a.__init__(a.st,b.st,a.c,a.a)
						
				else :
					points = a.intersect(b)
					if len(points)==0 : 
						arc = self.connect_items_with_arc(a,b,r)
						if arc!=None:
							subitems.insert(i+1,arc)
							i += 1
					else :
						# take closest point to the start of a
						l2 = None
						for p in points :
							if l2==None or (point-a.st).l2()<l2 : point = p 
						# now we've got only one point		
						a.head(point)
						b.tail(point)
#					for p in a.intersect(b) : 
#						draw_pointer(p.to_list(), layer=gcodetools.layers[-1], color="orange")
				i += 1				
				
						
	def draw(self, layer=None, group=None, style="biarc_style", width=None, color=None):
		global gcodetools
		gcodetools.set_markers()
		layer, group, transform, reverse_angle = gcodetools.get_preview_group(layer, group, None, None)
		group = inkex.etree.SubElement( group,inkex.addNS('g','svg'), {"gcodetools": "Biarc preview %s"%self} )
		
		num = 0
		for subitems in self.items :
			group_ = inkex.etree.SubElement( group,inkex.addNS('g','svg'), {"gcodetools": "Biarc preview sub %s"%self} )
			for item in subitems :
				num += 1
				#if num>1 : break
				item.draw(group_, style, layer, transform, num, reverse_angle, width=width, color=color)

	def from_old_style(self, curve) :
		#Crve defenitnion [start point, type = {'arc','line','move','end'}, arc center, arc angle, end point, [zstart, zend]]		
		self.items = []
		for sp in curve:
			if sp[1] == 'move':				
				self.items.append([])
			if sp[1] == 'arc':
				self.items[-1].append(Arc(sp[0],sp[4],sp[2],sp[3]))
			if sp[1] == 'line':
				self.items[-1].append(Line(sp[0],sp[4]))
		self.clean()
		
			
		
			
