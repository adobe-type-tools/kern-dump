# NoneLab
import sys
from robofab.world import OpenFont

p = sys.argv[-1]

f = OpenFont(p)

f.kerning.scale(0.48828125)
f.save()

print 'done'