from points import P
from math import *
import inkex
import cubicsuperpath
import simplestyle
import cmath
import bezmisc
################################################################################
###		CSP - cubic super path class
################################################################################
	# CSP = [ [subpath0]...[subpathn] ] - items
	# subpath = [ [p01,p02,p03]...[pm1,pm2,pm3] ] - points
	# [p01,p02,p03] - control point - cp
	# p0k = P(x,y) - point

def cubic_solver_real(a,b,c,d):
	# returns only real roots of a cubic equation.
	roots = cubic_solver(a,b,c,d)
	res = []
	for root in roots :
		if type(root) is complex :	
			if -1e-10<root.imag<1e-10 :
				res.append(root.real)
		else :
			res.append(root)
	return res 
	
	
def cubic_solver(a,b,c,d):	
	if a!=0:
		#	Monics formula see http://en.wikipedia.org/wiki/Cubic_function#Monic_formula_of_roots
		a,b,c = (b/a, c/a, d/a)
		m = 2*a**3 - 9*a*b + 27*c
		k = a**2 - 3*b
		n = m**2 - 4*k**3
		w1 = -.5 + .5*cmath.sqrt(3)*1j
		w2 = -.5 - .5*cmath.sqrt(3)*1j
		if n>=0 :
			t = m+sqrt(n)
			m1 = pow(t/2,1./3) if t>=0 else -pow(-t/2,1./3)
			t = m-sqrt(n)
			n1 = pow(t/2,1./3) if t>=0 else -pow(-t/2,1./3)
		else :
			m1 = complex((m+cmath.sqrt(n))/2)**(1./3) 
			n1 = complex((m-cmath.sqrt(n))/2)**(1./3)
		x1 = -1./3 * (a + m1 + n1)
		x2 = -1./3 * (a + w1*m1 + w2*n1)
		x3 = -1./3 * (a + w2*m1 + w1*n1)
		return [x1,x2,x3]
	elif b!=0:
		det = c**2-4*b*d
		if det>0 :
			return [(-c+sqrt(det))/(2*b),(-c-sqrt(det))/(2*b)]
		elif d == 0 :
			return [-c/(b*b)] 	
		else :
			return [(-c+cmath.sqrt(det))/(2*b),(-c-cmath.sqrt(det))/(2*b)]
	elif c!=0 :
		return [-d/c]
	else : return []

	
