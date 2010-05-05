#!/usr/bin/env python 
import xml.dom.minidom 
import getopt, sys, os, re, copy

def usage():
	print "Usage is not ready yet." # TODO


def main():

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "input=" ])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	input_file = None
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-i", "--input"):
			input_file = a
		else:
			assert False, "unhandled option"

	if args == []: 
		args = ["Cutting: ptg area", "ptg area",  "Engraving: engraving", "Tools library: tools_library no_options no_preferences", "Orientation points: orientation no_options no_preferences", "All in one: ptg area engraving tools_library orientation"]
	
	f = open("gcodetools-dev.inx" if input_file == None else input_file,"r")
	s = f.read()
	f.close()
	
	tags = dict(re.findall( r"(?ims)<!--\s*Gcodetools\s*:\s*(.*?)\s*block\s*-->(.*)<!--\s*Gcodetools\s*:\s*/\1\s*block\s*-->",s))
	
	for arg_ in args:
		print "Computing set: %s..." % arg_
		r = re.match("((.*):)?(.*)",arg_)
		if r!=None:
			arg = r.group(3).split()
			res = '<?xml version="1.0" encoding="UTF-8"?>\n'+tags['header']
			name = r.group(2) if r.group(2)!=None else r.group(3)
			id = re.sub("\s|[\.,!@#$%^&*]", "_", r.group(3).lower())
			res = re.sub("(?ims)<!--\s*Gcodetools\s*:\s*name\s*-->(.*)<!--\s*Gcodetools\s*:\s*/name\s*-->","<name>%s</name>"%name,res)
			res = re.sub("(?ims)<!--\s*Gcodetools\s*:\s*id\s*-->(.*)<!--\s*Gcodetools\s*:\s*/id\s*-->","<id>ru.cnc-club.filter.gcodetools_%s</id>"%id,res)

			if 'help' not in arg and 'no_help' not in arg : res += tags['help']
			if 'options' not in arg and 'no_options' not in arg: res += tags['options']
			if 'preferences' not in arg and 'no_preferences' not in arg : res += tags['preferences']

			for i in arg:
				if i not in tags and not re.match("no_",i): 
					print "Can not find tag %s. Ignoring this set %s!\n" % (i,arg_)
					break
				if not re.match("no_",i): res += tags[i]
			if i not in tags and not re.match("no_",i) : continue				
			submenu ="""		<effects-menu>
			<submenu _name="Gcodetools"/>
		</effects-menu>"""
			res += re.sub("(?ims)<!--\s*Gcodetools\s*:\s*submenu\s*-->(.*)<!--\s*Gcodetools\s*:\s*/submenu\s*-->",submenu,tags['footer'])
			
			f = open("gcodetools_%s.inx"%re.sub("\s|[\.,!@#$%^&*]", "_", name.lower()),"w")
			f.write(res)
			f.close()
			print "Done\n"
					
		"""		
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
				pass			
		"""
if __name__ == "__main__":
	main()

