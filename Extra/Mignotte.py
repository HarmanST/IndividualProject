# -*- coding: utf-8 -*-


from libnum import generate_prime
from random import randint
from math import prod
from sympy.ntheory.modular import crt


# Function to generate pairwise coprime integers with Mignotte's constraints
def generate_mignotte_sequence(n, t, secret):
    m = []
    # Generate n coprime integers, ensuring that m0 < secret and m1 < m2 < ... < mn
    for _ in range(n):
        new_prime = generate_prime(8)
        while any(new_prime % prime == 0 for prime in m):
            new_prime = generate_prime(8)
        m.append(new_prime)

    # Ensure the threshold property m1 * m2 * ... * mk > secret > m0 * ... * m_{n-k}
    while not (prod(m[1:t+1]) > secret > prod(m[t+1:])):
        m = []
        for _ in range(n):
            new_prime = generate_prime(8)
            while any(new_prime % prime == 0 for prime in m):
                new_prime = generate_prime(8)
            m.append(new_prime)

    return m

# Function to create shares for a secret
def create_mignotte_shares(n, t, secret):

    if t > n:
        raise ValueError("Threshold cannot be greater than the total number of shares.")

    # Generate sequence of coprime integers
    m = generate_mignotte_sequence(n, t, secret)

    # Create shares as secret mod mi
    shares = [secret % m[i] for i in range(n)]

    # Return the shares and the corresponding moduli
    return shares, m

# Function to reconstruct original secret from shares
def reconstruct_secret(shares, moduli, t):
    # Use the first t shares and moduli for reconstruction
    t_moduli = moduli[:t]
    t_shares = shares[:t]

    # Solve using Chinese Remainder Theorem
    secret, _ = crt(t_moduli, t_shares)

    return secret

# Example usage of create_mignotte_shares and reconstruct_secret functions
if __name__ == "__main__":
    secret = int(input("Enter a secret integer: "))
    n = int(input("Enter the total number of shares (n): "))
    t = int(input("Enter the threshold number of shares (t): "))

    # Create shares
    shares, moduli = create_mignotte_shares(n, t, secret)
    print("\nGenerated shares:")
    for i in range(n):
        print(f"Share {i+1}: (s{i+1} = {shares[i]}, m{i+1} = {moduli[i]})")

    # Reconstruct original secret from shares
    reconstructed_secret = reconstruct_secret(shares, moduli, t)
    print(f"\nReconstructed secret: {reconstructed_secret}")