class CSP() :
	def __init__(self, csp=[], clean = True ) :
		
		self.items = []
		if type(csp) == type([]) : 
			self.from_list(csp)
		else :
			self.from_el(csp)
		if clean :				
			self.clean()
	
	def join(self, others=None, tolerance=None) :
		if type( others == CSP) :
			others = [others]
		if others != None :	
			for csp in others :
				self.items += csp.copy().items
		joined_smf = True
		while joined_smf : 
			joined_smf = False
			i=0
			while i<len(self.items) :
				j=i+1
				while j<len(self.items) :
					if self.items[i].points[-1][1].near(self.items[j].points[0][1], tolerance) :
						self.concat_subpaths(i,j)
						joined_smf = True
						continue
					if self.items[i].points[0][1].near(self.items[j].points[-1][1], tolerance) :
						self.reverse(i)
						self.reverse(j)						
						self.concat_subpaths(i,j)
						joined_smf = True
						continue
					if self.items[i].points[0][1].near(self.items[j].points[0][1], tolerance) :
						self.reverse(i)
						self.concat_subpaths(i,j)
						joined_smf = True
						continue
					if self.items[i].points[-1][1].near(self.items[j].points[-1][1], tolerance) :
						self.reverse(j)
						self.concat_subpaths(i,j)
						joined_smf = True
						continue
					j += 1
				i += 1
						
						
	
	def concat_subpaths(self, i,j) :
		if not self.items[i].points[-1][1].near(self.items[j].points[0][1]):
			self.items[i].points[-1][2] = self.items[i].points[-1][1].copy()
			self.items[j].points[0][0] = self.items[j].points[0][1].copy()
		else :
			self.items[i].points[-1][2] = self.items[j].points[0][2].copy()
			self.items[j].points[0:1] = []
		self.items[i].points += self.items[j].points	
		self.items[j:j+1] = []
	
	def reverse(self, i=None) :
		if i==None : 
			for i in range(len(self.items)) :
				self.reverse(i)
		else :
			item = self.items[i]
			for cp in item.points : 
				cp.reverse()
			item.points.reverse()	  
	
	def copy(self) : 
		res = CSP()
		for subpath in self.items :
			res.items.append(subpath.copy())
		return res	
		
	def from_list(self, csp) :
		self.items = []
		for subpath in csp :
			self.items.append(CSPsubpath(subpath))	

	def to_list(self) :
		res = []
		for subpath in self.items :
			res.append(subpath.to_list())
		return res		
	
	def from_el(self, el) : 
		if "d" not in el.keys() : 
			return #TODO error!!! 
		self.from_list( cubicsuperpath.parsePath(el.get("d")) )
		
		# TODO redo transforms!  
		#layer = gcodetools.get_layer(el)
		#self.apply_transforms(el)
		#self.transform(layer)

	def to_string(self) : 
		return cubicsuperpath.formatPath(self.to_list()) 

	def length(self) :
		return sum([subpath.length() for subpath in self.items()])

	def slope(self,i,j,t) :
		# slope - normalized slope, i.e. l(n)=1
		return self.items[i].slope(j,t)

	def normal(self,i,j,t) :
		# normal - normalized normal, i.e. l(n)=1
		return self.items[i].normal(j,t)
		
	def transform(self, layer, reverse = False) :
		if layer not in gcodetools.transform_matrix : 
			gcodetools.get_transform_matrix(layer)
		if not reverse :
			self.transform_by_matrix( gcodetools.transform_matrix[layer] )
		else :
			self.transform_by_matrix( gcodetools.transform_matrix_reverse[layer] )

	def transform_by_matrix(self, matrix) :
		for subpath in self.items : 
			subpath.transform(matrix)

	def apply_transforms(self, el, reverse = False) :	
		# applies inkscape's transforms to csp, el element in inkscape object tree
		matrix = gcodetools.get_transforms(el)
		if matrix == [] : return
		if reverse : 
			matrix = gcodetools.reverse_transform(matrix)
		self.transform_by_matrix( matrix )

	def clean(self) : 
		i = 0
		while i<len(self.items) :
			self.items[i].clean()
			if len(self.items[i].points)<=1 : 
				self.items[i:i+1] = []
			else :	
				i += 1
	
	def point(i,j,t) :
		return self.items[i].point(j,t)
		
	def draw(self, near=None, group=None, style_from=None, layer=None, transform=None, stroke=None, fill=None, width=None,  text="", gcodetools_tag = None) :
		# near mean draw net to element 
		# style should be an element to copy style from
		
		# TODO rewrite layers assignment
		if near!=None : 
			group = near.getparent()
			layer = gcodetools.get_layer(near)
			if style_from == None : style_from = near
		#layer, group, transform, reverse_angle = gcodetools.get_preview_group(layer, group, transform)

		#if style_from!=None and "style" in style_from.keys() : 
		#	style = simplestyle.parseStyle(style_from.get("style"))
		#else :
		#	style = {}
		style = {}	
		if width != None  : style['stroke-width'] = "%s"%width
		if stroke != None : style['stroke'] = "%s"%stroke
		if fill != None   : style['fill'] = "%s"%fill
		if style == {} : style = { 'stroke': '#0072a7', 'fill': 'none', 'stroke-width':'1'}
		style = simplestyle.formatStyle(style)

		csp = self.copy()
		#csp.transform(layer,True)	
		
		if text!="" :
			st = csp.items[0].points[0][1]
			draw_text(text, st.x+10,st.y , group = group) 
		attr = {
				"style":	style,
				"d": 		cubicsuperpath.formatPath(csp.to_list()),
				"gcodetools": "Preview %s"%self,
				}	
		if transform != [] and transform != None :
			attr["transform"] = transform	
		return inkex.etree.SubElement(	group, inkex.addNS('path','svg'), attr)
		
	def bounds(self,i=None): 
		if i!=None : 
			return self.bounds.items[i].bounds()
		else :	
			b = [1e100, 1e100, -1e100, -1e100]
			for i in range(len(self.items)) :
				b1 = self.items[i].bounds()
				b = [min(b[0],b1[0]), min(b[1],b1[1]), max(b[2],b1[2]), max(b[3],b1[3])]
			if b == [1e100, 1e100, -1e100, -1e100] : return None
			return b
	
		
		
			
