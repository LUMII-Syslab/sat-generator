#!/usr/bin/env python3

from SatFormula import *


class SatMemory:
    # literal indices start from 1, e.g., 1 for x1 and -2 for not(x2)

    def __init__(self, n_free_vars):
        self.next_index = 1
        self.n_free_vars = n_free_vars
        self.literals = {}  # serialized formula -> Literal instance
        self.reduced_formulas = {}  # serialized literal -> formula, for which we introduced the literal
        for i in range(1, n_free_vars+1):
            self.allocate()
        self.values = {}
        self.clear_values()  # self.values: serialized formula -> computed/assigned value

    def clear_values(self):
        self.values = {}
        self.assign("True", True)
        self.assign("False", False)
        pass

    def is_free_var(self, var_name):
        index = int(var_name[1:])
        return (1 <= index) and (index <=self.n_free_vars)

    def allocate(self):
        # returns a Literal instance; always creates 2 literals
        var_name = "x" + str(self.next_index)  # new binary variable
        self.next_index += 1
        pos_literal = Literal(self, False, var_name)
        neg_literal = Literal(self, True, var_name)
        self.literals[str(pos_literal)] = pos_literal
        self.literals[str(neg_literal)] = neg_literal
        return pos_literal

    def allocate_for(self, formula):
        # returns either a positive or a negative Literal instance depending on
        # whether the formula is a negation; there will be 2 literals for each SAT memory bit
        s = str(formula)
        if s in self.literals:
            return self.literals[s]
        var_name = "x" + str(self.next_index)  # new binary variable
        self.next_index += 1
        if formula.is_negation():
            pos_literal = Literal(self, False, var_name)
            neg_literal = Literal(self, True, var_name, formula)
            ret_val = neg_literal
        else:
            pos_literal = Literal(self, False, var_name, formula)
            neg_literal = Literal(self, True, var_name)
            ret_val = pos_literal

        self.literals[str(formula)] = pos_literal
        self.literals[str(pos_literal)] = pos_literal
        self.literals[str(neg_literal)] = neg_literal
        return ret_val

    def assign(self, formula_str, val):
        self.values[formula_str] = val

    def assigned(self, formula_str):
        return formula_str in self.values

    def literal(self, str):
        if str == "True":
            return Constant(self, True)
        elif str == "False":
            return Constant(self, False)
        else:
            return self.literals[str]







