#!/usr/bin/python

""" 

	pyminify.py
	A script to pass javascript files through both closure and the ScriptDiet compressor
	Written by Emil Loer <emil@koffietijd.net>

	Usage: pyminify.py <input.js> <output.js>

"""

import sys
import urllib
import tempfile
from StringIO import StringIO

try:
	import pycurl
except ImportError:
	print "You need the pycurl package for pyminify to work correctly."
	raise SystemExit

def post(url,data=None,mpdata=None):
	""" Do an http post to url with given data and return the result """
	body=StringIO()
	c=pycurl.Curl()
	c.setopt(c.URL,url)
	if mpdata is not None:
		c.setopt(c.HTTPPOST,mpdata)
	else:
		c.setopt(c.POSTFIELDS,urllib.urlencode(data))
	c.setopt(c.WRITEFUNCTION,body.write)
	c.perform()
	c.close()
	return body.getvalue()

if __name__ == '__main__':
	try:
		filename=sys.argv[1]
		outfile=sys.argv[2]
	except IndexError:
		print "usage: %s <input.js> <output.js>"%sys.argv[0]
		raise SystemExit

	try:
		file=open(filename).read()
	except IOError:
		print "Error reading input file"
		raise SystemExit
	origsize=len(file)

	closure=post("http://closure-compiler.appspot.com/compile",data={
		"compilation_level":"ADVANCED_OPTIMIZATIONS",
		"output_format":"text",
		"output_info":"compiled_code",
		"js_code":file,
	})

	closuresize=len(closure)
	print "closure:     %d -> %d (%.1f%% of original)"%(origsize,closuresize,float(closuresize)/float(origsize)*100.0)
	
	tf=tempfile.NamedTemporaryFile()
	tf.write(closure)
	tf.flush()
	
	compressor=post("http://scriptingmagic.com/Compressor.action",mpdata=[
		("file",(pycurl.FORM_FILE,tf.name)),
		("submit","Compress"),
		("_sourcePage","/Topics/Compression/JavaScript Compressor/index.jsp"),
		("__fp","y8Zc0SHFQ0oO0blWj1/lBQ=="),
	])
	
	compressorsize=len(compressor)
	print "compressor:  %d -> %d (%.1f%% of original)"%(closuresize,compressorsize,float(compressorsize)/float(closuresize)*100.0)
	print "grand total: %d -> %d (%.1f%% of original)"%(origsize,compressorsize,float(compressorsize)/float(origsize)*100.0)
	
	try:
		open(outfile,"w").write(compressor)
	except IOError:
		print "Error writing output file"
		raise SystemExit
