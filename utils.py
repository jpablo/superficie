import math

def fluid(method):
    """
    Fluiditize a method
    """
    def func(self, *args, **kwargs):
        method(self,*args, **kwargs)
        return self
    return func


def refine(function, (vmin, vmax, n_points), test, tolerance):
    """ Evaluates function on the n points between vmin and vmax, refining if necessary,
    making sure the distance between any two consecutive points is less than max_distance

    >>> from pivy.coin import SbVec2f as v

    >>> d, i = refine(lambda t: v(t,0), (0,1,3), .5)
    >>> map(tuple, i)
    [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)]
    >>> len(d) == len(i)
    True

    >>> d, i = refine(lambda t: v(t,0), (0,1,3), .4)
    >>> map(tuple, i)
    [(0.0, 0.0), (0.25, 0.0), (0.5, 0.0), (0.75, 0.0), (1.0, 0.0)]
    >>> len(d) == len(i)
    True
    """
    dt = float(vmax - vmin) / ( n_points - 1 )
    domain = [vmin + n*dt for n in xrange(n_points)]
    image = map(function,domain)
    if tolerance:
        i = 0
        n = n_points
        while i < n - 2:
            if test(image,i) > tolerance:
                domain.insert( i+1, (domain[i] + domain[i+1])/2 )
                image.insert ( i+1, function(domain[i+1]) )
                n += 1
            else:
                i += 1
    return domain, image

def refine_by_distance(function, (vmin, vmax, n_points), max_distance):
    """ Evaluates function on the n points between vmin and vmax, refining if necessary,
    making sure the distance between any two consecutive points is less than max_distance

    >>> from pivy.coin import SbVec2f as v

    >>> d, i = refine(lambda t: v(t,0), (0,1,3), .5)
    >>> map(tuple, i)
    [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)]
    >>> len(d) == len(i)
    True

    >>> d, i = refine(lambda t: v(t,0), (0,1,3), .4)
    >>> map(tuple, i)
    [(0.0, 0.0), (0.25, 0.0), (0.5, 0.0), (0.75, 0.0), (1.0, 0.0)]
    >>> len(d) == len(i)
    True
    """
    return refine(function, (vmin, vmax, n_points), distance, max_distance)

def refine_by_angle(function, (vmin, vmax, n_points), max_angle):
    delta = 1e-5
    def test(points, i):
        v1 = points[i+1] - points[i]
        v2 = points[i+2] - points[i+1]
        d = distance(v1, v2)
        length1 = v1.length()
        length2 = v2.length()
        if length1 < delta or length2 < delta:
            return 0
        return abs(angle(v1, v2, length1, length2))
    return refine(function, (vmin, vmax, n_points), test, max_angle)

def adjustArg(arg):
    if arg > 1.0:
        return 1.0
    elif arg < -1.0:
        return -1.0
    return arg


def distance(v1,v2):
    return (v1-v2).length()


def angle(v1,v2, length1, length2):
    return math.acos(adjustArg(v1.dot(v2) / (length1 * length2)))