from math import sin, cos, atan2, hypot

################################################################################
###		Point (x,y) operations
################################################################################
class P:
	def __init__(self, x, y=None):
		if not y==None:
			self.x, self.y = float(x), float(y)
		elif x.__class__ == P :
			self.x, self.y = float(x.x), float(x.y)
		else:
			self.x, self.y = float(x[0]), float(x[1])
	def __add__(self, other): return P(self.x + other.x, self.y + other.y)
	def __sub__(self, other): return P(self.x - other.x, self.y - other.y)
	def __neg__(self): return P(-self.x, -self.y)
	def __mul__(self, other):
		if isinstance(other, P):
			return self.x * other.x + self.y * other.y
		return P(self.x * other, self.y * other)
	__rmul__ = __mul__
	def __div__(self, other): return P(self.x / other, self.y / other)
	def mag(self): return hypot(self.x, self.y)
	def unit(self):
		h = self.mag()
		if h: return self / h
		else: return P(0,0)
	def dot(self, other): return self.x * other.x + self.y * other.y
	def cross(self, other): return self.x * other.y - self.y * other.x
	
	def rot(self, theta):
		c = cos(theta)
		s = sin(theta)
		return P(self.x * c - self.y * s,  self.x * s + self.y * c)	
	def rotate(self, theta):
		c = cos(theta)
		s = sin(theta)
		return P(self.x * c - self.y * s,  self.x * s + self.y * c)
	def angle(self): return atan2(self.y, self.x)
	def __repr__(self): return '%.2f,%.2f' % (self.x, self.y)
	def pr(self): return "%.2f,%.2f" % (self.x, self.y)
	def to_list(self): return [self.x, self.y]	
	def ccw(self): return P(-self.y,self.x)
	def cw(self): return P(self.y,-self.x)
	def l2(self): return self.x*self.x + self.y*self.y
	def transform(self, matrix) :
		x = self.x
		self.x = x*matrix[0][0] + self.y*matrix[0][1] + matrix[0][2] 
		self.y = x*matrix[1][0] + self.y*matrix[1][1] + matrix[1][2] 
	def near(self, b, tolerance=None ) :
		if tolerance==None : tolerance = 1e-7
		return (self-b).l2() < tolerance
	def copy(self) : return P(self.x,self.y)
	def __getitem__(self, i):
		return (self.x if i==0 else self.y if i==1 else None)
