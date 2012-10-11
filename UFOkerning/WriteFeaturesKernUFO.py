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
		
## kerning lists for pairs only
group_group = []
glyph_glyph = []
glyph_group = []
group_glyph = []

# kerning dicts that will contain pair-value combinations
glyph_glyph_dict = {}
glyph_glyph_exceptions_dict = {}
glyph_group_dict = {}
glyph_group_exceptions_dict = {}
group_glyph_dict = {}
group_glyph_exceptions_dict = {}
group_group_dict = {}		

# kerndict = {}

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
	return groupName
	# change Metrics Machine class name to match Adobe class naming.
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

# make glyph-to-group dict to identify which glyphs are in a kerning class; and which one it is.
gl2gr = {}
for i in font.groups.keys():
	for glyph in font.groups[i]:
		if not glyph in gl2gr:
			gl2gr[glyph] = [i]
		else:
			gl2gr[glyph].append(i)
for i in gl2gr:
	gl2gr[i].sort()
	# sorting by left/right

# filter the raw kerning pairs into glyph/glyph, glyph/group, group/glyph and group/group lists.
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
 	
if len(glyph_group) + len(glyph_glyph) + len(group_glyph) + len(group_group) != len(font.kerning): print 'Something went wrong: kerning lists do not match the amount of kerning pairs in the font.'


# process lists to find out which pairs are exceptions, and which just are normal pairs.
for (g, gr) in glyph_group:
	group = font.groups[gr]
	if g in gl2gr:
		# it is a glyph_to_group exception!
		glyph_group_exceptions_dict[g, gr] = font.kerning[g, gr]
	else:
		for i in group:
			pair = (g, i)
			if pair in glyph_glyph:
				# that pair is a glyph_to_glyph exception!
				glyph_glyph_exceptions_dict[pair] = font.kerning[pair]
		else:
			# kerndict[g, group[0]] = font.kerning[g, gr]
			glyph_group_dict[g, gr] = font.kerning[g, gr]



for (gr, g) in group_glyph:
	group = font.groups[gr]
	if g in gl2gr:
		# it is a group_to_glyph exception!
		group_glyph_exceptions_dict[gr, g] = font.kerning[gr, g]
	else:
		for i in group:
			pair = (i, g)
			if pair in glyph_glyph:
				# that pair is a glyph_to_glyph exception!
				glyph_glyph_exceptions_dict[pair] = font.kerning[pair]
		else:
			# kerndict[group[0], g] = font.kerning[gr, g]
			group_glyph_dict[gr, g] = font.kerning[gr, g]
		

for (lgr, rgr) in group_group:
	lgroup = font.groups[lgr]
	rgroup = font.groups[rgr]
	for lg in lgroup:
		for rg in rgroup:
			pair = (lg, rg)
			if pair in glyph_glyph:
				# that pair is a glyph_to_glyph exception!
				glyph_glyph_exceptions_dict[pair] = font.kerning[pair]
	else:
		# kerndict[lgroup[0], rgroup[0]] = font.kerning[lgr, rgr]
		group_group_dict[lgr, rgr] = font.kerning[lgr, rgr]


for (lg, rg) in glyph_glyph:
	pair = (lg, rg)
	if not pair in glyph_glyph_exceptions_dict:
 		# kerndict[pair] = font.kerning[pair]
		glyph_glyph_dict[pair] = font.kerning[pair]



		
def dict2pos(dictionary):
	output = []
	for i in dictionary:
		if (isGroup(i[0]), isGroup(i[1])) == (True, False):
			output.append( '\tpos %s %s %s;' % (adobeName(i[0]), i[1], dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (False, True):
			output.append( '\tpos %s %s %s;' % (i[0], adobeName(i[1]), dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (True, True):
			output.append( '\tpos %s %s %s;' % (adobeName(i[0]), adobeName(i[1]), dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (False, False):
			output.append( '\tpos %s %s;' % (' '.join(i), dictionary[i]) )
	return '\n'.join(sorted(output))


def dict2enumpos(dictionary):
	output = []
	for i in dictionary:
		if (isGroup(i[0]), isGroup(i[1])) == (True, False):
			output.append( '\tenum pos %s %s %s;' % (adobeName(i[0]), i[1], dictionary[i]) )
		if (isGroup(i[0]), isGroup(i[1])) == (False, True):
			output.append( '\tenum pos %s %s %s;' % (i[0], adobeName(i[1]), dictionary[i]) )
	return '\n'.join(sorted(output))



## figure which way the classes are named:
alt_mode = False  # this switch is for the alternate mode, for groups named 'LAT_LC_a', 'CYR_LC_a.cyr' etc.

rex = r'(LAT|CYR|GRK)_(LC|UC)'
counter = 0
for g in font.groups.keys():
	if re.search(rex, g): counter += 1
if counter > len(font.groups.keys())/2:
	alt_mode = True


for groupName, glyphList in sorted(font.groups.items()):
#	print '\t%s = [%s];' % (adobeName(groupName), ' '.join(glyphList))
	if len(getOtherGlyphs(groupName)) == 0:
		print '\t%s = [%s];' % (adobeName(groupName), getKeyGlyph(groupName))
	else:
		print '\t%s = [%s %s];' % (adobeName(groupName), getKeyGlyph(groupName), ' '.join(getOtherGlyphs(groupName)))

# print glyph_glyph_dict
# print glyph_group_dict
# print group_glyph_dict
# print group_group_dict
# print glyph_group_exceptions_dict
# print group_glyph_exceptions_dict
# print
# print glyph_glyph_exceptions_dict



if len(glyph_glyph_exceptions_dict):
	print '\n\t# glyph, glyph exceptions:'
	print dict2pos(glyph_glyph_exceptions_dict)
if len(glyph_glyph_dict):
	print '\n\t# glyph, glyph:'
	print dict2pos(glyph_glyph_dict)
if len(glyph_group_exceptions_dict):
	print '\n\t# glyph, group exceptions:'
	print dict2enumpos(glyph_group_exceptions_dict)
if len(group_glyph_exceptions_dict):
	print '\n\t# group, glyph exceptions:'
	print dict2enumpos(group_glyph_exceptions_dict)

if len(glyph_group_dict):
	print '\n\t# glyph, group:'
	print dict2pos(glyph_group_dict)
if len(group_glyph_dict):
	print '\n\t# group, glyph:'
	print dict2pos(group_glyph_dict)
if len(group_group_dict):
	print '\n\t# group, group:'
	print dict2pos(group_group_dict)

	def writeDataToFile(self):

		if self.MM:
			kKernFeatureFileName = '%s.%s' % (kKernFeatureFileBaseName, 'mmkern')
		else:
			kKernFeatureFileName = '%s.%s' % (kKernFeatureFileBaseName, 'kern')

		print '\tSaving %s file...' % kKernFeatureFileName
		if self.trimmedPairs > 0:
			print '\tTrimmed pairs: %s' % self.trimmedPairs
		
		filePath = os.path.join(self.folder, kKernFeatureFileName)
# 		if os.path.isfile(filePath):
# 			os.chmod(filePath, 0644)  # makes file writable, if it happens to be set to read-only
		outfile = open(filePath, 'w')
		outfile.write('\n'.join(self.instanceFontInfo))
		outfile.write('\n\n')
		if len(self.OTkernClasses):
			outfile.writelines(self.OTkernClasses)
			outfile.write(self.lineBreak)
		if len(self.allKernPairs):
			outfile.writelines(self.allKernPairs)
			outfile.write(self.lineBreak)
		outfile.close()


