
#The following Python implementation is based on Wikipedia Contributors (2019). Shamir’s Secret Sharing.
#[online] Wikipedia. Available at: https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing.
#All functions are inspired by the implementation from Wikipedia Contributors (2019).

from __future__ import division, print_function
import random
import functools

# Import the pairing functions
from .pairingFunctions import scale_float_to_int, scale_int_to_float, ElegantPairSigned, ElegantUnpair

# Use a smaller prime, for example, a 64-bit prime number
_PRIME = 2 ** 61 - 1  # A smaller prime, e.g., Mersenne prime
_RINT = functools.partial(random.SystemRandom().randint, 0)

# Polynomial evaluation for Shamir's Secret Sharing
def _eval_at(poly, x, prime):
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def make_random_shares(secret, minimum, shares, prime=_PRIME):
    """Generates a random Shamir pool for a given secret."""
    if minimum > shares:
        raise ValueError("Pool secret would be irrecoverable.")
    poly = [secret] + [_RINT(prime - 1) for _ in range(minimum - 1)]
    points = [(i, _eval_at(poly, i, prime)) for i in range(1, shares + 1)]
    return points

# Extended Euclidean algorithm for modular division
def _extended_gcd(a, b):
    x, last_x = 0, 1
    y, last_y = 1, 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def _divmod(num, den, p):
    inv, _ = _extended_gcd(den, p)
    return num * inv % p

def _lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    assert k == len(set(x_s)), "Points must be distinct"

    def PI(vals):
        accum = 1
        for v in vals:
            accum *= v
        return accum

    nums, dens = [], []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p) for i in range(k)])
    return (_divmod(num, den, p) + p) % p

def recover_secret(shares, prime=_PRIME):
    """Recovers the secret from share points."""
    if len(shares) < 2:
        raise ValueError("Need at least two shares")
    x_s, y_s = zip(*shares)
    return _lagrange_interpolate(0, x_s, y_s, prime)

# Function to create shares from latitude and longitude
def create_shares_shamirs_pairing(latitude, longitude, t, n):
    """Generates shares from latitude and longitude."""
    longitude_scaled = scale_float_to_int(longitude)
    latitude_scaled = scale_float_to_int(latitude)

    # Encode coordinates using Elegant Pairing
    encoded_value = ElegantPairSigned(longitude_scaled, latitude_scaled)

    # Generate Shamir's shares
    shares = make_random_shares(secret=encoded_value, minimum=t, shares=n)

    return {
        "encoded_secret": encoded_value,
        "shares": shares
    }

# Function to recover the secret (longitude, latitude) from shares
def recover_location_shamirs_pairing(shares, t):
    """Recovers the latitude and longitude from a set of shares."""
    if len(shares) < t:
        raise ValueError("Insufficient shares for reconstruction")

    # Recover the encoded secret using the first t shares
    recovered_secret = recover_secret(shares[:t])

    # Decode the secret back into latitude and longitude
    decoded_pair = ElegantUnpair(recovered_secret)
    longitude_decoded = scale_int_to_float(decoded_pair[0])
    latitude_decoded = scale_int_to_float(decoded_pair[1])

    return {
        "recovered_longitude": longitude_decoded,
        "recovered_latitude": latitude_decoded
    }
