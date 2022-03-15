import logging

from SatFormula import *
from SatClauses import SatClauses

from itertools import chain, combinations


class CNF:
    def __init__(self, sat_memory, simplified_formula, expanded_variables=set()):
        """

        :param sat_memory:
        :param simplified_formula:
        :param expanded_variables: mutable set!
        """
        self.sat_memory = sat_memory
        self.simplified_formula = simplified_formula
        self.expanded_variables = expanded_variables

    def is_atom(self, literal, expanded_variables):
        if not literal.is_literal():
            return False
        return self.sat_memory.is_free_var(literal.var_name) or (literal.var_name in expanded_variables)

    def expansion_for(self, literal):
        s = str(literal)
        inv = literal.inverse()
        s_inv = str(inv)
        if (s not in self.sat_memory.reduced_formulas) and (s_inv not in self.sat_memory.reduced_formulas):
            raise Exception(
                "Neither " + s + ", nor " + s_inv + " have an associated reduced formula. Furthermore, "
                + literal.var_name + " is not a free variable.")

        if s in self.sat_memory.reduced_formulas:
            f = self.sat_memory.reduced_formulas[s]
        else:
            f = Not(self.sat_memory, self.sat_memory.reduced_formulas[s_inv]).simplified_formula()
            self.sat_memory.reduced_formulas[s] = f  # Or or And
        return f

    def insert_dependencies(self, result, o, expanded_so_far):
        if not self.is_atom(o, expanded_so_far):
            expansion = self.expansion_for(o)
            expanded_so_far.add(o.var_name)
            if expansion.is_or():
                for clause in self.sat_clauses_for_literal_equiv_or(o, expansion, expanded_so_far).as_list():
                    result.insert(clause)
            else:
                # print("EXPANSION: ",expansion)
                if expansion.is_and():
                    for clause in self.sat_clauses_for_literal_equiv_and(o, expansion, expanded_so_far).as_list():
                        result.insert(clause)

    def sat_clauses_for_and_formula(self, ff, expanded_so_far):
        result = SatClauses()
        ff = ff.simplified_formula()
        for o in ff.operands:
            assert o.is_literal()
            result.insert([int(o)])
            self.insert_dependencies(result, o, expanded_so_far)

        return result

    def sat_clauses_for_or_formula(self, ff, expanded_so_far, with_literal=None):
        # the last clause in the returned list corresponds to the OR formula
        current_clause = []
        result = SatClauses()
        for o in ff.operands:
            assert o.is_literal()
            current_clause.append(int(o))
            self.insert_dependencies(result, o, expanded_so_far)

        if with_literal is not None:
            current_clause.append(int(with_literal))
        result.insert(current_clause)
        return result

    def sat_clauses_for_literal_equiv_and(self, f, ff, expanded_so_far):
        """Returns CNF clauses for the formula f <=> ff

        :param f: literal
        :param ff: and formula (is_and()==True)
        :param expanded_so_far: a set of expanded literals so far
        :return:
        """

        # ff => f === -ff | f
        not_ff = Not(self.sat_memory, ff).simplified_formula()
        result = self.sat_clauses_for_or_formula(not_ff, expanded_so_far, int(f))
        # ^^^ result contains also clauses for resolving literals of the OR (because of De Morgan's law) formula -ff;
        # the last argument extends the last clause (containing not_ff.operands[0] | not_ff.operands[1] | ...) with f

        # f => ff === -f | +-ff.operands[0] | +-ff.operands[1] | ... except all -
        assert not ff.is_literal()  # literals are not reduced by literals in SAT memory

        if len(ff.operands) == 2:
            v = int(f)
            a = int(ff.operands[0])
            b = int(ff.operands[1])
            result.insert([-v, -a, b])
            result.insert([-v, a, -b])
            result.insert([-v, a, b])
            return result
        else:
            s = range(len(ff.operands))
            if len(s) > 2:
                logging.warning(
                    "The formula " + str(ff) + " has more than two AND operands, which may lead to exponential "
                                               "growth in clauses.")
            subsets = chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))
            v = int(f)
            for pos_literal_indices in subsets:
                clause = [-v]
                for i in s:
                    if i in pos_literal_indices:
                        clause.append(int(ff.operands[i]))
                    else:
                        clause.append(-int(ff.operands[i]))
                result.insert(clause)
            return result

    def sat_clauses_for_literal_equiv_or(self, f, ff, expanded_so_far):
        """Returns CNF clauses for the formula f <=> ff

        :param f: literal
        :param ff: or formula (is_or()==True)
        :param expanded_so_far: a set of expanded literals so far
        :return:
        """

        # f => ff === -f | ff.operands[0] | ff.operands[1] | ...
        # the last argument extends the last clause (containing ff.operands[0] | ff.operands[1] | ...) with -f
        result = self.sat_clauses_for_or_formula(ff, expanded_so_far, int(f.inverse()))
        # ^^^ result contains also clauses for resolving literals of the OR formula ff

        # ff => f === -ff | f === f | +-ff.operands[0] | +-ff.operands[1] | ... except all +
        assert not ff.is_literal()  # literals are not reduced by literals in SAT memory

        if len(ff.operands) == 2:
            v = int(f)
            a = int(ff.operands[0])
            b = int(ff.operands[1])
            result.insert([v, -a, -b])
            result.insert([v, -a, b])
            result.insert([v, a, -b])
            return result
        else:
            s = range(len(ff.operands))
            if len(s) > 2:
                logging.warning(
                    "The formula " + str(ff) + " has more than two OR operands, which may lead to exponential "
                                               "growth in clauses.")
            subsets = chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))
            v = int(f)
            for neg_literal_indices in subsets:
                clause = [v]
                for i in s:
                    if i in neg_literal_indices:
                        clause.append(-int(ff.operands[i]))
                    else:
                        clause.append(int(ff.operands[i]))
                result.insert(clause)
            return result

    def clauses(self):
        f = self.simplified_formula
        expanded_so_far = self.expanded_variables

        if f.is_constant():
            print("Warning: the given literal " + str(f) + " is a constant")
            if f.evaluation():
                return []  # empty CNF is True
            else:
                raise Exception("Unsatisfiable CNF " + str(f))

        if self.is_atom(f, expanded_so_far):
            return [[int(f)]]

        # not an atom - we have either a simplified and/or formula, or a literal that has to be expanded

        if f.is_and():
            return self.sat_clauses_for_and_formula(f, expanded_so_far).as_list()

        if f.is_or():
            return self.sat_clauses_for_or_formula(f, expanded_so_far).as_list()

        assert f.is_literal()
        # assert f not expanded
        assert not self.is_atom(f, expanded_so_far)

        ff = self.expansion_for(f)
        expanded_so_far.add(f.var_name)

        # assert: ff is not a Not formula, since De Morgan's law would be applied;
        # ff is not a literal, since it is impossible to reduce a literal as another literal in SAT memory
        assert ff.is_and() or ff.is_or()

        # adding equivalence: f <=> ff (linking f with its expansion ff)
        if ff.is_and():
            print("adding AND EQUIV: " + str(f) + "===" + str(ff))
            result = self.sat_clauses_for_literal_equiv_and(f, ff, expanded_so_far)
            result.insert([int(f)])
            return result.as_list()
        else:  # ff.is_or()
            print("adding OR EQUIV: " + str(f) + "===" + str(ff))
            result = SatClauses()
            result = self.sat_clauses_for_literal_equiv_or(f, ff, expanded_so_far)
            result.insert([int(f)])
            return result.as_list()
