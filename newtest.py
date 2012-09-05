from GPOSmodules import fromGPOS
# path = '/Users/fgriessh/Desktop/AdobeDevanagari-Regular_LatinOnlyKerning.otf'
path = '/Users/fgriessh/adobe/AdobeTypeLibrary/fonts/SourceSansPro/Roman/ExtraLight/SourceSansPro-ExtraLight.otf'
# print test(path).getSinglePairs()
# print readGPOS.pairPos(path)
# print
# for i in readGPOS.getPairPos(path):
print fromGPOS.getSinglePairs(path)
# print 'x' * 555
# print fromGPOS.getClasses(path)
# (fontPath)
# print readGPOS.__doc__
# 
# print s(path)