#!/usr/bin/env python 
import xml.dom.minidom 
import getopt, sys, os, re, copy

def main():
	def get_gettext(root_node, current_page="", remove=False):
		for node in root_node.childNodes :
			if node.nodeType != node.TEXT_NODE :
				print(node.nodeType)
				if node.nodeType != node.ENTITY_NODE:
					print(node.tagName)
				get_gettext(node)
	f = open("gcodetools-dev.inx","r")
	s = f.read()
	f.close()
	
	s = re.sub( r"(?i).*<!--\s*Gcodetools\s*:\s*(/?)(.*?)\s*-->",r"<\1gcodetools_\2>",s)
	root = xml.dom.minidom.parseString(s)
	
	tags = {}	
		
	def recursive(root):
		for i in root.childNodes:
			if i.nodeType != xml.dom.minidom.Node.TEXT_NODE :
				r = re.match(r"gcodetools_(.*)",i.tagName) 	
				if r :
					tags[r.group(1)] = i
				recursive(i)
#		print tags	
	recursive(root)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "input=" ])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	output = None
	verbose = False
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-i", "--input"):
			input_file = a
		else:
			assert False, "unhandled option"

	for arg_ in args:
		arg = arg_.split()
		for i in arg:
			if i not in tags : 
				print "Can not find tag %s. Ignoring this set %s." % (i,arg_)
				break
		if i not in tags : continue		
		print i
		f=open("./gcodetools_"+"_".join(["%s" % k for k in arg])+".inx"	,"w")		
		inx = copy.deepcopy(root)
		tags = {}
		recursive(inx)
		for i in tags: 
			if i not in ["notebook","help","options","id"] + arg:
				inx.
			
		
if __name__ == "__main__":
	main()

