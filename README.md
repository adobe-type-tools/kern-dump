# kernDump 
Various scripts for analyzing, reading and writing kerning information. These 
can be helpful for analyzing kerning (and the loss thereof) through various 
stages of font production.  
As Presented at [ATypI Amsterdam 2013](http://www.atypi.org/past-conferences/atypi-amsterdam-2013/amsterdam-programme/activity?a=265). 

---

### `dumpKernFeatureFromOTF.py`
Dump a viable kern feature interpreted from the GPOS table found in a compiled font. 

__Dependencies:__ `getKerningPairsFromOTF.py` (same repo), [fontTools](http://sourceforge.net/projects/fonttools/)  
__Environment:__ command line  
```
python dumpKernFeatureFromOTF.py font.otf
python dumpKernFeatureFromOTF.py font.ttf
```

---

### `getKerningPairsFromFeatureFile.py`
Extract a list of all kerning pairs that would be created from a feature file.  
This script is still in development, ‘compact’ notation within a single line 
is not yet fully supported. (Compact notation example: `pos [ a adieresis aacute ] [ v w ] -1000;`)

__Dependencies:__ None  
__Environment:__ command line  

```
python getKerningPairsFromFeatureFile.py kern.fea
```

---

### `getKerningPairsFromOTF.py`
Extract a list of all (flat) GPOS kerning pairs in a font, and report the 
absolute number of pairs.  

__Dependencies:__ [fontTools](http://sourceforge.net/projects/fonttools/)  
__Environment:__ command line

```
python getKerningPairsFromOTF.py font.otf
python getKerningPairsFromOTF.py font.ttf
```

---

### `getKerningPairsFromUFO.py`
Extract a list of all (flat) kerning pairs in a UFO file’s kern object, and 
report the absolute number of pairs.  

__Dependencies:__ [defcon](https://github.com/typesupply/defcon) or Robofont  
__Environment:__ command line or Robofont

```
python getKerningPairsFromUFO.py font.ufo
```

---

### `kernInfoWindow.py`
(Silly) visualization of absolute kerning distance.  
Example of using the above `getKerningPairsFromUFO.py` from within Robofont.  

__Dependencies:__ `getKerningPairsFromUFO.py` (above)  
__Environment:__ Robofont

<img src="kernInfoWindow.png" width="412" height="384" alt="Kern Info Window" />
