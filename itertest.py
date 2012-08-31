import itertools

l1 = [['e', 'eacute', 'ebreve', 'ecircumflex', 'edieresis', 'egrave', 'oe', 'uni1EBD', 'ae'], ['Z', 'Zcaron']]
l2 = [['v', 'w', 'y', 'yacute', 'ydieresis'], ['K', 'uni1E32', 'uni1E34']]
output = []
for i in l1:
	for j in l2:
		output.extend( list(itertools.product(i, j)))
		
print output
print
output2 = []
for i,j in list(itertools.product(l1, l2)):
	print i, j
	output2.extend( list(itertools.product(i, j)))
#print output2