class SatClauses:
    def __init__(self):
        self.existing_clauses_keys = set()
        self.clauses = []

    def insert(self, clause):
        new_clause = []
        # remove x and -x:
        for x in clause:
            if -int(x) in clause:
                return  # both x and -x are found, the clause is always True
            else:
                new_clause.append(int(x))

        if len(new_clause) == 0:
            return  # do not add an empty clause

        new_clause.sort()

        key = str(new_clause)
        if key not in self.existing_clauses_keys:
            self.existing_clauses_keys.add(key)
            self.clauses.append(new_clause)

    def as_list(self):
        return list(self.clauses)
