import math

def fluid(method):
    """
    Fluiditize a method
    """
    def func(self, *args, **kwargs):
        method(self,*args, **kwargs)
        return self
    return func


def refine(function, (vmin, vmax, n_points), angle, length):
    """ Evaluates function on the n points between vmin and vmax, refining if necessary,
    making sure the distance between any two consecutive points is less than max_distance
    """
    max_points = 3000
    dt = float(vmax - vmin) / ( n_points - 1 )
    domain = [vmin + n*dt for n in xrange(n_points)]
    image = map(function,domain)

    def bisect_and_insert(domain,image,i):
        mp = (domain[i] + domain[i+1])/2
        domain.insert( i+1, mp ); image.insert ( i+1, function(mp) )

    if angle and length:
        i = 0
        n = n_points
        while i < n - 2 and i < max_points:
            if test_angle(image,i) > angle:
                bisect_and_insert(domain,image,i+1)
                bisect_and_insert(domain,image,i)
                n += 2
            elif distance(image, i) > length:
                bisect_and_insert(domain,image,i)
                n += 1
            elif distance(image, i+1) > length:
                bisect_and_insert(domain,image,i+1)
                n += 1
            else:
                i += 1
    return domain, image

def test_angle(points, i):
    delta = 1e-5
    v1 = points[i+1] - points[i]
    v2 = points[i+2] - points[i+1]
    length1 = v1.length()
    length2 = v2.length()
    if length1 < delta or length2 < delta:
        return 0
    return abs(angle(v1, v2))

def adjustArg(arg):
    if arg > 1.0:
        return 1.0
    elif arg < -1.0:
        return -1.0
    return arg


def distance(points, i):
    return (points[i]-points[i+1]).length()


def angle(v1,v2):
    return math.acos(adjustArg(v1.dot(v2) / (v1.length() * v2.length())))