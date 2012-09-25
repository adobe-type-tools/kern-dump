# write kern pairs from UFO in a pairs.kern fashion

from defcon import Font
import sys, os, re

if len(sys.argv) > 1:
	input = sys.argv[1]
else:
	print 'No UFO file provided.'
	sys.exit()
	
if os.path.exists(input):
	font = Font(input)
else:
	print 'No proper UFO file provided.'
	sys.exit()


def getKeyGlyph(groupName):
	if groupName in font.groups.keys():
		if alt_mode:
			# this is for groups named 'LAT_LC_a', 'CYR_LC_a.cyr' etc.
	
			if groupName.split('_')[-1] in font.groups[groupName]:
				return '%s' % groupName.split('_')[-1]
			elif '%s_%s' % (groupName.split('_')[-2], groupName.split('_')[-1]) in font.groups[groupName]: # ligatures
				return '%s_%s' % (groupName.split('_')[-2], groupName.split('_')[-1])
			elif '%s_%s_%s' % (groupName.split('_')[-3], groupName.split('_')[-2], groupName.split('_')[-1]) in font.groups[groupName]: # ligatures
				return '%s_%s_%s' % (groupName.split('_')[-3], groupName.split('_')[-2], groupName.split('_')[-1])
			else:
				return font.groups[groupName][0]
	
		else:
			# this is for groups named 'I', 'I_LC', 'S_LC_LEFT_LAT' etc.
			# assuming Metrics Machine-built group names
			glyph = groupName.split('_')[2]

 			if glyph in font.groups[groupName]:
 				return '%s' % glyph
 			elif glyph.lower() in font.groups[groupName]:
 				return '%s' % glyph.lower()

#			ligature crap - omitted
# 			elif '%s_%s' % (groupName.split('_')[-2], groupName.split('_')[-1]) in font.groups[groupName]: # ligatures
# 				return '%s_%s' % (groupName.split('_')[-2], groupName.split('_')[-1])
# 			elif '%s_%s_%s' % (groupName.split('_')[-3], groupName.split('_')[-2], groupName.split('_')[-1]) in font.groups[groupName]: # ligatures
# 				return '%s_%s_%s' % (groupName.split('_')[-3], groupName.split('_')[-2], groupName.split('_')[-1])

			else:
				return font.groups[groupName][0]


		
def isGroup(name):
	if name[0] == '@':
		return True
	else:
		return False


## figure which way the classes are named:
alt_mode = False  # this is the alternate mode, for groups named 'LAT_LC_a', 'CYR_LC_a.cyr' etc.

rex = r'(LAT|CYR|GRK)_(LC|UC)'
counter = 0
for g in font.groups.keys():
	if re.search(rex, g): counter += 1
if counter > len(font.groups.keys())/2:
	alt_mode = True
		
## kerning
d = {}
for (left, right), value in font.kerning.items():
	lGroup = ''
	rGroup = ''
	if isGroup(left):
		lGroup = left
		left = getKeyGlyph(left)
	if isGroup(right):
		rGroup = right
		right = getKeyGlyph(right)

	if (left, right) in d:
		pass
		print '# keyglyph exception: (%s %s)' % (left, right), value

#		print ' '.join((left, right))
#		print (left, right), value, 'already in dict'
#		print d[(left, right)]
#		print lGroup, rGroup
	else:
		d[(left, right)] = value
		
for i in sorted(d):
	print 'pos %s %s;' % (' '.join(i), d[i])

