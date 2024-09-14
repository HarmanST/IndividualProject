from sympy.ntheory.modular import crt
from libnum import generate_prime
from random import randint
import sys
from math import prod

# Import functions from pairing_functions.py script
from .pairingFunction import scale_float_to_int, scale_int_to_float, ElegantPairSigned, ElegantUnpair

# Function to calculate the minimum number of bits needed to represent a number
def get_bit_size(x):
    return x.bit_length()

# Function to generate pairwise coprime integers
def generate_coprime_sequence(n, bit_size=8):
    m = [generate_prime(bit_size)]  # Start with a small prime for m0
    for _ in range(n):
        new_prime = generate_prime(bit_size)
        # Ensure coprimality by using primes or prime-like numbers
        while any(new_prime % prime == 0 for prime in m):
            new_prime = generate_prime(bit_size)
        m.append(new_prime)
    return m

# Function to create shares for longitude and latitude
def create_shares(n, t, longitude, latitude):
    # Scale the float coordinates to integers
    longitude_scaled = scale_float_to_int(longitude)
    latitude_scaled = scale_float_to_int(latitude)

    # Encode coordinates
    encoded_value = ElegantPairSigned(longitude_scaled, latitude_scaled)
    secret = encoded_value

    # Validate that t <= n
    if t > n:
        raise ValueError("Threshold cannot be greater than the total number of shares.")

    secret_bitsize = get_bit_size(secret)
    bitsize = max(secret_bitsize + 10, 60)  # Ensure m0 has at least 10 bits more than S, or default to 60 bits

    m = generate_coprime_sequence(n, bitsize)

    while not (m[0] * prod(m[n-t+2:n+1]) < prod(m[1:t+1])):
        m = generate_coprime_sequence(n, bitsize)  # Regenerate sequence until condition is met

    M = prod(m[1:t+1])  # Product of the first t moduli
    alpha = randint(1, M // m[0])  # Random α such that S + alpha * m0 < m1 * ... * mk

    shares = [(secret + alpha * m[0]) % m[i+1] for i in range(n)]

    return {
        "shares": shares,
        "moduli": m
    }

# Function to reconstruct original coordinates from the shares
def reconstruct_coordinates(shares, moduli, t):
    # Use the first t shares and moduli for reconstruction
    t_moduli = [moduli[i+1] for i in range(t)]
    t_shares = [shares[i] for i in range(t)]

    # Solve the system of congruences using the Chinese Remainder Theorem (CRT)
    reconstructed, _ = crt(t_moduli, t_shares)
    result = reconstructed % moduli[0]

    # Decode the encoded integer back to the original coordinates
    decoded_pair = ElegantUnpair(result)

    # Scale the integers back to floats
    longitude_decoded = scale_int_to_float(decoded_pair[0])
    latitude_decoded = scale_int_to_float(decoded_pair[1])

    return {
        "recovered_longitude": longitude_decoded,
        "recovered_latitude": latitude_decoded
    }

