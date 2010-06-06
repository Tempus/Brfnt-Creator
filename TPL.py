def Decode(dest, tex, w, h, type):
    """Pass it on!"""

    if type == 0:
        return I4Decode(dest, tex, w, h)
    elif type == 1:
        return I8Decode(dest, tex, w, h)
    elif type == 2:
        return IA4Decode(dest, tex, w, h)
    elif type == 3:
        return IA8Decode(dest, tex, w, h)
    elif type == 4:
        return RGB565Decode(dest, tex, w, h)
    elif type == 5:
        return RGB4A3Decode(dest, tex, w, h)
    elif type == 6:
        print "Oops! Not done this yet."
        return
        return RGBA8Decode(dest, tex, w, h)
    elif type == 8:
        print "CI4 Not supported."
        return
    elif type == 9:
        print "CI8 Not supported."
        return
    elif type == 10:
        print "CI14x2 Not supported."
        return
    elif type == 14:
        print "I love the CMPR format. But not supported."
        return


def Encode(dest, tex, w, h, type):
    """Pass it on!"""

    if type == 0:
        return I4Encode(dest, tex, w, h)
    elif type == 1:
        return I8Encode(dest, tex, w, h)
    elif type == 2:
        return IA4Encode(dest, tex, w, h)
    elif type == 3:
        return IA8Encode(dest, tex, w, h)
    elif type == 4:
        return RGB565Encode(dest, tex, w, h)
    elif type == 5:
        return RGB4A3Encode(dest, tex, w, h)
    elif type == 6:
        return RGBA8Encode(dest, tex, w, h)
    elif type == 8:
        print "CI4 Not supported."
        return
    elif type == 9:
        print "CI8 Not supported."
        return
    elif type == 10:
        print "CI14x2 Not supported."
        return
    elif type == 14:
        print "I love the CMPR format. But not supported."
        return



def I4Decode(dest, tex, w, h):
    i = 0
    for ytile in xrange(0, h, 8):
        for xtile in xrange(0, w, 8):
            for ypixel in xrange(ytile, ytile + 8):
                for xpixel in xrange(xtile, xtile + 8, 2):

                    if(xpixel >= w or ypixel >= h):
                        continue
                    
                    newpixel = (tex[i] >> 4) * 255 / 15 # upper nybble
                    
                    argb = (newpixel) | (newpixel << 8) | (newpixel << 16) | (0xFF << 24)
                    dest.setPixel(xpixel, ypixel, argb)
                    
                    newpixel = (tex[i] & 0x0F) * 255 / 15 # lower nybble
                    
                    argb = (newpixel) | (newpixel << 8) | (newpixel << 16) | (0xFF << 24)
                    dest.setPixel(xpixel+1, ypixel, argb)
                    
                    i += 1
    return dest
    
def I8Decode(dest, tex, w, h):
	i = 0
	for ytile in xrange(0, h, 4):
		for xtile in xrange(0, w, 8):
			for ypixel in xrange(ytile, ytile + 4):
				for xpixel in xrange(xtile, xtile + 8):
					
					if(xpixel >= w or ypixel >= h):
						continue
					
					newpixel = tex[i]

					argb = (newpixel) | (newpixel << 8) | (newpixel << 16) | (0xFF << 24)
					dest.setPixel(xpixel, ypixel, argb)
					
					i += 1
	return dest

def IA4Decode(dest, tex, w, h):
	i = 0
	for ytile in xrange(0, h, 4):
		for xtile in xrange(0, w, 8):
			for ypixel in xrange(ytile, ytile + 4):
				for xpixel in xrange(xtile, xtile + 8):
					
					if(xpixel >= w or ypixel >= h):
						continue
					
					alpha = (tex[i] >> 4) * 255 / 15
					newpixel = (tex[i] & 0x0F) * 255 / 15

					argb = (newpixel) | (newpixel << 8) | (newpixel << 16) | (alpha << 24)
					dest.setPixel(xpixel, ypixel, argb)

					i += 1
	return dest
	
def IA8Decode(dest, tex, w, h):
	i = 0
	for ytile in xrange(0, h, 4):
		for xtile in xrange(0, w, 4):
			for ypixel in xrange(ytile, ytile + 4):
				for xpixel in xrange(xtile, xtile + 4):
					
					if(xpixel >= w or ypixel >= h):
						continue
					
					newpixel = tex[i]
					i += 1
					
					alpha = tex[i]
					i += 1

					argb = (newpixel) | (newpixel << 8) | (newpixel << 16) | (alpha << 24)
					dest.setPixel(xpixel, ypixel, argb)

	return dest

def RGB565(dest, tex, w, h):
	i = 0
	for ytile in xrange(0, h, 4):
		for xtile in xrange(0, w, 4):
			for ypixel in xrange(ytile, ytile + 4):
				for xpixel in xrange(xtile, xtile + 4):
					
					if(xpixel >= w or ypixel >= h):
						continue
					
					
					blue = (tex[i] & 0x1F) * 255 / 0x1F
					
					
					green1 = (tex[i] >> 5)
					green2 = (tex[i+1] & 0x7)
					
					green = (green1 << 3) | (green2)
					
					red = (tex[i+1] >> 3) * 255 / 0x1F

					argb = (blue) | (green << 8) | (red << 16) | (0xFF << 24)
					dest.setPixel(xpixel, ypixel, argb)

					i += 2

	return dest
	
def RGB4A3Decode(dest, tex, w, h):
	i = 0
	for ytile in xrange(0, h, 4):
		for xtile in xrange(0, w, 4):
			for ypixel in xrange(ytile, ytile + 4):
				for xpixel in xrange(xtile, xtile + 4):
					
					if(xpixel >= w or ypixel >= h):
						continue
					
					newpixel = (tex[i] << 8) | tex[i+1]
					

					if(newpixel >= 0x8000): # Check if it's RGB555
						red = ((newpixel >> 10) & 0x1F) * 255 / 0x1F
						green = ((newpixel >> 5) & 0x1F) * 255 / 0x1F
						blue = (newpixel & 0x1F) * 255 / 0x1F
						alpha = 0xFF

					else: # If not, it's RGB4A3
						alpha = ((newpixel & 0x7000) >> 12) * 255 / 0x7
						blue = ((newpixel & 0xF00) >> 8) * 255 / 0xF
						green = ((newpixel & 0xF0) >> 4) * 255 / 0xF
						red = (newpixel & 0xF) * 255 / 0xF

					argb = (blue) | (green << 8) | (red << 16) | (alpha << 24)
					dest.setPixel(xpixel, ypixel, argb)
					i += 2
    
	return dest

def RGBA8Decode(dest, tex, w, h):
    i = 0
    for ytile in xrange(0, h, 4):
        for xtile in xrange(0, w, 4):
            for cacheline in xrange(4):
            
                if(xpixel >= w or ypixel >= h):
                    continue
                
                argb = (tex[i]) | (tex[i+1] << 8) | (tex[i+2] << 16) | (tex[i+3] << 24)
                dest.setPixel(xpixel, ypixel, argb)
                i += 4
    
    return dest
