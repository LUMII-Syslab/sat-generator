#!/usr/bin/env python3

import sys  # for argv

from pysat.solvers import Solver

from SatMemory import SatMemory
from SatInteger import SatInteger
from SatFormula import *
from CNF import CNF
from BitUtils import *
from DimacsFile import DimacsFile

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " <fileName.dimacs>")
        exit(0)
        
    df = DimacsFile(sys.argv[1])
    df.load()
    clauses = df.clauses()
    
    print("#vars="+str(df.number_of_vars())+" #clauses="+str(df.number_of_clauses()))

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
