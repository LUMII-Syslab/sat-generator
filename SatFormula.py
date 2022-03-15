#!/usr/bin/env python3

import abc


class SatFormula(metaclass=abc.ABCMeta):
    def __init__(self, sat_memory, operands):
        self.sat_memory = sat_memory
        self.operands = operands

    def simplified_literal(self):
        """
        Simplifies the formula to one of: conjunction of literals, disjunction of literals, literal, constant.

        :return:
            If the simplified formula is a conjunction or disjunction, returns a new or previously created Literal
            representing the simplified formula. Otherwise, returns the simplified formula itself,
            which is either a Literal, or a Constant.
        """
        f = self.simplified_formula()
        s = str(f)
        if s in self.sat_memory.literals:
            return self.sat_memory.literals[s]
        else:
            return self.sat_memory.allocate_for(f)
        pass

    @abc.abstractmethod
    def simplified_formula(self):
        """
        Simplifies the formula to one of: conjunction of literals, disjunction of literals, literal, constant.

        :return: conjunction of literals, disjunction of literals, literal, or constant
        """
        pass

    def is_constant(self):
        return False

    def is_literal(self):
        return False

    def is_negation(self):
        # returns True for negative literals and not(formula)
        return False

    def is_and(self):
        return False

    def is_or(self):
        return False

    @abc.abstractmethod
    def evaluation(self):
        """Evaluates the formula and returns the result.
        If previously cached in sat_memory, returns the cached value.
        If some free variable doesn't have a value, raises an Exception."""
        pass


class And(SatFormula):
    def __init__(self, sat_memory, operands):
        #if len(operands) <= 2:
            super().__init__(sat_memory, operands)
        #else:
        #    super().__init__(sat_memory, [operands[0], And(sat_memory, operands[1:])])

    def simplified_formula(self):
        l1 = []
        for o in self.operands:
            if o.is_and():
                for child in o.operands:
                    l1.append(child.simplified_literal())
            elif o.is_constant():
                if o.evaluation():
                    continue  # skip True
                else:
                    return Constant(self.sat_memory, False)
            else:
                l1.append(o.simplified_literal())
        if len(l1) == 0:
            return Constant(self.sat_memory, True)  # empty And is True (e.g., if all operands were True)
        if len(l1) == 1:
            return l1[0]
        f = And(self.sat_memory, l1)
        return f

    def is_and(self):
        return True

    def __str__(self):
        s = ""
        for o in self.operands:
            if len(s) == 0:
                s += str(o)
            else:
                s += "&" + str(o)
        return "{"+s+"}"

    def evaluation(self):
        s = str(self)
        if s in self.sat_memory.values:
            return self.sat_memory.values[s]

        for o in self.operands:
            if not o.evaluation():  # at least one operand is False
                self.sat_memory.values[s] = False
                return False

        # all operands are True
        self.sat_memory.values[s] = True
        return True


class Or(SatFormula):
    def __init__(self, sat_memory, operands):
        #if len(operands) <= 2:
            super().__init__(sat_memory, operands)
        #else:
        #    super().__init__(sat_memory, [operands[0], Or(sat_memory, operands[1:])])

    def simplified_formula(self):
        l1 = []
        for o in self.operands:
            if o.is_or():
                for child in o.operands:
                    l1.append(child.simplified_literal())
            elif o.is_constant():
                if o.evaluation():
                    return Constant(self.sat_memory, True)
                else:
                    continue  # skip False
            else:
                l1.append(o.simplified_literal())
        if len(l1) == 0:
            return Constant(self.sat_memory, False)  # empty Or is False (e.g., if all operands were False)
        if len(l1) == 1:
            return l1[0]
        f = Or(self.sat_memory, l1)
        return f

    def is_or(self):
        return True

    def __str__(self):
        s = ""
        for o in self.operands:
            if len(s) == 0:
                s += str(o)
            else:
                s += "|" + str(o)
        return "["+s+"]"

    def evaluation(self):
        s = str(self)
        if s in self.sat_memory.values:
            return self.sat_memory.values[s]

        for o in self.operands:
            if o.evaluation():  # at least one operand is True
                self.sat_memory.values[s] = True
                return True

        # all operands are False
        self.sat_memory.values[s] = False
        return False


class Xor(Or):
    def __init__(self, sat_memory, operands):
        if len(operands) < 2:
            raise Exception("Xor takes at least 2 operands but " + str(len(operands)) + " given.")
        if len(operands) == 2:
            operand1 = operands[1]
        else:
            operand1 = Xor(sat_memory, operands[1:])
        super().__init__(sat_memory, [
            And(sat_memory, [
                Not(sat_memory, operands[0]),
                operand1]),
            And(sat_memory, [
                operands[0],
                Not(sat_memory, operand1)]),
        ])


