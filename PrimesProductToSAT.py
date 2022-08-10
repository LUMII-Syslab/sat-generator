#!/usr/bin/env python3

import sys  # for argv

from SatMemory import SatMemory
from SatInteger import SatInteger
from SatFormula import *
from CNF import CNF
from DimacsFile import DimacsFile
from BitUtils import *

if __name__ == "__main__":

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage for known factors <p> and <q>:")
        print("  " + sys.argv[0] + " <p> <q>")
        print("Usage for unknown factors of <n>, where n=p*q:")
        print("  " + sys.argv[0] + " <n> <#bits-of-p> <#bits-of-q>")
        print("Unique solution:")
        print("  In order to generate a SAT instance with the UNIQUE solution, n must be a product of two distinct "
              "primes!")
        exit(0)
    if len(sys.argv) == 3:
        # args are: p and q
        given_p = int(sys.argv[1])
        given_q = int(sys.argv[2])
        given_p, given_q = max(given_p, given_q), min(given_p, given_q)
        if given_p <= 1 or given_q <= 1:
            raise Exception("<p> and <q> must be positive factors greater than 1")
        n = given_p * given_q
        p_bits = bits_required(given_p)
        q_bits = bits_required(given_q)
    elif len(sys.argv) == 4:
        # args are: n #bits-of-p #bits-of-q
        n = int(sys.argv[1])
        if n < 4:
            raise Exception("<n> must be a positive product of two positive factors greater than 1, i.e., n>=4")
        p_bits = int(sys.argv[2])
        q_bits = int(sys.argv[3])

    # adding one more bit to each factor, since we use two's complement notation,
    # and we want the most significant bit to be zero (in order to exclude negative numbers)
    p_bits += 1
    q_bits += 1
    # make p and q of equal length, since our SatInteger.product_with() currently
    # does not support multiplying numbers of different length
    p_bits = q_bits = max(p_bits, q_bits)

    n_bits = p_bits + q_bits
    # ^^^important: do not use n_bits = bits_required(n), since there could be not enough bits for n
    #               counter-example: 5*3=15 or 3 bits * 2 bits = 4 bits; 4/2-bits are not sufficient

    n_bits = power_of_2(n_bits)
    p_bits = q_bits = n_bits // 2
    print(str(n_bits) + "-bit product = ", str(p_bits) + "-bit factor", " x ", str(q_bits) + "-bit factor")

    mem = SatMemory(p_bits + q_bits)  # number of free vars
    p_vars = ["x" + str(k) for k in range(1, p_bits + 1)]
    p = SatInteger(mem, p_vars)
    q_vars = ["x" + str(k) for k in range(p_bits + 1, p_bits + q_bits + 1)]
    q = SatInteger(mem, q_vars)

    pq = p.product_with(q, True)  # the last argument specifies whether to optimize multiplication

    n_len = len(pq.literals)
    conjuncts = []
    # conjuncts corresponding to the product bits:
    nn = n
    for i in range(n_len):
        bit = nn % 2
        print("bit " + str(i) + " = " + str(bit))
        nn = nn // 2
        if bit == 1:
            conjuncts.append(pq.literals[i])
        else:
            conjuncts.append(pq.literals[i].inverse())

    # conjuncts that ensure unique solution:
    # 1) exclude negative numbers
    conjuncts.append(p.literals[-1].inverse())  # the most significant p bit is 0
    conjuncts.append(q.literals[-1].inverse())  # the most significant q bit is 0
    # 2) exclude factors equal to 1
    conjuncts.append(Or(mem, p.literals[1:]))  # at least one non-zero p bit (not counting the least significant)
    conjuncts.append(Or(mem, q.literals[1:]))  # at least one non-zero q bit (not counting the least significant)
    # 3) ensuring p-q>=0 that is the most significant bit of (p-q) is 0
    diff = p.sum_with(q.negation())
    conjuncts.append(diff.literals[-1].inverse())

    expected_result = And(mem, conjuncts)

    cnf = CNF(mem, expected_result)
    clauses = cnf.clauses()

    df = DimacsFile(str(n) + ".cnf")
    df.add_clauses(clauses)

    comment = "SAT instance for factoring " + str(n)
    if given_p is not None and given_q is not None:
        comment += " = " + str(given_p) + " x " + str(given_q)
    else:
        comment += " with unknown factors"
    comment1 = "the bits of the first factor (right-to-left): " + str(p)
    comment2 = "the bits of the second factor (right-to-left): " + str(q)

    df.store(comment, comment1, comment2)
