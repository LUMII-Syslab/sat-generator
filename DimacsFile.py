#!/usr/bin/env python3

class DimacsFile:
    def __init__(self, filename, n_vars=0, clauses=[]):
        self.filename = filename
        self.n_vars = n_vars
        self.i_clauses = clauses

    def load(self):
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()

        self.n_vars = 0
        self.i_clauses = []
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            i = line.find("p cnf")
            if i >= 0:
                line = line[len("p cnf"):].strip()
                i = line.find(" ")
                line = line[:i]
                self.n_vars = int(line)
                continue
            if line[0].isalpha():
                continue

            clause = []
            for s in line.split():
                i = int(s)
                if i == 0:
                    break  # end of clause
                clause.append(i)
            self.add_clause(clause)

    def number_of_vars(self):
        return self.n_vars

    def number_of_clauses(self):
        return len(self.i_clauses)

    def clauses(self):
        return self.i_clauses

    def add_clause(self, clause):
        self.add_clauses([clause])

    def add_clauses(self, clauses):
        for c in clauses:
            # if the clause contains index abs(i) > nVars, update nVars
            for i in c:
                self.n_vars = max(self.n_vars, abs(i))
            # append the new clause:
            self.i_clauses.append(c)

    def store(self, *comments):
        f = open(self.filename, 'w')
        for c in comments:
            f.write("c " + c + "\n")
        f.write("p cnf " + str(self.number_of_vars()) + " " + str(self.number_of_clauses()) + "\n")

        for c in self.clauses():
            s = ""
            for i in c:
                s += str(i) + " "
            s += "0"
            f.write(s + "\n")
        f.close()


if __name__ == "__main__":  # test
    df = DimacsFile("in.cnf")
    df.load()
    print(df.number_of_vars(), df.number_of_clauses(), df.clauses())

    df2 = DimacsFile("out.cnf", df.number_of_vars(), df.clauses())
    df2.add_clause([100, -99])
    df2.store("added clause [100, 99]", "the number of vars should increase to 100")
