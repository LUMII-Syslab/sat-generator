#!/usr/bin/env python3

from SatMemory import SatMemory
from SatInteger import SatInteger
from SatFormula import *
from CNF import CNF
from pysat.solvers import Solver

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
    print("clauses ("+str(len(cc))+")=", cc)

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
    print("clauses (" + str(len(clauses)) + ")=", clauses)
    print("Solving: look at ", list(reversed(list(map(lambda x: str(x), q.literals)))))  # q = p_q - p

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

def test_product_with_solver(p, q):
    mem = p.sat_memory
    mem.clear_values()

    diff = p.sum_with(q.negation())
    p_q = p.product_with(q)

    # expected_result = And(mem, [  # 1001 = 9
    #     p_q.literals[0],
    #     p_q.literals[1].inverse(),
    #     p_q.literals[2].inverse(),
    #     p_q.literals[3],
    #     p_q.literals[4].inverse(),
    #     p_q.literals[5].inverse(),
    #     p_q.literals[6].inverse(),
    #     p_q.literals[7].inverse(),
    #     p.literals[-1].inverse(),
    #     Or(mem, p.literals[1:]), # !=0 and !=1
    #     Or(mem, q.literals[1:])  # !=0 and !=1
    # ])
    expected_result = And(mem, [  # 0110 = 6
        p_q.literals[0].inverse(),
        p_q.literals[1],
        p_q.literals[2],
        p_q.literals[3].inverse(),
        p_q.literals[4].inverse(),
        p_q.literals[5].inverse(),
        p_q.literals[6].inverse(),
        p_q.literals[7].inverse(),
        p.literals[-1].inverse(), # exclude negative numbers
        Or(mem, p.literals[1:]),  # !=0 and !=1 (exclude 0 and 1)
        Or(mem, q.literals[1:]),  # !=0 and !=1
        diff.literals[-1].inverse()  # diff >= 0 === p >= q
    ])

    cnf = CNF(mem, expected_result)
    clauses = cnf.clauses()
    print("clauses (" + str(len(clauses)) + ")=", clauses)
    print("Solving: look at p=", list(reversed(list(map(lambda x: str(x), p.literals)))))
    print("Solving: look at q=", list(reversed(list(map(lambda x: str(x), q.literals)))))

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
    p = 5
    q = 3
    n = p * q

    p_bits = bits_required(p)
    q_bits = bits_required(q)

    n_bits = p_bits + q_bits
    # important: do not use n_bits = bits_required(n)
    # counter-example: 5*3=15 or 3 bits * 2 bits = 4 bits; 4/2-bits are not sufficient

    n_bits = power_of_2(n_bits)
    p_bits = q_bits = n_bits // 2
    print(n_bits, p_bits, q_bits)

    mem = SatMemory(p_bits + q_bits)  # number of free vars
    p_vars = ["x" + str(k) for k in range(1, p_bits + 1)]
    p = SatInteger(mem, p_vars)
    q_vars = ["x" + str(k) for k in range(p_bits + 1, p_bits + q_bits + 1)]
    q = SatInteger(mem, q_vars)

    #test_negation(p)
    #test_negation_zero(p)
    #test_negation_with_solver(p)
    #test_sum(p, q)
    #test_sum_with_solver(p, q)
    #test_product(p, q)
    test_product_with_solver(p, q)

    #pq = p.product_with(q)
    # print("pq vars=", pq.var_names)
