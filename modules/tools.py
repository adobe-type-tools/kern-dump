#!/usr/bin/python
import string
import itertools

def sortGlyphs(glyphlist):
	# This function is sorting the glyphs in a way that glyphs from the exception list or glyphs starting with 'uni' names don't get 
	# to be key (first) glyphs. Also, an infinite loop is avoided, in case there are only glyphs matching above mentioned properties.
	exceptionList = 'dotlessi dotlessj kgreenlandic ae oe AE OE uhorn'.split()

	glyphs = sorted(glyphlist)
	# sorting the strings by length and then alphabetically

	sort_key = lambda s: (len(s), s)
	glyphs.sort(key=sort_key)

	for i in range(len(glyphs)):
		if glyphs[0] in exceptionList or glyphs[0].startswith('uni') or '_' in glyphs[0]:
			glyphs.insert(len(glyphs), glyphs.pop(0))
		else:
			continue

	return glyphs


def nameClass(glyphlist, flag):
	glyphs = sortGlyphs(glyphlist)	
	if len(glyphs) == 0:
		print 'class is empty'
		return
	else:
		name = glyphs[0]

	if name in string.ascii_lowercase:
		case = '_LC'
	elif name in string.ascii_uppercase:
		case = '_UC'
	else:
		case = ''

	flag = '_%s' % flag
	
	return '@%s%s%s' % (name, flag, case)


def explode(leftClass, rightClass):
	return list(itertools.product(leftClass, rightClass))

