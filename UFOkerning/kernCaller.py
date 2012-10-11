import WriteFeaturesKernUFO
import time, os, sys

if __name__ == "__main__":
	startTime = time.time()
	# ufo = sys.argv[-1]
	#  	orderFile = sys.argv[1]
	desktop = os.path.expanduser('~/Desktop')
	endTime = round(time.time() - startTime, 2)
	print '%s seconds.' % endTime