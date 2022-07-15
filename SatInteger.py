#!/usr/bin/env python3

from SatFormula import *
import traceback


class SatInteger:
    def __init__(self, sat_memory, literals):
        """ Initializes an integer with bits corresponding to literals.
        for positive literal x_i, bit_i = 1 means x_i = True;
        for negative literal -x_i, bit_i = 1 means x_i = False (-x_i = True)

        :param sat_memory:
        :param literals:
        """
        self.sat_memory = sat_memory
        self.n_bits = len(literals)
        self.literals = list(map(lambda x: self.sat_memory.literal(str(x)), literals))

    def clipped(self, n_bits):
        if self.n_bits <= n_bits:
            zero = Constant(self.sat_memory, False)
            return SatInteger(self.sat_memory, self.literals + [zero] * (n_bits - self.n_bits))
        else:
            return SatInteger(self.sat_memory, self.literals[:n_bits])

    def extended(self, literals):
        return SatInteger(self.sat_memory, self.literals + literals)

    def left_shifted(self, k_bits):
        zero = Constant(self.sat_memory, False)
        return SatInteger(self.sat_memory, [zero] * k_bits + self.literals)

    def right_shifted(self, k_bits):
        return SatInteger(self.sat_memory, self.literals[k_bits:])

    def and_with(self, other):
        if self.n_bits != other.n_bits:
            raise Exception("Cannot perform bitwise AND on arguments of different length")
        result = []
        for i in range(self.n_bits):
            result.append(And(self.sat_memory, [self.literals[i], other.literals[i]]).simplified_literal())
        return SatInteger(self.sat_memory, result)

    def negation(self):
        # inverse bits
        inverse_literals = list(map(lambda lit: lit.inverse(), self.literals))

        # result = inverse + 1

        #                      1  +
        # carry   = ....c1,c0
        # inverse = ....i2,i1,i0
        # ----------------------
        # result  = ....r2,r1,r0

        carry = [inverse_literals[0]]
        r0 = inverse_literals[0].inverse()
        result = [r0]
        for i in range(1, self.n_bits):
            # computing: carry[i],result[i] <- inverse_literals[i] + carry[i-1]
            carry_formula = And(self.sat_memory, [inverse_literals[i], carry[i - 1]])
            result_formula = Xor(self.sat_memory, [inverse_literals[i], carry[i - 1]])

            result.append(result_formula.simplified_literal())
            if i < self.n_bits - 1:  # the next carry bit, ignoring the last one
                carry.append(carry_formula.simplified_literal())
        return SatInteger(self.sat_memory, result)

    def sum_with(self, other):
        if self.n_bits != other.n_bits:
            raise Exception("Could not sum numbers with different number of bits (" +
                            str(self.n_bits) + " and " + str(other.n_bits) + ")")
        # carry   = ....c1,c0
        # self    = ....i2,i1,i0 +
        # other   = ....j2,j1,j0
        # ----------------------
        # result  = ....r2,r1,r0

        carry = [And(self.sat_memory, [self.literals[0], other.literals[0]]).simplified_literal()]
        r0 = Xor(self.sat_memory, [self.literals[0], other.literals[0]])  # half adder
        result = [r0.simplified_literal()]

        for i in range(1, self.n_bits):
            # implementing full adder
            result_formula = Xor(self.sat_memory, [
                self.literals[i],
                Xor(self.sat_memory, [
                    other.literals[i],
                    carry[i - 1]])
            ])

            carry_formula = Majority(self.sat_memory, [
                self.literals[i],
                other.literals[i],
                carry[i - 1]])

            result.append(result_formula.simplified_literal())

            if i < self.n_bits - 1:  # the next carry bit, ignoring the last one
                carry.append(carry_formula.simplified_literal())

        return SatInteger(self.sat_memory, result)

    def product_with(self, other):
        if self.n_bits != other.n_bits:
            raise Exception("Could not multiply numbers with different number of bits (" +
                            str(self.n_bits) + " and " + str(other.n_bits) + ")")
        if self.n_bits == 1:
            product_lo = And(self.sat_memory, [self.literals[0], other.literals[0]]).simplified_literal()
            product_hi = Constant(self.sat_memory, False)
            return SatInteger(self.sat_memory, [product_lo, product_hi])

        if self.n_bits % 2 == 1:
            raise Exception("Currently we support only 2^k bits for Karatsuba multiplication but "
                            + str(self) + " has " + str(self.n_bits) + " bits")

        half_bits = self.n_bits // 2
        zero = Constant(self.sat_memory, False)
        u0 = SatInteger(self.sat_memory, self.literals[0:half_bits])
        u1 = SatInteger(self.sat_memory, self.literals[half_bits:self.n_bits])
        u0z = SatInteger(self.sat_memory, self.literals[0:half_bits] + [zero])
        u1z = SatInteger(self.sat_memory, self.literals[half_bits:self.n_bits] + [zero])

        v0 = SatInteger(self.sat_memory, other.literals[0:half_bits])
        v1 = SatInteger(self.sat_memory, other.literals[half_bits:other.n_bits])
        v0z = SatInteger(self.sat_memory, other.literals[0:half_bits] + [zero])
        v1z = SatInteger(self.sat_memory, other.literals[half_bits:other.n_bits] + [zero])

        u1_minus_u0 = u1z.sum_with(u0z.negation())
        v0_minus_v1 = v0z.sum_with(v1z.negation())

        # remove the sign/overflow bit
        sign1 = u1_minus_u0.literals[-1]
        sign2 = v0_minus_v1.literals[-1]
        u1_minus_u0 = u1_minus_u0.clipped(u1_minus_u0.n_bits - 1)
        v0_minus_v1 = v0_minus_v1.clipped(v0_minus_v1.n_bits - 1)

        # (sign(arg1) xor sign(arg2) and (arg1 != 0) and (arg2 != 0)
        xor_signs = And(self.sat_memory,
                        [Xor(self.sat_memory, [sign1, sign2]),
                         Or(self.sat_memory, u1_minus_u0.literals),
                         Or(self.sat_memory, v0_minus_v1.literals)])
        xor_signs = xor_signs.simplified_literal()

        u0v0 = u0.product_with(v0)
        u1v1 = u1.product_with(v1)
        mixed = u1_minus_u0.product_with(v0_minus_v1)

        # important: we add shifted product of ...11111 * u1_minus_u0, which is the same as shifted -u1_minus_u0
        mixed = mixed.sum_with(u1_minus_u0.negation().and_with(
                SatInteger(self.sat_memory, [sign2] * half_bits))
                .left_shifted(half_bits))
        mixed = mixed.sum_with(v0_minus_v1.negation().and_with(
                SatInteger(self.sat_memory, [sign1] * half_bits))
                .left_shifted(half_bits))

        result = SatInteger(self.sat_memory, u0v0.literals + u1v1.literals)  # u1v1|u0v0

        mixed0 = mixed.clipped(self.n_bits).extended([xor_signs] * half_bits)

        mixed1 = mixed0.sum_with(u0v0.clipped(self.n_bits + half_bits))
        mixed2 = mixed1.sum_with(u1v1.clipped(self.n_bits + half_bits))
        mixed = SatInteger(self.sat_memory, [zero] * half_bits + mixed2.literals)
        result = result.sum_with(mixed)

        return result

    def __str__(self):
        try:
            s = ""
            for i in reversed(range(len(self.literals))):
                s += "1" if self.literals[i].evaluation() else "0"
            return s
        except Exception as e:
            # traceback.print_exc()
            s = ""
            for i in reversed(range(len(self.literals))):
                if len(s) > 0:
                    s += ","
                s += str(self.literals[i])
            return s
            # if we want to see details:
            # return s + " (" + str(e) + ")"