class CSPsubpath() :
	def __init__(self, subpath=[]) :
		self.points = []
		self.from_list(subpath)
	
	def copy(self,st=None,end=None) :
		res = CSPsubpath()
		if st == None : st = 0
		if end == None : end = len(self.points)-1
		for i in range(st,end+1) : 
			cp_ = []
			for point in self.points[i] : 
				cp_.append(P(point.x,point.y))
			res.points.append(cp_)	
		return res
	
	def from_list(self, subpath) :
		self.points = []
		for cp in subpath :
			self.points.append([P(cp[0]),P(cp[1]),P(cp[2])])
	
	def to_list(self) :
		res = []
		for cp in self.points : 
			cp_ = []
			for point in cp :
				cp_.append(point.to_list())
			res.append(cp_)
		return res	

	def draw(self, *args,**kwargs):
		csp = CSP()
		csp.items.append(self)
		return csp.draw(*args,**kwargs)

	def reverse(self) : 
		for p in self.points :
			p.reverse()
		self.points.reverse()
		
	def close(self) :
		if not self.points[0][1].near(self.points[-1][1]) : 
			self.points[-1][2].__init__(self.points[-1][1])
			self.points[0][0].__init__(self.points[0][1])
			self.points.append([ P(self.points[0][1]), P(self.points[0][1]), P(self.points[0][2])  ])

	def is_closed(self) : 
		return self.points[0][1].near(self.points[-1][1])
			
	def length(self) :
		return sum([self.l(i) for i in range(len(self.points)-1)])

	def cp_to_list(self,i) :
		return [point.to_list() for point in self.points[i]]
	
	def l(self, i, tolerance=0.001) :
		return bezmisc.bezierlength( self.cp_to_list(i)[:2]+self.cp_to_list(i+1)[1:], tolerance)
		
	def t_at_l(self, i, l, self_l=None, tolerance=0.001) :
		if self_l == None : self_l = self.l(i)
		if self_l == 0 : return 0.
		return bezmisc.beziertatlength(self.cp_to_list(i)[1:]+self.cp_to_list(i+1)[:2] , l/self_l, tolerance)
	
	def at_l(self, l, tolerance=0.001) :
		i = 0
		while i<len(self.points)-1 :
			l1 = self.l(i)
			if l1<l : 
				l-=l1
			else :	
				return i, self.t_at_l(i,l,l1)
			i += 1	
		return i-1,1	

	def point(self,i,t) :
		sp1,sp2 = self.cp_to_list(i), self.cp_to_list(i+1)
		ax,bx,cx,dx = sp1[1][0], sp1[2][0], sp2[0][0], sp2[1][0]
		ay,by,cy,dy = sp1[1][1], sp1[2][1], sp2[0][1], sp2[1][1]

		x1, y1 = ax+(bx-ax)*t, ay+(by-ay)*t	
		x2, y2 = bx+(cx-bx)*t, by+(cy-by)*t	
		x3, y3 = cx+(dx-cx)*t, cy+(dy-cy)*t	
	
		x4,y4 = x1+(x2-x1)*t, y1+(y2-y1)*t 
		x5,y5 = x2+(x3-x2)*t, y2+(y3-y2)*t 
	
		x,y = x4+(x5-x4)*t, y4+(y5-y4)*t 
		return P(x,y)
	
	def headi(self, i, t) :
		return self.split(i,t)[:2]
		
	def taili(self, i, t) :
		return self.split(i,t)[1:]
	
	def head(self,i,t=0) : # like [:i] for list
		res = self.copy(end=i)
		if t==0 : return res
		res.points[-1:] = []
		res.points+=self.headi(i,t)
		return res
	
	def tail(self,i,t=0) :	# like [i:] for list
		if t==0 : return self.copy(st=i)
		res = self.copy(st=i+1)
		if t==1 : return res
		res.points[:1] = []
		res.points = self.taili(i,t) + res.points
		return res

	def headl(self,l): # Cuts subpath to fit defined l
		i,t = self.at_l(l)
		if i==len(self.points) and t==1 : return CSPSubpath([])
		return self.head(i,t)

	def taill(self,l,cut=False): # Cuts subpath to fit defined l
		res = self.copy()
		res.reverse()
		i,t = res.at_l(l)
		if i==len(res.points) and t==1 : return CSPSubpath([])
		#warn(i,t)
		res = res.head(i,t)
		res.reverse()
		return res
		
	def cut_head_l(self,l):
		return self.taill(self.length()-l)
	
	def cut_tail_l(self,l):
		return self.headl(self.length()-l)
	

				
	def split(self,i,t=.5) :
		sp1,sp2 = self.cp_to_list(i), self.cp_to_list(i+1)
		[x1,y1],[x2,y2],[x3,y3],[x4,y4] = sp1[1], sp1[2], sp2[0], sp2[1] 
		x12 = x1+(x2-x1)*t
		y12 = y1+(y2-y1)*t
		x23 = x2+(x3-x2)*t
		y23 = y2+(y3-y2)*t
		x34 = x3+(x4-x3)*t
		y34 = y3+(y4-y3)*t
		x1223 = x12+(x23-x12)*t
		y1223 = y12+(y23-y12)*t
		x2334 = x23+(x34-x23)*t
		y2334 = y23+(y34-y23)*t
		x = x1223+(x2334-x1223)*t
		y = y1223+(y2334-y1223)*t
		return [[P(sp1[0]),P(sp1[1]),P(x12,y12)], [P(x1223,y1223),P(x,y),P(x2334,y2334)], [P(x34,y34),P(sp2[1]),P(sp2[2])]]
	
	def transform(self, matrix) :
		if matrix == [] : return
		for cp in self.points :
			cp[0].transform(matrix)
			cp[1].transform(matrix)
			cp[2].transform(matrix)

	def zerro_segment(self, j) :
		cp1, cp2 = self.get_segment(j)
		return (cp1[1]-cp2[1]).l2() + (cp1[1]-cp1[2]).l2() + (cp1[1]-cp2[0]).l2() < 1e-7
	
	def parameterize_segment(self,j) :
		# from bezmisc.bezierparameterize 
		cp1, cp2 = self.get_segment(j)
		x0=cp1[1].x
		y0=cp1[1].y
		cx=3*(cp1[2].x-x0)
		bx=3*(cp2[0].x-cp1[2].x)-cx
		ax=cp2[1].x-x0-cx-bx
		cy=3*(cp1[2].y-y0)
		by=3*(cp2[0].y-cp1[2].y)-cy
		ay=cp2[1].y-y0-cy-by
		return ax,ay,bx,by,cx,cy,x0,y0
		#ax,ay,bx,by,cx,cy,x0,y0=bezierparameterize(((bx0,by0),(bx1,by1),(bx2,by2),(bx3,by3)))

	def clean(self) :
		i=0
		while i<len(self.points)-1 :
			if self.zerro_segment(i) : 
				self.points[i][2] = self.points[i+1][2]
				self.points[i+1:i+2] = []
			else : 
				i += 1
		if self.points[0][1].near(self.points[-1][1]) :
			self.points[0][0]  = self.points[-1][0]
			self.points[-1][2] = self.points[0][2]

	
	def get_segment(self,i): 
		if i>=0 : return self.points[i], self.points[i+1]
		else : return self.points[i-1], self.points[i]
			
	def slope(self,j,t) :
		cp1, cp2 = self.get_segment(j)
		if self.zerro_segment(j) : return P(1.,0.)
		ax,ay,bx,by,cx,cy,dx,dy=self.parameterize_segment(j)
		slope = P(3*ax*t*t+2*bx*t+cx, 3*ay*t*t+2*by*t+cy)
		if slope.l2() > 1e-9 : #LT changed this from 1e-20, which caused problems, same further
			return slope.unit()
		# appears than slope len = 0  (can be at start/end point if control point equals endpoint)
		if t == 0 : # starting point 
			slope = cp2[0]-cp1[1]
			if slope.l2() > 1e-9 :  
				return slope.unit()
		if t == 1 :
			slope = cp2[1]-cp1[2]
			if slope.l2() > 1e-9 :  
				return slope.unit()
		# probably segment straight
		slope = cp2[1]-cp1[1]
		if slope.l2() > 1e-9 :  
			return slope.unit()
		# probably something went wrong		
		return P(1.,0.)
	
	def normal(self,j,t) :
		return self.slope(j,t).ccw()
	
	def bounds(self,i=None): 
		if i!=None : 
			return self.boundsi(i)
		else :	
			b = [1e100, 1e100, -1e100, -1e100]
			for i in range(len(self.points)-1) :
				b1 = self.boundsi(i)
				b = [min(b[0],b1[0]), min(b[1],b1[1]), max(b[2],b1[2]), max(b[3],b1[3])]
			if b ==	[1e100, 1e100, -1e100, -1e100] : return None
			return b
				
	def boundsi(self,i): 
		minx, miny, maxx, maxy  = 1e100, 1e100, -1e100, -1e100
		ax,ay,bx,by,cx,cy,x0,y0 = self.parameterize_segment(i)
		roots = cubic_solver(0, 3*ax, 2*bx, cx)	 + [0,1]
		for root in roots :
			if type(root) is complex and abs(root.imag)<1e-10:
				root = root.real
			if type(root) is not complex and 0<=root<=1:
				y = ay*(root**3)+by*(root**2)+cy*root+y0  
				x = ax*(root**3)+bx*(root**2)+cx*root+x0  
				maxx = max(x,maxx)
				minx = min(x,minx)

			roots = cubic_solver(0, 3*ay, 2*by, cy)	 + [0,1]
			for root in roots :
				if type(root) is complex and root.imag==0:
					root = root.real
				if type(root) is not complex and 0<=root<=1:
					y = ay*(root**3)+by*(root**2)+cy*root+y0  
					x = ax*(root**3)+bx*(root**2)+cx*root+x0  
					maxy = max(y,maxy)
					miny = min(y,miny)
		return minx,miny,maxx,maxy
		
		
		
