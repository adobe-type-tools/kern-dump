import WriteFeaturesKernUFO
import time, os, sys

if __name__ == "__main__":
	startTime = time.time()


	if len(sys.argv) > 1:
		input = sys.argv[1]
	else:
		print 'No UFO file provided.'
		sys.exit()
	
	if os.path.exists(input):
		dir = os.path.abspath(input).split(os.sep)[:-1]
		ufo = os.path.abspath(input).split(os.sep)[-1]
		ufoName = ufo.split('.')[0]
		ext = 'kern'
		f = open('%s%s%s.%s' % (os.sep.join(dir), os.sep, ufoName, ext), 'w')
		f.write(WriteFeaturesKernUFO.UFOkernData(input).do())
		f.close()
	else:
		print 'No proper UFO file provided.'
		sys.exit()

	endTime = round(time.time() - startTime, 2)
	print '%s seconds.' % endTime