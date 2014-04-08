#!/usr/bin/env python 
"""
Copyright (C) 2009 Nick Drobchenko, nick@cnc-club.ru
based on gcode.py (C) 2007 hugomatic... 
based on addnodes.py (C) 2005,2007 Aaron Spike, aaron@ekips.org
based on dots.py (C) 2005 Aaron Spike, aaron@ekips.org

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

#	
#	This extension close paths by adding 'z' before each 'm' if it is not
#	the first 'm' and it is not prepended by 'z' already.
#

import inkex, re, cubicsuperpath
			
class CloseCurves(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("-s", "--subpaths",					action="store", type="inkbool", 		dest="subpaths", default=True)
		self.OptionParser.add_option("-f", "--tolerance",					action="store", type="float", 		dest="tolerance", default=".01")			

	

	def effect(self):
		def point_d2(p1,p2): 
			return (p1[0]-p2[0])**2+(p1[1]-p2[1])**2
		
		def close_csp(csp, tolerance):
			csp = [i for i in csp if i!=[]]
			done_smth = True
			while done_smth:			
				done_smth = False
				i = 0
				while i<len(csp) :
					j = i+1
					while j<len(csp) :
						#inkex.errormsg("%s \n---------\n %s\n\n"%(csp[i],csp[j]))
						if point_d2(csp[i][0][1],csp[j][-1][1])<tolerance :
							csp[i][0][0] = csp[i][0][1]
							csp[j][-1][2] = csp[j][-1][1]
							csp[i] = csp[j] + csp[i]
							csp[j:j+1] = []
							done_smth = True
							continue 
						if point_d2(csp[i][-1][1],csp[j][0][1])<tolerance :
							csp[i][-1][2] = csp[i][-1][1]
							csp[j][0][0] = csp[j][1][1]
							csp[i] = csp[i] + csp[j]
							csp[j:j+1] = []
							done_smth = True
							continue 
						if point_d2(csp[i][0][1],csp[j][0][1])<tolerance :	
							csp[i][0][0] = csp[i][0][1]
							csp[j][0][0] = csp[j][1][1]
							csp[i] = reverse_csp([csp[i]])[0]
							csp[i] = csp[i] + csp[j]
							csp[j:j+1] = []
							done_smth = True
							continue 
						if point_d2(csp[i][-1][1],csp[j][-1][1])<tolerance :	
							csp[i][-1][2] = csp[i][-1][1]
							csp[j][-1][2] = csp[j][-1][1]
							csp[i] = reverse_csp([csp[j]])[0]
							csp[i] = csp[i] + csp[j]
							csp[j:j+1] = []
							done_smth = True
							continue 
						j += 1	
					i += 1
						
			return csp				
							
		def reverse_csp(csp) :
			res =  [ [ [point[2],point[1],point[0]]  for point in subpath]  for subpath in csp]
			res.reverse()
			return res
	
		if self.options.subpaths :
			csp = []
			for id, node in self.selected.iteritems():
				if node.tag == inkex.addNS('path','svg'):
					if "d" not in node.keys() : 
						inkex.errormsg("Warning: One or more paths do not have 'd' parameter, try to Ungroup (Ctrl+Shift+G) and Object to Path (Ctrl+Shift+C)!"+"\n")		
						continue
					csp += cubicsuperpath.parsePath(node.get('d'))
			csp = close_csp(csp,self.options.tolerance**2)			
			attributes = {	'd': cubicsuperpath.formatPath(csp)	}
			inkex.etree.SubElement( self.document.getroot(), inkex.addNS('path','svg'), attributes) 		
			
		else :
			for id, node in self.selected.iteritems():
				if node.tag == inkex.addNS('path','svg'):
					if "d" not in node.keys() : 
						inkex.errormsg("Warning: One or more paths do not have 'd' parameter, try to Ungroup (Ctrl+Shift+G) and Object to Path (Ctrl+Shift+C)!"+"\n")		
						continue
					csp = cubicsuperpath.parsePath(node.get('d'))
					csp = close_csp(csp,self.options.tolerance**2)			
					attributes = {	'd':cubicsuperpath.formatPath(csp)	}
					inkex.etree.SubElement( self.document.getroot(), inkex.addNS('path','svg'), attributes) 		
		
		 					
					
					
				

	
e = CloseCurves()
e.affect()
























