#!/usr/bin/env python3

from pysat.solvers import Solver

from SatMemory import SatMemory
from SatInteger import SatInteger
from SatFormula import *
from CNF import CNF
from BitUtils import *

def test_negation(p):
    mem = p.sat_memory
    mem.clear_values()
    negated = p.negation()
    print("p=", p)
    print("negated=", negated)
    mem.assign(str(p.literals[0]), True)
    mem.assign(str(p.literals[1]), True)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), False)

    print("negated 0011:", negated)


def test_negation_zero(p):
    mem = p.sat_memory
    mem.clear_values()
    negated = p.negation()
    print("p=", p)
    print("negated=", negated)
    mem.assign(str(p.literals[0]), False)
    mem.assign(str(p.literals[1]), False)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), False)

    print("negated 0000:", negated)

    mem.assign(str(p.literals[0]), False)
    mem.assign(str(p.literals[1]), False)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), True)

    print("negated 1000:", negated)


def test_negation_with_solver(p):
    mem = p.sat_memory
    mem.clear_values()
    negated = p.negation()
    print("p=", p)
    print("negated=", negated)
    # mem.assign(str(p.literals[0]), True)
    # mem.assign(str(p.literals[1]), True)
    # mem.assign(str(p.literals[2]), False)
    # mem.assign(str(p.literals[3]), False)

    expected_result = And(mem, [  # 1101
        negated.literals[0],
        negated.literals[1].inverse(),
        negated.literals[2],
        negated.literals[3]
    ])
    print("Expected: ")
    for lit in expected_result.operands:
        print(lit)

    cnf = CNF(mem, expected_result)
    clauses = cnf.clauses()
    print("clauses (" + str(len(clauses)) + ")=", clauses)
    print("Solving: look at ", list(reversed(list(map(lambda x: str(x), p.literals)))))

    with Solver(name="Cadical", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Cadical result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
        print(solver.get_model())
    with Solver(name="Glucose3", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Gluecose3 result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
    print(solver.get_model())
    with Solver(name="Glucose4", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Gluecose4 result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
        print(solver.get_model())


def test_sum(p, q):
    mem = p.sat_memory

    mem.clear_values()
    mem.assign(str(p.literals[0]), True)
    mem.assign(str(p.literals[1]), True)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), False)

    p_q = p.sum_with(q)

    print(str(p) + "+" + str(q) + "=" + str(p_q))
    mem.assign(str(q.literals[0]), True)
    mem.assign(str(q.literals[1]), False)
    mem.assign(str(q.literals[2]), True)
    mem.assign(str(q.literals[3]), False)
    print(str(p) + "+" + str(q) + "=" + str(p_q))

    mem.clear_values()
    mem.assign(str(p.literals[0]), True)
    mem.assign(str(p.literals[1]), True)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), False)

    mem.assign(str(q.literals[0]), True)
    mem.assign(str(q.literals[1]), True)
    mem.assign(str(q.literals[2]), False)
    mem.assign(str(q.literals[3]), False)
    print(str(p) + "+" + str(q) + "=" + str(p_q))

    mem.clear_values()
    mem.assign(str(p.literals[0]), True)
    mem.assign(str(p.literals[1]), True)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), False)

    mem.assign(str(q.literals[0]), True)
    mem.assign(str(q.literals[1]), True)
    mem.assign(str(q.literals[2]), True)
    mem.assign(str(q.literals[3]), True)
    print(str(p) + "+" + str(q) + "=" + str(p_q))

    expected = And(mem, [
        p_q.literals[0].inverse(),
        p_q.literals[1],
        p_q.literals[2].inverse(),
        p_q.literals[3].inverse()
    ])
    cnf = CNF(mem, expected.simplified_formula())
    cc = cnf.clauses()
    print("clauses (" + str(len(cc)) + ")=", cc)


