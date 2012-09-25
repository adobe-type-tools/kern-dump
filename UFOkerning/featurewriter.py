from defcon import Font
import re, sys, os

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

def isGroup(name):
	if name[0] == '@':
		return True
	else:
		return False
		
## kerning
group_group = []
glyph_glyph = []
glyph_group = []
group_glyph = []

exceptions = {}
kerndict = {}

def getFlag(groupName):
	if groupName in font.groups.keys():
		return groupName.split('_')[1]


def getWSystem(groupName):
	wSystem = None
	for i in groupName.split('_'):
		if re.match(r'(LAT|GRK|CYR)', i):
			wSystem = i
			break
	return wSystem


def getCase(groupName):
	case = None
	for i in groupName.split('_'):
		if len(i) > 1:
			if re.match(r'(UC|LC)', i):
					case = i
	return case


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


def getOtherGlyphs(groupName):
	li = []
	if groupName in font.groups.keys():
		li.extend(font.groups[groupName])
		li.remove(getKeyGlyph(groupName))
		return sorted(li)


def adobeName(groupName):
	# change class name to match adobe class naming.
	if getFlag(groupName) == 'L':
		flag = 'LEFT'
	else: flag = 'RIGHT'

	name = '@%s' % getKeyGlyph(groupName)

	if getCase(groupName):
		name += '_%s' % getCase(groupName)

	name += '_%s' % flag
	
	if getWSystem(groupName):
		name += '_%s' % getWSystem(groupName)
	
	return name


for (left, right), value in sorted(font.kerning.items()):
	if isGroup(left):
		if isGroup(right):
			group_group.append((left, right))
		else:
			group_glyph.append((left, right))
	elif isGroup(right):
		if isGroup(left):
			group_group.append((left, right))
		else:
			glyph_group.append((left, right))
			
	else:
		glyph_glyph.append((left, right))
	

g_gr_dict = {}
for (g, gr) in glyph_group:
	group = font.groups[gr]
	for i in group:
		pair = (g, i)
		if pair in glyph_glyph:
			# it is an exception
			exceptions[pair] = font.kerning[pair]
	else:
		kerndict[g, group[0]] = font.kerning[g, gr]
		g_gr_dict[g, gr] = font.kerning[g, gr]


gr_g_dict = {}
for (gr, g) in group_glyph:
	group = font.groups[gr]
	for i in group:
		pair = (i, g)
		if pair in glyph_glyph:
			# it is an exception
			exceptions[pair] = font.kerning[pair]
	else:
		kerndict[group[0], g] = font.kerning[gr, g]
		gr_g_dict[gr, g] = font.kerning[gr, g]
		

gr_gr_dict = {}		
for (lgr, rgr) in group_group:
	lgroup = font.groups[lgr]
	rgroup = font.groups[rgr]
	for lg in lgroup:
		for rg in rgroup:
			pair = (lg, rg)
			if pair in glyph_glyph:
			# it is an exception
				exceptions[pair] = font.kerning[pair]
	else:
		kerndict[lgroup[0], rgroup[0]] = font.kerning[lgr, rgr]
		gr_gr_dict[lgr, rgr] = font.kerning[lgr, rgr]


g_g_dict = {}
for (lg, rg) in glyph_glyph:
	pair = (lg, rg)
	if not pair in exceptions:
 		kerndict[pair] = font.kerning[pair]
		g_g_dict[pair] = font.kerning[pair]

		
def dict2pos(dictionary):
	output = []
	for i in dictionary:
		if (isGroup(i[0]), isGroup(i[1])) == (True, False):
			output.append( 'enum pos %s [%s] %s;' % (adobeName(i[0]), i[1], dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (False, True):
			output.append( 'enum pos [%s] %s %s;' % (i[0], adobeName(i[1]), dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (True, True):
			output.append( 'pos %s %s %s;' % (adobeName(i[0]), adobeName(i[1]), dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (False, False):
			output.append( 'pos %s %s;' % (' '.join(i), dictionary[i]) )
	return '\n'.join(sorted(output))


## figure which way the classes are named:
alt_mode = False  # this is the alternate mode, for groups named 'LAT_LC_a', 'CYR_LC_a.cyr' etc.

rex = r'(LAT|CYR|GRK)_(LC|UC)'
counter = 0
for g in font.groups.keys():
	if re.search(rex, g): counter += 1
if counter > len(font.groups.keys())/2:
	alt_mode = True


for groupName, glyphList in sorted(font.groups.items()):
#	print '%s = [%s];' % (adobeName(groupName), ' '.join(glyphList))
	if len(getOtherGlyphs(groupName)) == 0:
		print '%s = [%s];' % (adobeName(groupName), getKeyGlyph(groupName))
	else:
		print '%s = [%s %s];' % (adobeName(groupName), getKeyGlyph(groupName), ' '.join(getOtherGlyphs(groupName)))


print
print
print '\n# exceptions:\n'
print dict2pos(exceptions)
print '\n# glyph, glyph:\n'
print dict2pos(g_g_dict)
print '\n# group, glyph:\n'
print dict2pos(gr_g_dict)
print '\n# glyph, group:\n'
print dict2pos(g_gr_dict)
print '\n# group, group:\n'
print dict2pos(gr_gr_dict)