class Majority(Or):
    def __init__(self, sat_memory, operands):
        if len(operands) != 3:
            raise Exception("Majority takes exactly 3 operands but " + str(len(operands)) + " given.")
        super().__init__(sat_memory, [
            And(sat_memory, [operands[0], operands[1]]),
            And(sat_memory, [operands[2], Xor(sat_memory, [operands[0], operands[1]])])])


class Implication(Or):
    def __init__(self, sat_memory, operands):
        if len(operands) != 2:
            raise Exception("Implication takes exactly 2 operands but " + str(len(operands)) + " given.")
        # using the law: A=>B === not(A) or B
        super().__init__(sat_memory, [
                Not(sat_memory, operands[0]),
                operands[1]])


class Equivalence(And):
    def __init__(self, sat_memory, operands):
        if len(operands) != 2:
            raise Exception("Equivalence takes exactly 2 operands but " + str(len(operands)) + " given.")
        super().__init__(sat_memory, [
            Implication(sat_memory, operands),
            Implication(sat_memory, list(reversed(operands)))
        ])


class Constant(SatFormula):
    def __init__(self, sat_memory, value):
        super().__init__(sat_memory, [])
        self.value = value

    def simplified_formula(self):
        return self

    def simplified_literal(self):
        return self

    def is_constant(self):
        return True

    def __str__(self):
        return str(self.value)

    def inverse(self):
        return Constant(self.sat_memory, not self.value)

    def evaluation(self):
        return self.value


class Literal(SatFormula):
    def __init__(self, sat_memory, negation_flag, var_name, reduced_formula=None):
        # reduced_formula - if set, must correspond to the negation_flag
        super().__init__(sat_memory, [])
        self.negation_flag = negation_flag
        self.var_name = var_name
        if reduced_formula is not None:
            sat_memory.reduced_formulas[str(self)] = reduced_formula
            # TODO: check for different formulas

    def __int__(self):
        if self.negation_flag:
            return -int(self.var_name[1:])
        else:
            return int(self.var_name[1:])

    def simplified_formula(self):
        return self

    def simplified_literal(self):
        return self

    def inverse(self):
        return Literal(self.sat_memory, not self.negation_flag, self.var_name)

    def is_literal(self):
        return True

    def is_negation(self):
        return self.negation_flag

    def __str__(self):
        if self.negation_flag:
            return "-" + self.var_name
        else:
            return self.var_name

    def evaluation(self):
        s = str(self)

        if s in self.sat_memory.values:
            return self.sat_memory.values[s]

        if s in self.sat_memory.reduced_formulas:
            # via reduced_formula:
            reduced_formula = self.sat_memory.reduced_formulas[s]
            value = reduced_formula.evaluation()
            self.sat_memory.values[s] = value
            return value

        if self.negation_flag:
            if self.var_name in self.sat_memory.values:
                value = not self.sat_memory.values[self.var_name]
            else:
                if self.var_name in self.sat_memory.reduced_formulas:
                    value = not self.sat_memory.reduced_formulas[self.var_name].evaluation()
                else:
                    raise Exception(self.var_name + " does not have a value and does not represent a reduced sub-formula")
        else:
            if "-"+self.var_name in self.sat_memory.values:
                value = not self.sat_memory.values["-" + self.var_name]
            else:
                if "-"+self.var_name in self.sat_memory.reduced_formulas:
                    value = not self.sat_memory.reduced_formulas["-" + self.var_name].evaluation()
                else:
                    raise Exception(self.var_name + " does not have a value and does not represent a reduced sub-formula")

        self.sat_memory.values[s] = value
        return value


class Not(SatFormula):
    def __init__(self, sat_memory, operand):
        super().__init__(sat_memory, [operand])

    def simplified_formula(self):
        o = self.operands[0]
        if o.is_constant():
            return Constant(self.sat_memory, not o.evaluation())

        if o.is_literal():
            return Literal(self.sat_memory, not o.is_negation(), o.var_name)

        if o.is_negation():
            oo = o.operands[0]
            return oo.simplified_formula()

        # De Morgan's laws:
        if o.is_and():  # -(O1 & O2) = -O1 | -O2
            l1 = []
            for oo in o.operands:
                l1.append(Not(self.sat_memory, oo).simplified_literal())
            f = Or(self.sat_memory, l1).simplified_formula()
        elif o.is_or():  # -(O1 | O2) = -O1 & -O2
            l2 = []
            for oo in o.operands:
                l2.append(Not(self.sat_memory, oo).simplified_literal())
            f = And(self.sat_memory, l2).simplified_formula()
        else:
            raise Exception("unknown Not operand: "+str(o))
            # f = self
        return f

    def is_negation(self):
        return True

    def __str__(self):
        if self.operands[0].is_literal() or self.operands[0].is_constant():
            return "-"+str(self.operands[0])
        else:
            return "-(" + str(self.operands[0]) + ")"

    def evaluation(self):
        s = str(self)
        if s in self.sat_memory.values:
            return self.sat_memory.values[s]

        o = self.operands[0]
        value = not o.evaluation()
        self.sat_memory.values[s] = value
        return value
