import fontTools

from fontTools import ttLib
from fontTools import afmLib
from fontTools import cffLib

font = ttLib.TTFont('/Users/fgriessh/adobe/AdobeTypeLibrary/fonts/SourceSansPro/Roman/ExtraLight/SourceSansPro-ExtraLight.otf')
#afm = afmLib.AFM('/Users/fgriessh/adobe/AdobeTypeLibrary/fonts/SourceSansPro/Roman/ExtraLight/SourceSansPro-ExtraLight.otf')
#font = cffLib.TTFont('/Users/fgriessh/adobe/AdobeTypeLibrary/fonts/SourceSansPro/Roman/ExtraLight/SourceSansPro-ExtraLight.otf')
#print dir(font['GPOS'].table)
#print font['maxp'].numGlyphs
#print font['GPOS'].table.decompile(font['GPOS'] ,font)
# gp = font['GPOS'] #.decompile()
# cm = font['cmap']

t = font['GPOS']
#print
# for i in font.getGlyphSet().keys():
#	print i
#print font.getTableData('GPOS')
#print dir(t)
#print t.compile(font)
decomp = t.decompile(font.getTableData('GPOS'), font)

#t.decompile(font.getTableData('GPOS'), font)
print .toXML(decomp, font)

# print font.getTableData('GPOS')

# for i in a:
# 	print i
#print dir(afmLib)
#a = afmLib.AFM.read(afm)

#print a

#li = []
# for i in font.keys():
# 	if len(i) == 4:
# #		li.append('print "%s"\nprint dir(font[\'%s\'])' % (i, i))
# 		exec( 'var_%s = font["%s"]' % (i, i))
# 		print i
#	exec('print %s' % i)
# for i in li:
# 	exec(i)

#print t.keys()
#print name
#print cm.decompile(font, font)	
#print gp.table.compile



#print dir(font)
# for name in font.keys():
# 	print name
# for name in glyf.keys():
# 	print name

# glyf = font['glyf']
# glyph = glyf['a']
# if hasattr(glyph, "program"):
# 	print dir(glyph.program)

#	print 
# 	asm = glyph.program.getAssembly()
# 	print asm
# p = fontTools.ttLib.tables.ttProgram.Program()
# p.fromAssembly(asm)
# glyph.program = p



#.decompile()
# class abc(DefaultTable.DefaultTable):
# 	def __init__(self, font):
# 		font = self.font
# 		
# 
# 	def what():
# 		print self.font
# 		
# 		
# a = abc

# 	def decompile(self, data, ttFont):

# 		data = self.data
#		ttfont = self.font
	

# class table_F_O_O_(DefaultTable.DefaultTable): # converter for table 'FOO '
# 	
# 	def decompile(self, data, ttFont):
# 		# 'data' is the raw table data. Unpack it into a
# 		# Python data structure.
# 		# 'ttFont' is a ttLib.TTfile instance, enabling you to
# 		# refer to other tables. Do ***not*** keep a reference to
# 		# it: it will cause a circular reference (ttFont saves 
# 		# a reference to us), and that means we'll be leaking 
# 		# memory. If you need to use it in other methods, just 
# 		# pass it around as a method argument.
# 	
# 	def compile(self, ttFont):
# 		# Return the raw data, as converted from the Python
# 		# data structure. 
# 		# Again, 'ttFont' is there so you can access other tables.
# 		# Same warning applies.
