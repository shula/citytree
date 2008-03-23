def interpolateHSV( inSaturation, inBrightness, inPercent ):
    """
    Given valuse for saturation and brightness interpolate percent and return value
    """
    assert( inSaturation >= 0 and inSaturation <= 100 );
    assert( inBrightness >= 0 and inBrightness <= 100 );
    assert( inPercent >= 0 and inPercent <= 1 );
    
    #---------- get Hue based on Percent ----------
    
    #convert H to [0..360] s,v to [0,1]
    h = 360.0*(1.0-inPercent) + 252.0;
    s =  inSaturation/100.0;
    v =  inBrightness/100.0;
    
    if( h > 360 ): h -= 360
    
    return [h,s,v]

def hsvToRgb( h, s, v ):
    """
    Converts colors in hsv to rgb
    """
    
    
    import math
    Hi = math.floor( h/60.0 ) % 6
    f   = h/60.0 - Hi
    p   = v * (1.0-s)
    q   = v * (1.0-f*s)
    t   = v * (1.0-(1.0-f)*s)
    
    if( Hi == 0 ):
        r = v
        g = t
        b = p
    elif( Hi == 1):
        r = q
        g = v
        b = p
    elif( Hi == 2):
        r = p
        g = v
        b = t
    elif( Hi == 3):
        r = p
        g = q
        b = v
    elif( Hi == 4):
        r = t
        g = p
        b = v
    elif( Hi == 5):
        r = v
        g = p
        b = q
    else:
        raise ValueError("Hi should be 0..5 is %d" % Hi)
        
    r = int(r*255.0)
    g = int(g*255.0)
    b = int(b*255.0)
    
    return [r,g,b]
    
def rgbToWebColor( r,g,b ):
    """
        Converts RGB to #rgb web color
     """
    return "#%02X%02X%02X"%(r,g,b)

