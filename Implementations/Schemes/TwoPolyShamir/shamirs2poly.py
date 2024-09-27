# shamirs2poly.py. This is "C:\Users\harma\OneDrive - City, University of London\Cyber Security MSc\Individual Project\Implementations of schemes\Shamirs\2PolyLowerPrimeForHigherThreshold.py"

from __future__ import division
from __future__ import print_function
import random
import functools

# Use a smaller 256-bit prime
_PRIME = 2 ** 61 - 1

_RINT = functools.partial(random.SystemRandom().randint, 0)

def generate_location_shares(latitude, longitude, minimum, shares, prime=_PRIME, scale=1000000):
    lat_shares = make_random_shares(latitude, minimum, shares, prime, scale)
    lon_shares = make_random_shares(longitude, minimum, shares, prime, scale)
    return [(i, lat[1], lon[1]) for i, lat, lon in zip(range(1, shares + 1), lat_shares, lon_shares)]

def recover_location(lat_shares, lon_shares, prime=_PRIME, scale=1000000):
    latitude = recover_secret(lat_shares, prime, scale)
    longitude = recover_secret(lon_shares, prime, scale)
    return latitude, longitude

def make_random_shares(secret, minimum, shares, prime=_PRIME, scale=1000000):
    if minimum > shares:
        raise ValueError("Pool secret would be irrecoverable.")

    scaled_secret = int(secret * scale) % prime
    poly = [scaled_secret] + [_RINT(prime - 1) for _ in range(minimum - 1)]
    points = [(i, _eval_at(poly, i, prime)) for i in range(1, shares + 1)]
    return points

def _eval_at(poly, x, prime):
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def recover_secret(shares, prime=_PRIME, scale=1000000):
    if len(shares) < 2:
        raise ValueError("Need at least two shares")

    x_s, y_s = zip(*shares)
    recovered_secret = _lagrange_interpolate(0, x_s, y_s, prime)

    if recovered_secret > prime // 2:
        recovered_secret -= prime

    return recovered_secret / scale

def _lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"

    def PI(vals):
        accum = 1
        for v in vals:
            accum *= v
        return accum

    nums = []
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others) % p)
        dens.append(PI(cur - o for o in others) % p)
    den = PI(dens) % p
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p) for i in range(k)]) % p
    return (_divmod(num, den, p) + p) % p

def _divmod(num, den, p):
    inv, _ = _extended_gcd(den, p)
    return (num * inv) % p

def _extended_gcd(a, b):
    x, last_x = 0, 1
    y, last_y = 1, 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

# I think this can be removed
#def process_scheme2(latitude, longitude, t, n):
#    """Process Scheme 2"""
#    shares = generate_location_shares(latitude, longitude, t, n)
#    lat_shares = [(share[0], share[1]) for share in shares[:t]]
#    lon_shares = [(share[0], share[2]) for share in shares[:t]]
#    recovered_latitude, recovered_longitude = recover_location(lat_shares, lon_shares)
#    return recovered_latitude, recovered_longitude, shares
