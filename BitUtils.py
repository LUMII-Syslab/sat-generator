def power_of_2(n):
    # returns x = 2^k, where x >= n
    log = 0
    x = 1
    # searching for x >= n...
    # invariant: 2^log = x;
    while x < n:
        log = log + 1
        x = x * 2
    return x


def bits_required(n):
    # returns how many bits are required to represent n
    bits = 1
    pow2 = 2
    # invariant: bits bits are sufficient to represent numbers < pow2 = 2^bits
    #            but not sufficient to represent pow2 = 2^bits
    while pow2 <= n:
        bits = bits + 1
        pow2 = pow2 * 2
    return bits
