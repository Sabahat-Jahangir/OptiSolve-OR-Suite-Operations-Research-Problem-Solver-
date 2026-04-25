# ============================================
# SIMPLEX + BRANCH AND BOUND (PURE PYTHON)
# ============================================

INF = 10**12
EPS = 1e-6

# -----------------------------
# SIMPLEX SOLVER (LP RELAXATION)
# -----------------------------
class Simplex:
    def __init__(self, c, A, b):
        self.n = len(c)          # variables
        self.m = len(A)          # constraints
        self.tableau = []

        # Build tableau
        for i in range(self.m):
            self.tableau.append(A[i] + [0]*self.m + [b[i]])
            self.tableau[i][self.n + i] = 1

        self.tableau.append([-ci for ci in c] + [0]*self.m + [0])
        self.rows = self.m + 1
        self.cols = self.n + self.m + 1

    def pivot(self, r, c):
        pivot_val = self.tableau[r][c]
        for j in range(self.cols):
            self.tableau[r][j] /= pivot_val

        for i in range(self.rows):
            if i != r:
                factor = self.tableau[i][c]
                for j in range(self.cols):
                    self.tableau[i][j] -= factor * self.tableau[r][j]

    def solve(self):
        while True:
            col = -1
            for j in range(self.cols - 1):
                if self.tableau[-1][j] < -EPS:
                    col = j
                    break
            if col == -1:
                break

            row = -1
            min_ratio = INF
            for i in range(self.m):
                if self.tableau[i][col] > EPS:
                    ratio = self.tableau[i][-1] / self.tableau[i][col]
                    if ratio < min_ratio:
                        min_ratio = ratio
                        row = i

            if row == -1:
                return None  # Unbounded

            self.pivot(row, col)

        solution = [0]*self.n
        for j in range(self.n):
            for i in range(self.m):
                if abs(self.tableau[i][j] - 1) < EPS:
                    solution[j] = self.tableau[i][-1]

        return solution, self.tableau[-1][-1]


# -----------------------------
# BRANCH AND BOUND
# -----------------------------
class BranchAndBound:
    def __init__(self, c, A, b, maximize=True):
        if not maximize:
            c = [-x for x in c]

        self.c = c
        self.A = A
        self.b = b
        self.best_value = -INF
        self.best_solution = None

    def is_integer(self, x):
        return abs(x - round(x)) < EPS

    def branch(self, A, b):
        simplex = Simplex(self.c, A, b)
        res = simplex.solve()

        if res is None:
            return

        sol, value = res
        if value <= self.best_value + EPS:
            return

        for i, x in enumerate(sol):
            if not self.is_integer(x):
                floor_x = int(x)
                ceil_x = floor_x + 1

                # Left branch: xi <= floor(x)
                A1 = A + [[0]*len(sol)]
                A1[-1][i] = 1
                b1 = b + [floor_x]

                # Right branch: xi >= ceil(x) → -xi <= -ceil(x)
                A2 = A + [[0]*len(sol)]
                A2[-1][i] = -1
                b2 = b + [-ceil_x]

                self.branch(A1, b1)
                self.branch(A2, b2)
                return

        self.best_value = value
        self.best_solution = sol

    def solve(self):
        self.branch(self.A, self.b)
        return self.best_solution, self.best_value


# -----------------------------
# USER INPUT
# -----------------------------
def main():
    print("INTEGER LINEAR PROGRAMMING (Branch & Bound)")
    print("-----------------------------------------")

    n = int(input("Number of variables: "))
    m = int(input("Number of constraints: "))

    print("Enter objective coefficients:")
    c = list(map(float, input().split()))

    typ = input("Maximize or Minimize (max/min): ").strip().lower()
    maximize = (typ == "max")

    A = []
    b = []

    print("Enter constraints:")
    print("Format: coefficients <= RHS | >= RHS | = RHS")

    for _ in range(m):
        parts = input().split()
        coeffs = list(map(float, parts[:n]))
        sign = parts[n]
        rhs = float(parts[n+1])

        if sign == "<=":
            A.append(coeffs)
            b.append(rhs)
        elif sign == ">=":
            A.append([-x for x in coeffs])
            b.append(-rhs)
        else:  # =
            A.append(coeffs)
            b.append(rhs)
            A.append([-x for x in coeffs])
            b.append(-rhs)

    solver = BranchAndBound(c, A, b, maximize)
    sol, val = solver.solve()

    print("\nOPTIMAL INTEGER SOLUTION")
    print("------------------------")
    for i, x in enumerate(sol):
        print(f"x{i+1} = {int(round(x))}")
    print("Objective =", val if maximize else -val)


# -----------------------------
if __name__ == "__main__":
    main()
