
def g(arg1, arg2):
    print "arg1=",arg1," arg2=",arg2

def test( a ):
    return lambda arg: g( arg, a )
