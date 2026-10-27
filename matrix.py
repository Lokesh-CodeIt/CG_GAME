"""
matrix.py  -  2D TRANSFORMATIONS using 3x3 HOMOGENEOUS MATRICES
----------------------------------------------------------------
A point (x, y) is written as the column vector [x, y, 1].
Every transformation is a 3x3 matrix, so they can be COMBINED by
matrix multiplication (composite transformation).

Used in the game for:
  * Translation  -> moving the player / bats / keys
  * Rotation     -> player arrow turns to face movement, portal star spins
  * Scaling      -> pulsing key & portal, bat wing flapping, EXPLOSION growing
  * Rotation     -> also: shot arrow aimed at the facing direction, spinning debris
  * Translation  -> also: the arrow flying through the cave
  * Reflection   -> bat is mirrored when it flies left  (scale(-1, 1))
  * Shear        -> torch flame wobbles sideways
"""
import math


def identity():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def translate(tx, ty):
    return [[1, 0, tx], [0, 1, ty], [0, 0, 1]]


def scale(sx, sy):
    return [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]


def rotate(theta):
    """Rotation about the origin by theta radians."""
    c, s = math.cos(theta), math.sin(theta)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def shear(shx, shy):
    return [[1, shx, 0], [shy, 1, 0], [0, 0, 1]]


def reflect_x():
    """Reflection about the X axis (flip vertically)."""
    return scale(1, -1)


def reflect_y():
    """Reflection about the Y axis (flip horizontally)."""
    return scale(-1, 1)


def multiply(a, b):
    """3x3 matrix multiplication  a x b."""
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)]


def compose(*matrices):
    """
    compose(T, R, S) = T x R x S
    The point is transformed by the LAST matrix first (S, then R, then T).
    """
    result = identity()
    for m in matrices:
        result = multiply(result, m)
    return result


def apply(m, points):
    """Apply matrix m to a list of (x, y) points."""
    out = []
    for x, y in points:
        out.append((m[0][0] * x + m[0][1] * y + m[0][2],
                    m[1][0] * x + m[1][1] * y + m[1][2]))
    return out
