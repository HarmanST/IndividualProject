"""
Found here: https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing#Shamir's_secret_sharing_scheme

The following Python implementation of Shamir's secret sharing is
released into the Public Domain under the terms of CC0 and OWFa:
https://creativecommons.org/publicdomain/zero/1.0/
http://www.openwebfoundation.org/legal/the-owf-1-0-agreements/owfa-1-0

See the bottom few lines for usage. Tested on Python 2 and 3.
"""

from __future__ import division
from __future__ import print_function

import random
import functools

# Import the functions from the pairing_functions.py script
from .elegantPairingFunction import scale_float_to_int, scale_int_to_float, ElegantPairSigned, ElegantUnpair



# Use a smaller prime, for example, a 64-bit prime number
_PRIME = 2 ** 61 - 1  # A smaller prime, e.g., Mersenne prime

_RINT = functools.partial(random.SystemRandom().randint, 0)

def _eval_at(poly, x, prime):
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def make_random_shares(secret, minimum, shares, prime=_PRIME):
    """
    Generates a random shamir pool for a given secret, returns share points.
    """
    if minimum > shares:
        raise ValueError("Pool secret would be irrecoverable.")
    poly = [secret] + [_RINT(prime - 1) for i in range(minimum - 1)]
    points = [(i, _eval_at(poly, i, prime)) for i in range(1, shares + 1)]
    return points

def _extended_gcd(a, b):
    """
    Division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1). This can
    be computed via the extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    """
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def _divmod(num, den, p):
    """Compute num / den modulo prime p

    To explain this, the result will be such that:
    den * _divmod(num, den, p) % p == num
    """
    inv, _ = _extended_gcd(den, p)
    return num * inv % p

def _lagrange_interpolate(x, x_s, y_s, p):
    """
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order.
    """
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"

    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum *= v
        return accum

    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p)
               for i in range(k)])
    return (_divmod(num, den, p) + p) % p

def recover_secret(shares, prime=_PRIME):
    """
    Recover the secret from share points
    (points (x,y) on the polynomial).
    """
    if len(shares) < 3:
        raise ValueError("need at least three shares")
    x_s, y_s = zip(*shares)
    return _lagrange_interpolate(0, x_s, y_s, prime)



def shamir_secret_sharing(latitude, longitude, t, n):
    """
    Uses Shamir's Secret Sharing scheme to encode and decode coordinates.

    Args:
        latitude (float): The latitude value.
        longitude (float): The longitude value.
        t (int): The minimum number of shares needed to reconstruct the secret.
        n (int): The number of shares to generate.

    Returns:
        dict: A dictionary containing the encoded secret, the shares, and the recovered coordinates.
    """
    # Scale the float coordinates to integers
    longitude_scaled = scale_float_to_int(longitude)
    latitude_scaled = scale_float_to_int(latitude)

    # Encode coordinates
    encoded_value = ElegantPairSigned(longitude_scaled, latitude_scaled)

    # Shamir's Secret Sharing: Generate shares
    shares = make_random_shares(secret=encoded_value, minimum=t, shares=n)

    # Recover the secret from the shares
    recovered_secret = recover_secret(shares[:t])

    # Decode the encoded integer back to the original coordinates
    decoded_pair = ElegantUnpair(recovered_secret)

    # Scale the integers back to floats
    longitude_decoded = scale_int_to_float(decoded_pair[0])
    latitude_decoded = scale_int_to_float(decoded_pair[1])

    return {
        "encoded_secret": encoded_value,
        "shares": shares,
        "recovered_longitude": longitude_decoded,
        "recovered_latitude": latitude_decoded
    }

