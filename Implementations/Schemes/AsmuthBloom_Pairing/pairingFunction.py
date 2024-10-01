import math

# This script uses functions from Guillou, J (2022). Signed Pairing Function. [online] replit.
# Available at: https://replit.com/@rooksword1/Signed-Pairing-Function#main.py.




# Scaling factor to preserve decimal precision
SCALE_FACTOR = 10**6

def scale_float_to_int(value):
    return int(value * SCALE_FACTOR)

def scale_int_to_float(value):
    return value / SCALE_FACTOR


#Guillou, J (2022)- START
def ElegantPairSigned(x, y):
    a = (x * 2) if x >= 0 else (x * -2 - 1)
    b = (y * 2) if y >= 0 else (y * -2 - 1)

    return (a * a) + a + b if a >= b else (b * b) + a


def ElegantUnpair(z):
    a = math.floor(math.sqrt(z))
    b = z - (a * a)
    r = [a, b - a] if (b >= a) else [b, a]

    a = r[0] // 2 if r[0] % 2 == 0 else (r[0] + 1) // -2
    b = r[1] // 2 if r[1] % 2 == 0 else (r[1] + 1) // -2

    return [a, b]

#Guillou, J (2022) - END