def test_sum_with_solver(p, q):
    mem = p.sat_memory

    mem.clear_values()
    mem.assign(str(p.literals[0]), True)
    mem.assign(str(p.literals[1]), True)
    mem.assign(str(p.literals[2]), False)
    mem.assign(str(p.literals[3]), False)

    p_q = p.sum_with(q)

    expected_result = And(mem, [  # 1101
        p_q.literals[0],
        p_q.literals[1].inverse(),
        p_q.literals[2],
        p_q.literals[3]
    ])
    print("Expected: ")
    for lit in expected_result.operands:
        print(lit)

    cnf = CNF(mem, expected_result)
    clauses = cnf.clauses()
    #print("clauses (" + str(len(clauses)) + ")=", clauses)
    print("Solving: look at ", list(reversed(list(map(lambda x: str(x), q.literals)))))  # q = p_q - p

    return
    with Solver(name="Cadical", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Cadical result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
        print(solver.get_model())
    with Solver(name="Glucose3", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Gluecose3 result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
    print(solver.get_model())
    with Solver(name="Glucose4", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Gluecose4 result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
        print(solver.get_model())


def test_product(p, q):
    mem = p.sat_memory
    mem.clear_values()
    print("p=", p)
    print("q=", q)
    mem.assign(str(p.literals[0]), True)
    mem.assign(str(p.literals[1]), False)
    mem.assign(str(p.literals[2]), True)
    mem.assign(str(p.literals[3]), False)

    mem.assign(str(q.literals[0]), True)
    mem.assign(str(q.literals[1]), True)
    mem.assign(str(q.literals[2]), False)
    mem.assign(str(q.literals[3]), False)

    pq = p.product_with(q)

    print("p*q = ", pq)


def test_product_with_solver(n, p, q):
    mem = p.sat_memory
    #mem.clear_values()

    p_q = p.product_with(q)

    # Computing the expected_result clause, e.g.,
    # expected_result = And(mem, [  # 0110 = 6
    #    p_q.literals[0].inverse(),
    #    p_q.literals[1],
    #    p_q.literals[2],
    #    p_q.literals[3].inverse(),
    #    p_q.literals[4].inverse(),
    #    p_q.literals[5].inverse(),
    #    p_q.literals[6].inverse(),
    #    p_q.literals[7].inverse(),
    #    p.literals[-1].inverse(),  # exclude negative p
    #    q.literals[-1].inverse(),  # exclude negative q
    #    Or(mem, p.literals[1:]),  # !=0 and !=1 (exclude 0 and 1)
    #    Or(mem, q.literals[1:]),  # !=0 and !=1
    #    diff.literals[-1].inverse()  # diff >= 0 === p >= q
    #])

    n_len = len(p_q.literals)
    conjuncts = []
    # conjuncts corresponding to the product bits:
    for i in range(n_len):
        bit = n % 2
        print("bit "+str(i)+" = "+str(bit))
        n = n // 2
        if bit == 1:
            conjuncts.append(p_q.literals[i])
        else:
            conjuncts.append(p_q.literals[i].inverse())
    print (p_q)

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


    sss = ""
    for con in conjuncts:
        sss += str(con)+" "
    print("CONJUNCTS ",sss)
    expected_result = And(mem, conjuncts)

    cnf = CNF(mem, expected_result)
    clauses = cnf.clauses()
    # print("clauses (" + str(len(clauses)) + ")=", clauses)
    print("Solving: look at p=", list(reversed(list(map(lambda x: str(x), p.literals)))))
    print("Solving: look at q=", list(reversed(list(map(lambda x: str(x), q.literals)))))

    print (p_q)

    from DimacsFile import DimacsFile
    df = DimacsFile("test.cnf")
    df.add_clauses(clauses)

    df.store(str(p)+" "+str(q))

    with Solver(name="Cadical", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Cadical result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
        print(solver.get_model())
    with Solver(name="Glucose3", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Gluecose3 result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
    print(solver.get_model())
    with Solver(name="Glucose4", bootstrap_with=clauses, use_timer=True) as solver:
        is_sat = solver.solve()
        print("Gluecose4 result: ", is_sat, '{0:.4f}s'.format(solver.time()), len(clauses), " clauses")
        print(solver.get_model())


if __name__ == "__main__":

    given_p = 127#114#127 #114 # 127  #3
    given_q = 113#101#113 #101 # 113  #2
    p_bits = bits_required(given_p)
    q_bits = bits_required(given_q)
    n = given_p * given_q

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
    # mem.assign("x1", True)
    # mem.assign("x2", True)
    # mem.assign("x3", True)
    # mem.assign("x4", True)
    # mem.assign("x5", True)
    # mem.assign("x6", True)
    # mem.assign("x7", True)
    # mem.assign("x8", False)
    #
    # mem.assign("x9", True)
    # mem.assign("x10", False)
    # mem.assign("x11", False)
    # mem.assign("x12", False)
    # mem.assign("x13", True)
    # mem.assign("x14", True)
    # mem.assign("x15", True)
    # mem.assign("x16", False)

    # mem.assign("x1", True)
    # mem.assign("x2", False)
    # mem.assign("x3", False)
    # mem.assign("x4", True)
    # mem.assign("x5", False)
    # mem.assign("x6", True)
    # mem.assign("x7", True)
    # mem.assign("x8", False)
    #
    # mem.assign("x9", True)
    # mem.assign("x10", True)
    # mem.assign("x11", True)
    # mem.assign("x12", False)
    # mem.assign("x13", True)
    # mem.assign("x14", False)
    # mem.assign("x15", True)
    # mem.assign("x16", False)

    p_vars = ["x" + str(k) for k in range(1, p_bits + 1)]
    p = SatInteger(mem, p_vars)
    print(p)
    q_vars = ["x" + str(k) for k in range(p_bits + 1, p_bits + q_bits + 1)]
    q = SatInteger(mem, q_vars)
    print(q)

    # test_negation(p)
    # test_negation_zero(p)
    # test_negation_with_solver(p)
    # test_sum(p, q)
    # test_sum_with_solver(p, q)
    #test_product(p, q)
    test_product_with_solver(n, p, q)
