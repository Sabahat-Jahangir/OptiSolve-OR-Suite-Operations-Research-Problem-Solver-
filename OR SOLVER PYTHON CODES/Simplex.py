def print_matrix(matrix, columns=None, index=None):
    """Print matrix in a formatted table"""
    if columns is None:
        columns = [f"Col{i}" for i in range(len(matrix[0]))]
    
    if index is None:
        index = [f"Row{i}" for i in range(len(matrix))]
    
    # Calculate column widths
    col_widths = [max(len(str(col)), 8) for col in columns]
    for row in matrix:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(f"{val:.4f}"))
    
    # Print header
    header = f"{'':>8} |"
    for i, col in enumerate(columns):
        header += f" {col:>{col_widths[i]}} |"
    print(header)
    print("-" * len(header))
    
    # Print rows
    for i, row in enumerate(matrix):
        row_str = f"{index[i]:>8} |"
        for j, val in enumerate(row):
            if isinstance(val, (int, float)):
                row_str += f" {val:>{col_widths[j]}.4f} |"
            else:
                row_str += f" {val:>{col_widths[j]}} |"
        print(row_str)


def matrix_multiply(A, B):
    """Multiply matrix A by matrix B"""
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])
    
    result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    
    return result


def matrix_vector_multiply(A, b):
    """Multiply matrix A by vector b"""
    result = [0.0] * len(A)
    for i in range(len(A)):
        for j in range(len(b)):
            result[i] += A[i][j] * b[j]
    return result


class SimplexSolver:
    
    def __init__(self):
        self.tableau = None
        self.basic_vars = []
        self.non_basic_vars = []
        self.var_names = []
        self.num_decision_vars = 0
        self.num_constraints = 0
        self.is_maximization = True
        self.iteration = 0
        self.M = 1e6
        self.history = []
        self.epsilon = 1e-10
        
    def get_problem_input(self):
        print("\n" + "="*80)
        print("SIMPLEX METHOD - PROBLEM INPUT")
        print("="*80)
        
        problem_type = input("\nIs this a (1) Maximization or (2) Minimization problem? [1/2]: ").strip()
        self.is_maximization = (problem_type == '1')
        
        self.num_decision_vars = int(input("Enter number of decision variables: "))
        self.num_constraints = int(input("Enter number of constraints: "))
        
        print(f"\nEnter objective function coefficients (c1, c2, ..., c{self.num_decision_vars}):")
        obj_coeffs = list(map(float, input("Coefficients (space-separated): ").split()))
        
        constraints = []
        constraint_types = []
        rhs_values = []
        
        print("\nEnter constraints:")
        print("Format: coefficients (space-separated), then type (<=, >=, =), then RHS value")
        
        for i in range(self.num_constraints):
            print(f"\nConstraint {i+1}:")
            coeffs = list(map(float, input(f"  Coefficients for x1 to x{self.num_decision_vars} (space-separated): ").split()))
            ctype = input("  Constraint type (<=, >=, =): ").strip()
            rhs = float(input("  RHS value: "))
            
            constraints.append(coeffs)
            constraint_types.append(ctype)
            rhs_values.append(rhs)
        
        return obj_coeffs, constraints, constraint_types, rhs_values
    
    def setup_initial_tableau(self, obj_coeffs, constraints, constraint_types, rhs_values):
        """Setup the initial simplex tableau with slack, surplus, and artificial variables"""
        
        # Count variables needed
        num_slack = 0
        num_artificial = 0
        
        for ct in constraint_types:
            if ct == '<=':
                num_slack += 1
            elif ct == '>=':
                num_slack += 1  # surplus
                num_artificial += 1
            elif ct == '=':
                num_artificial += 1
        
        total_vars = self.num_decision_vars + num_slack + num_artificial
        
        # Create variable names
        self.var_names = [f'x{i+1}' for i in range(self.num_decision_vars)]
        
        slack_idx = 0
        artificial_idx = 0
        
        for ct in constraint_types:
            if ct == '<=':
                slack_idx += 1
                self.var_names.append(f's{slack_idx}')
            elif ct == '>=':
                slack_idx += 1
                self.var_names.append(f's{slack_idx}')
                artificial_idx += 1
                self.var_names.append(f'a{artificial_idx}')
            elif ct == '=':
                artificial_idx += 1
                self.var_names.append(f'a{artificial_idx}')
        
        # Initialize tableau
        num_rows = self.num_constraints + 1
        num_cols = total_vars + 1
        
        self.tableau = [[0.0 for _ in range(num_cols)] for _ in range(num_rows)]
        
        # Setup objective function row (row 0)
        if self.is_maximization:
            for i in range(self.num_decision_vars):
                self.tableau[0][i] = -obj_coeffs[i]
        else:
            for i in range(self.num_decision_vars):
                self.tableau[0][i] = obj_coeffs[i]
        
        # Add Big M for artificial variables
        artificial_col_start = self.num_decision_vars + num_slack
        for i in range(num_artificial):
            if self.is_maximization:
                self.tableau[0][artificial_col_start + i] = self.M
            else:
                self.tableau[0][artificial_col_start + i] = self.M
        
        # Setup constraint rows
        slack_col = self.num_decision_vars
        artificial_col = self.num_decision_vars + num_slack
        
        self.basic_vars = []
        
        for i, (coeffs, ct, rhs) in enumerate(zip(constraints, constraint_types, rhs_values)):
            row_idx = i + 1
            
            # Handle negative RHS
            if rhs < 0:
                coeffs = [-c for c in coeffs]
                rhs = -rhs
                # Flip constraint type
                if ct == '<=':
                    ct = '>='
                elif ct == '>=':
                    ct = '<='
            
            # Set constraint coefficients
            for j in range(self.num_decision_vars):
                self.tableau[row_idx][j] = coeffs[j]
            
            # Set RHS
            self.tableau[row_idx][-1] = rhs
            
            # Add slack/surplus/artificial variables
            if ct == '<=':
                self.tableau[row_idx][slack_col] = 1
                self.basic_vars.append(self.var_names[slack_col])
                slack_col += 1
                
            elif ct == '>=':
                self.tableau[row_idx][slack_col] = -1  # surplus
                slack_col += 1
                self.tableau[row_idx][artificial_col] = 1  # artificial
                self.basic_vars.append(self.var_names[artificial_col])
                artificial_col += 1
                
            elif ct == '=':
                self.tableau[row_idx][artificial_col] = 1  # artificial
                self.basic_vars.append(self.var_names[artificial_col])
                artificial_col += 1
        
        # Eliminate artificial variables from Z row (Big M method)
        for i, bv in enumerate(self.basic_vars):
            if bv.startswith('a'):
                col_idx = self.var_names.index(bv)
                if abs(self.tableau[0][col_idx]) > self.epsilon:
                    # Subtract M times the constraint row from Z row
                    multiplier = self.tableau[0][col_idx]
                    for j in range(len(self.tableau[0])):
                        self.tableau[0][j] -= multiplier * self.tableau[i+1][j]
        
        self.non_basic_vars = [v for v in self.var_names if v not in self.basic_vars]
        
    def display_tableau(self, title="Current Tableau"):
        """Display the simplex tableau"""
        print(f"\n{title}")
        print("=" * 120)
        
        headers = self.var_names + ['RHS']
        row_labels = ['Z'] + self.basic_vars
        
        print_matrix(self.tableau, headers, row_labels)
        print("=" * 120)
        
    def find_pivot_column(self):
        """Find the entering variable (pivot column) using most negative coefficient"""
        z_row = self.tableau[0][:-1]
        
        # For maximization: most negative coefficient
        # For minimization: most negative coefficient
        min_val = min(z_row)
        
        if min_val >= -self.epsilon:
            return -1  # Optimal solution found
        
        return z_row.index(min_val)
    
    def find_pivot_row(self, pivot_col):
        """Find the leaving variable (pivot row) using minimum ratio test"""
        ratios = []
        
        for i in range(1, len(self.tableau)):
            if self.tableau[i][pivot_col] > self.epsilon:
                ratio = self.tableau[i][-1] / self.tableau[i][pivot_col]
                if ratio >= 0:  # Only consider non-negative ratios
                    ratios.append((ratio, i))
        
        if not ratios:
            return -1  # Unbounded solution
        
        # Select minimum ratio (with tie-breaking)
        min_ratio_value = min(r[0] for r in ratios)
        min_ratios = [r for r in ratios if abs(r[0] - min_ratio_value) < self.epsilon]
        
        # Return the first occurrence
        return min_ratios[0][1]
    
    def perform_pivot_operation(self, pivot_row, pivot_col):
        """Perform pivot operation (Gauss-Jordan elimination)"""
        pivot_element = self.tableau[pivot_row][pivot_col]
        
        # Divide pivot row by pivot element
        for j in range(len(self.tableau[pivot_row])):
            self.tableau[pivot_row][j] /= pivot_element
        
        # Eliminate pivot column in other rows
        for i in range(len(self.tableau)):
            if i != pivot_row:
                factor = self.tableau[i][pivot_col]
                for j in range(len(self.tableau[i])):
                    self.tableau[i][j] -= factor * self.tableau[pivot_row][j]
        
        # Update basic variables
        leaving_var = self.basic_vars[pivot_row - 1]
        entering_var = self.var_names[pivot_col]
        self.basic_vars[pivot_row - 1] = entering_var
        
        # Update non-basic variables
        self.non_basic_vars = [v for v in self.var_names if v not in self.basic_vars]
        
        return entering_var, leaving_var
    
    def solve(self):
        """Solve the LP problem using simplex method"""
        self.iteration = 0
        print("\n" + "="*80)
        print("SIMPLEX METHOD - SOLUTION PROCESS")
        print("="*80)
        
        self.display_tableau(f"Initial Tableau (Iteration {self.iteration})")
        self.history.append([row[:] for row in self.tableau])
        
        max_iterations = 100
        
        while self.iteration < max_iterations:
            # Find pivot column
            pivot_col = self.find_pivot_column()
            
            if pivot_col == -1:
                print("\n" + "="*80)
                print("*** OPTIMAL SOLUTION FOUND ***")
                print("="*80)
                break
            
            # Find pivot row
            pivot_row = self.find_pivot_row(pivot_col)
            
            if pivot_row == -1:
                print("\n" + "="*80)
                print("*** UNBOUNDED SOLUTION ***")
                print("="*80)
                print("The problem has no finite optimal solution.")
                return None
            
            self.iteration += 1
            
            print(f"\n{'='*80}")
            print(f"ITERATION {self.iteration}")
            print('='*80)
            print(f"Pivot Column: {self.var_names[pivot_col]} (column {pivot_col})")
            print(f"Pivot Row: {self.basic_vars[pivot_row-1]} (row {pivot_row})")
            print(f"Pivot Element: {self.tableau[pivot_row][pivot_col]:.4f}")
            
            # Perform pivot operation
            entering, leaving = self.perform_pivot_operation(pivot_row, pivot_col)
            print(f"Entering Variable: {entering}")
            print(f"Leaving Variable: {leaving}")
            
            self.display_tableau(f"Tableau after Iteration {self.iteration}")
            self.history.append([row[:] for row in self.tableau])
        
        if self.iteration >= max_iterations:
            print("\n*** Maximum iterations reached! ***")
            return None
        
        return self.get_solution()
    
    def solve_n_iterations(self, n_iterations):
        """Solve for exactly n iterations and show detailed steps"""
        self.iteration = 0
        print("\n" + "="*80)
        print(f"SIMPLEX METHOD - SOLVING {n_iterations} ITERATION(S)")
        print("="*80)
        
        print("\n*** SOLUTION AT ITERATION 0 (Initial BFS) ***")
        self.display_tableau(f"Iteration {self.iteration}")
        
        print("\nCurrent Solution:")
        for i, bv in enumerate(self.basic_vars):
            print(f"  {bv} = {self.tableau[i+1][-1]:.4f}")
        for v in self.non_basic_vars:
            print(f"  {v} = 0")
        print(f"  Z = {self.tableau[0][-1]:.4f}")
        
        self.history.append([row[:] for row in self.tableau])
        
        for iter_count in range(n_iterations):
            pivot_col = self.find_pivot_column()
            
            if pivot_col == -1:
                print(f"\n*** OPTIMAL SOLUTION REACHED at iteration {self.iteration} ***")
                break
            
            pivot_row = self.find_pivot_row(pivot_col)
            
            if pivot_row == -1:
                print("\n*** UNBOUNDED SOLUTION ***")
                return None
            
            self.iteration += 1
            
            print(f"\n" + "="*80)
            print(f"ITERATION {self.iteration}")
            print("="*80)
            
            print(f"\nStep 1: Identify Entering Variable")
            print("  Looking for most negative coefficient in Z row:")
            z_row = self.tableau[0][:-1]
            for j, coeff in enumerate(z_row):
                if coeff < -self.epsilon:
                    print(f"    {self.var_names[j]}: {coeff:.4f}")
            print(f"  Most negative: {self.var_names[pivot_col]} = {self.tableau[0][pivot_col]:.4f}")
            
            print(f"\nStep 2: Minimum Ratio Test (Leaving Variable)")
            print(f"  For entering variable {self.var_names[pivot_col]}:")
            for i in range(1, len(self.tableau)):
                if self.tableau[i][pivot_col] > self.epsilon:
                    ratio = self.tableau[i][-1] / self.tableau[i][pivot_col]
                    print(f"    {self.basic_vars[i-1]}: {self.tableau[i][-1]:.4f} / {self.tableau[i][pivot_col]:.4f} = {ratio:.4f}")
                else:
                    print(f"    {self.basic_vars[i-1]}: Not eligible (coefficient ≤ 0)")
            
            print(f"\nStep 3: Pivot Operation")
            print(f"  Pivot Element: {self.tableau[pivot_row][pivot_col]:.4f}")
            print(f"  Location: Row {pivot_row}, Column {pivot_col}")
            
            entering, leaving = self.perform_pivot_operation(pivot_row, pivot_col)
            print(f"  {entering} enters the basis")
            print(f"  {leaving} leaves the basis")
            
            print(f"\n*** SOLUTION AFTER ITERATION {self.iteration} ***")
            self.display_tableau(f"Tableau after Iteration {self.iteration}")
            
            print(f"\nCurrent Solution:")
            for i, bv in enumerate(self.basic_vars):
                print(f"  {bv} = {self.tableau[i+1][-1]:.4f}")
            for v in self.non_basic_vars:
                print(f"  {v} = 0")
            print(f"  Z = {self.tableau[0][-1]:.4f}")
            
            self.history.append([row[:] for row in self.tableau])
        
        return self.get_solution()
    
    def get_solution(self):
        """Extract the solution from the final tableau"""
        solution = {}
        
        for var in self.var_names:
            if var in self.basic_vars:
                row_idx = self.basic_vars.index(var) + 1
                solution[var] = self.tableau[row_idx][-1]
            else:
                solution[var] = 0
        
        z_value = self.tableau[0][-1]
        
        # Adjust Z value for minimization if needed
        if not self.is_maximization:
            z_value = self.tableau[0][-1]
        
        print("\n" + "="*80)
        print("OPTIMAL SOLUTION")
        print("="*80)
        
        print("\nDecision Variables:")
        for i in range(self.num_decision_vars):
            var = f'x{i+1}'
            print(f"  {var} = {solution.get(var, 0):.4f}")
        
        if self.is_maximization:
            print(f"\nMaximum Z value: {z_value:.4f}")
        else:
            print(f"\nMinimum Z value: {z_value:.4f}")
        
        print(f"\nBasic Variables: {self.basic_vars}")
        print(f"Non-Basic Variables: {self.non_basic_vars}")
        
        # Check for artificial variables in basis
        artificial_in_basis = [v for v in self.basic_vars if v.startswith('a')]
        if artificial_in_basis:
            print(f"\n⚠ WARNING: Artificial variables in basis: {artificial_in_basis}")
            print("This may indicate an infeasible problem.")
        
        return solution, z_value
    
    def sensitivity_analysis(self):
        """Perform sensitivity analysis on the optimal solution"""
        print("\n" + "="*80)
        print("SENSITIVITY ANALYSIS")
        print("="*80)
        
        while True:
            print("\nSensitivity Analysis Options:")
            print("1. Change in RHS (Resource Availability)")
            print("2. Change in Objective Coefficient")
            print("3. Add New Constraint")
            print("4. Add New Variable")
            print("5. Shadow Prices and Ranges")
            print("6. Return to Main Menu")
            
            choice = input("\nSelect option [1-6]: ").strip()
            
            if choice == '1':
                self.rhs_sensitivity()
            elif choice == '2':
                self.objective_coefficient_sensitivity()
            elif choice == '3':
                self.add_new_constraint()
            elif choice == '4':
                self.add_new_variable()
            elif choice == '5':
                self.shadow_price_analysis()
            elif choice == '6':
                break
            else:
                print("Invalid choice!")
    
    def shadow_price_analysis(self):
        """Analyze shadow prices for all constraints"""
        print("\n" + "="*80)
        print("SHADOW PRICE ANALYSIS")
        print("="*80)
        
        print("\nShadow prices indicate the rate of change in the objective")
        print("function value per unit change in the RHS of constraints.")
        
        print(f"\n{'Constraint':<15} {'Shadow Price':<15} {'Interpretation'}")
        print("-" * 70)
        
        for i in range(self.num_constraints):
            # Shadow price is the coefficient of slack variable in Z row
            slack_var = f's{i+1}'
            if slack_var in self.var_names:
                col_idx = self.var_names.index(slack_var)
                shadow_price = -self.tableau[0][col_idx] if self.is_maximization else self.tableau[0][col_idx]
                
                if abs(shadow_price) < self.epsilon:
                    interpretation = "Non-binding constraint (slack available)"
                elif shadow_price > 0:
                    interpretation = "Binding constraint (valuable resource)"
                else:
                    interpretation = "Binding constraint (costly resource)"
                
                print(f"Constraint {i+1:<4} {shadow_price:>14.4f}  {interpretation}")
    
    def rhs_sensitivity(self):
        """Analyze sensitivity to RHS changes"""
        print("\n" + "="*80)
        print("RHS SENSITIVITY ANALYSIS")
        print("="*80)
        
        constraint_num = int(input("\nEnter constraint number (1, 2, 3, ...): ")) - 1
        
        if constraint_num < 0 or constraint_num >= self.num_constraints:
            print("Invalid constraint number!")
            return
        
        slack_var = f's{constraint_num+1}'
        if slack_var not in self.var_names:
            print("Cannot find corresponding slack variable!")
            return
        
        col_idx = self.var_names.index(slack_var)
        shadow_price = -self.tableau[0][col_idx]
        
        print(f"\nConstraint {constraint_num+1} Analysis:")
        print(f"Shadow Price: {shadow_price:.4f}")
        
        if self.is_maximization:
            print(f"Interpretation: Each unit increase in RHS changes Z by {shadow_price:.4f}")
        else:
            print(f"Interpretation: Each unit increase in RHS changes Z by {-shadow_price:.4f}")
        
        # Get current RHS value
        current_rhs = self.tableau[constraint_num + 1][-1]
        print(f"Current RHS value: {current_rhs:.4f}")
        
        # Calculate feasibility range
        print("\nTo maintain feasibility, we need to ensure all basic variables remain non-negative.")
        print("The allowable range can be calculated using the column of the slack variable.")
    
    def objective_coefficient_sensitivity(self):
        """Analyze sensitivity to objective coefficient changes"""
        print("\n" + "="*80)
        print("OBJECTIVE COEFFICIENT SENSITIVITY ANALYSIS")
        print("="*80)
        
        var_num = int(input("\nEnter variable number (1, 2, 3, ...): ")) - 1
        
        if var_num < 0 or var_num >= self.num_decision_vars:
            print("Invalid variable number!")
            return
        
        var_name = f'x{var_num + 1}'
        
        if var_name in self.basic_vars:
            print(f"\n{var_name} is a BASIC variable")
            row_idx = self.basic_vars.index(var_name) + 1
            current_value = self.tableau[row_idx][-1]
            print(f"Current value: {var_name} = {current_value:.4f}")
            print(f"Reduced cost: 0 (basic variable)")
            
        else:
            print(f"\n{var_name} is a NON-BASIC variable")
            print(f"Current value: {var_name} = 0")
            reduced_cost = self.tableau[0][var_num]
            print(f"Reduced cost: {reduced_cost:.4f}")
            
            if self.is_maximization:
                if reduced_cost >= 0:
                    print(f"This variable is not in the solution because its reduced cost is non-negative.")
                    print(f"The objective coefficient would need to increase by at least {abs(reduced_cost):.4f}")
                    print(f"for this variable to enter the basis.")
    
    def add_new_constraint(self):
        """Add a new constraint to the optimal solution"""
        print("\n" + "="*80)
        print("ADDING NEW CONSTRAINT")
        print("="*80)
        
        print(f"\nEnter coefficients for new constraint (x1 to x{self.num_decision_vars}):")
        coeffs = list(map(float, input("Coefficients (space-separated): ").split()))
        
        ctype = input("Constraint type (<=, >=, =): ").strip()
        rhs = float(input("RHS value: "))
        
        # Evaluate constraint at current solution
        current_solution = {}
        for i, var in enumerate(self.var_names[:self.num_decision_vars]):
            if var in self.basic_vars:
                row_idx = self.basic_vars.index(var) + 1
                current_solution[var] = self.tableau[row_idx][-1]
            else:
                current_solution[var] = 0
        
        print(f"\nCurrent Optimal Solution:")
        for var, val in current_solution.items():
            print(f"  {var} = {val:.4f}")
        
        lhs_value = sum(coeffs[i] * current_solution[f'x{i+1}'] for i in range(self.num_decision_vars))
        
        print(f"\nEvaluating new constraint:")
        print(f"LHS = {lhs_value:.4f}")
        print(f"RHS = {rhs:.4f}")
        
        satisfied = False
        if ctype == '<=':
            satisfied = lhs_value <= rhs + self.epsilon
            slack = rhs - lhs_value
            print(f"Slack = {slack:.4f}")
        elif ctype == '>=':
            satisfied = lhs_value >= rhs - self.epsilon
            surplus = lhs_value - rhs
            print(f"Surplus = {surplus:.4f}")
        elif ctype == '=':
            satisfied = abs(lhs_value - rhs) < self.epsilon
            diff = lhs_value - rhs
            print(f"Difference = {diff:.4f}")
        
        if satisfied:
            print(f"\n✓ Constraint is SATISFIED by current solution")
            print("The optimal solution remains unchanged.")
        else:
            print(f"\n✗ Constraint is VIOLATED by current solution")
            print("Dual Simplex method would be needed to find new optimal solution.")
            print("The current solution is no longer feasible.")
    
    def add_new_variable(self):
        """Add a new variable to the problem"""
        print("\n" + "="*80)
        print("ADDING NEW VARIABLE")
        print("="*80)
        
        new_var_name = input("\nEnter name for new variable (e.g., x_new): ").strip()
        obj_coeff = float(input(f"Enter objective coefficient for {new_var_name}: "))
        
        print(f"\nEnter constraint coefficients for {new_var_name}:")
        print(f"(One coefficient for each of the {self.num_constraints} constraints)")
        constraint_coeffs = list(map(float, input("Coefficients (space-separated): ").split()))
        
        if len(constraint_coeffs) != self.num_constraints:
            print("Error: Number of coefficients doesn't match number of constraints!")
            return
        
        # Calculate reduced cost for new variable
        print(f"\nCalculating if {new_var_name} should enter the basis...")
        
        # Get shadow prices (dual variables)
        dual_vars = []
        for i in range(self.num_constraints):
            slack_var = f's{i+1}'
            if slack_var in self.var_names:
                col_idx = self.var_names.index(slack_var)
                dual_vars.append(-self.tableau[0][col_idx])
            else:
                dual_vars.append(0)
        
        print(f"Shadow prices (dual variables): {[f'{d:.4f}' for d in dual_vars]}")
        
        # Calculate z_j
        z_j = sum(dual_vars[i] * constraint_coeffs[i] for i in range(self.num_constraints))
        
        if self.is_maximization:
            reduced_cost = obj_coeff - z_j
            print(f"\nReduced cost = c_j - z_j = {obj_coeff} - {z_j:.4f} = {reduced_cost:.4f}")
            
            if reduced_cost <= self.epsilon:
                print(f"\n✓ {new_var_name} should NOT be added (reduced cost ≤ 0)")
                print("Adding this variable would not improve the objective function.")
            else:
                print(f"\n✗ {new_var_name} should be added (reduced cost > 0)")
                print(f"Adding this variable can improve the objective by {reduced_cost:.4f} per unit.")
        else:
            reduced_cost = obj_coeff - z_j
            print(f"\nReduced cost = c_j - z_j = {obj_coeff} - {z_j:.4f} = {reduced_cost:.4f}")
            
            if reduced_cost >= -self.epsilon:
                print(f"\n✓ {new_var_name} should NOT be added (reduced cost ≥ 0)")
                print("Adding this variable would not improve the objective function.")
            else:
                print(f"\n✗ {new_var_name} should be added (reduced cost < 0)")
                print(f"Adding this variable can improve the objective.")


class SimplexTableauAnalyzer:
    """Analyze an existing simplex tableau"""
    
    def __init__(self):
        self.tableau = None
        self.var_names = []
        self.basic_vars = []
        self.is_maximization = True
        
    def input_existing_tableau(self):
        """Input an existing tableau for analysis"""
        print("\n" + "="*80)
        print("TABLEAU ANALYSIS - INPUT EXISTING TABLEAU")
        print("="*80)
        
        problem_type = input("\nIs this a (1) Maximization or (2) Minimization problem? [1/2]: ").strip()
        self.is_maximization = (problem_type == '1')
        
        num_vars = int(input("Enter total number of variables (including slack/artificial): "))
        num_constraints = int(input("Enter number of constraints (rows excluding Z row): "))
        
        print(f"\nEnter variable names (space-separated):")
        print("Example: x1 x2 x3 s1 s2")
        self.var_names = input().split()
        
        if len(self.var_names) != num_vars:
            print(f"Warning: Expected {num_vars} variables, got {len(self.var_names)}")
        
        print(f"\nEnter basic variables for each constraint (space-separated):")
        print("Example: s1 s2")
        self.basic_vars = input().split()
        
        if len(self.basic_vars) != num_constraints:
            print(f"Warning: Expected {num_constraints} basic variables, got {len(self.basic_vars)}")
        
        # Initialize tableau
        self.tableau = [[0.0 for _ in range(num_vars + 1)] for _ in range(num_constraints + 1)]
        
        print("\nEnter tableau values:")
        print("(For each row, enter all values including RHS, space-separated)")
        
        print(f"\nZ row ({num_vars + 1} values):")
        z_row = list(map(float, input().split()))
        self.tableau[0] = z_row
        
        for i in range(num_constraints):
            print(f"\nRow {i+1} for {self.basic_vars[i]} ({num_vars + 1} values):")
            row = list(map(float, input().split()))
            self.tableau[i+1] = row
        
        self.display_tableau()
        
    def display_tableau(self):
        """Display the current tableau"""
        print("\n" + "="*80)
        print("CURRENT TABLEAU")
        print("="*80)
        
        headers = self.var_names + ['RHS']
        row_labels = ['Z'] + self.basic_vars
        
        print_matrix(self.tableau, headers, row_labels)
        
    def analyze_tableau(self):
        """Perform comprehensive analysis of the tableau"""
        print("\n" + "="*80)
        print("TABLEAU ANALYSIS")
        print("="*80)
        
        z_row = self.tableau[0][:-1]
        
        # 1. Optimality Check
        print("\n1. OPTIMALITY CHECK:")
        print("-" * 60)
        
        has_negative = any(coeff < -1e-10 for coeff in z_row)
        has_positive = any(coeff > 1e-10 for coeff in z_row)
        
        if self.is_maximization:
            if not has_negative:
                print("✓ All Z row coefficients ≥ 0")
                print("✓ Solution is OPTIMAL for maximization")
                is_optimal = True
            else:
                print("✗ Some Z row coefficients < 0")
                print("✗ Solution is NOT optimal for maximization")
                is_optimal = False
        else:
            if not has_positive:
                print("✓ All Z row coefficients ≤ 0")
                print("✓ Solution is OPTIMAL for minimization")
                is_optimal = True
            else:
                print("✗ Some Z row coefficients > 0")
                print("✗ Solution is NOT optimal for minimization")
                is_optimal = False
        
        # 2. Basic and Non-Basic Variables
        print("\n2. VARIABLE CLASSIFICATION:")
        print("-" * 60)
        print(f"Basic Variables: {', '.join(self.basic_vars)}")
        non_basic = [v for v in self.var_names if v not in self.basic_vars]
        print(f"Non-Basic Variables: {', '.join(non_basic)}")
        
        # 3. Current Solution
        print("\n3. CURRENT SOLUTION:")
        print("-" * 60)
        for i, bv in enumerate(self.basic_vars):
            print(f"  {bv} = {self.tableau[i+1][-1]:.4f}")
        for v in non_basic:
            print(f"  {v} = 0")
        
        obj_type = "Maximum" if self.is_maximization else "Minimum"
        print(f"  {obj_type} Z = {self.tableau[0][-1]:.4f}")
        
        # 4. Next Iteration (if not optimal)
        if not is_optimal:
            print("\n4. NEXT ITERATION:")
            print("-" * 60)
            
            if self.is_maximization:
                # Find most negative coefficient
                min_coeff = min(z_row)
                pivot_col = z_row.index(min_coeff)
                print(f"Entering Variable: {self.var_names[pivot_col]} (most negative: {min_coeff:.4f})")
            else:
                # Find most positive coefficient
                max_coeff = max(z_row)
                pivot_col = z_row.index(max_coeff)
                print(f"Entering Variable: {self.var_names[pivot_col]} (most positive: {max_coeff:.4f})")
            
            # Minimum Ratio Test
            print("\nMinimum Ratio Test:")
            ratios = []
            for i in range(1, len(self.tableau)):
                if self.tableau[i][pivot_col] > 1e-10:
                    ratio = self.tableau[i][-1] / self.tableau[i][pivot_col]
                    ratios.append((ratio, i-1, self.basic_vars[i-1]))
                    print(f"  {self.basic_vars[i-1]}: {self.tableau[i][-1]:.4f} / {self.tableau[i][pivot_col]:.4f} = {ratio:.4f}")
                else:
                    print(f"  {self.basic_vars[i-1]}: Not eligible (coefficient ≤ 0)")
            
            if ratios:
                min_ratio = min(ratios, key=lambda x: x[0])
                print(f"\nLeaving Variable: {min_ratio[2]} (minimum ratio: {min_ratio[0]:.4f})")
                print(f"Pivot Element: {self.tableau[min_ratio[1]+1][pivot_col]:.4f}")
            else:
                print("\n⚠ No valid ratios found - Solution may be UNBOUNDED")
        
        # 5. Feasibility Check
        print("\n5. FEASIBILITY CHECK:")
        print("-" * 60)
        all_feasible = all(self.tableau[i][-1] >= -1e-10 for i in range(1, len(self.tableau)))
        if all_feasible:
            print("✓ All RHS values ≥ 0: Solution is FEASIBLE")
        else:
            print("✗ Some RHS values < 0: Solution is INFEASIBLE")
            print("  Dual Simplex method may be needed")
        
        return self.tableau


def main():
    """Main function to run the simplex solver"""
    print("="*80)
    print("COMPLETE SIMPLEX METHOD SOLVER")
    print("="*80)
    
    print("\nSelect mode:")
    print("1. Solve new LP problem (complete solution)")
    print("2. Solve new LP problem (step-by-step for n iterations)")
    print("3. Analyze existing tableau")
    print("4. Sensitivity analysis on optimal solution")
    
    mode = input("\nYour choice [1-4]: ").strip()
    
    if mode == '1' or mode == '2':
        solver = SimplexSolver()
        
        print("\nInput method:")
        print("1. Enter problem manually")
        print("2. Use sample problem")
        
        input_choice = input("\nYour choice [1/2]: ").strip()
        
        if input_choice == '2':
            # Sample problem: Maximize Z = 3x1 + 5x2
            # Subject to: x1 <= 4, 2x2 <= 12, 3x1 + 2x2 <= 18, x1, x2 >= 0
            print("\nUsing sample problem:")
            print("Maximize Z = 3x1 + 2x2 + 5x3")
            print("Subject to:")
            print("  x1 + 2x2 + 1x3 <= 430")
            print(" 3x1 + 0x2 + 2x3 <= 460")
            print("  1x1 + 4x2 + 0x3 <= 420")
            
            
            obj_coeffs = [30, 60, 40]
            constraints = [[1, 4, 1], [2, 3, 1], [1, 2, 2] ]
            constraint_types = ['<=', '<=', '<=']
            rhs_values = [300, 500, 450]
            
            solver.num_decision_vars = 3
            solver.num_constraints = 3
            solver.is_maximization = True
        else:
            obj_coeffs, constraints, constraint_types, rhs_values = solver.get_problem_input()
        
        # Setup tableau
        solver.setup_initial_tableau(obj_coeffs, constraints, constraint_types, rhs_values)
        
        # Solve
        if mode == '1':
            result = solver.solve()
        else:
            n = int(input("\nHow many iterations to perform? "))
            result = solver.solve_n_iterations(n)
        
        if result:
            # Offer sensitivity analysis
            perform_sa = input("\nPerform sensitivity analysis? [y/n]: ").strip().lower()
            if perform_sa == 'y':
                solver.sensitivity_analysis()
    
    elif mode == '3':
        analyzer = SimplexTableauAnalyzer()
        analyzer.input_existing_tableau()
        analyzer.analyze_tableau()
        
        cont = input("\nPerform another analysis? [y/n]: ").strip().lower()
        if cont == 'y':
            analyzer.analyze_tableau()
    
    elif mode == '4':
        print("\nFor sensitivity analysis, first solve an LP problem to optimality.")
        solver = SimplexSolver()
        obj_coeffs, constraints, constraint_types, rhs_values = solver.get_problem_input()
        solver.setup_initial_tableau(obj_coeffs, constraints, constraint_types, rhs_values)
        result = solver.solve()
        
        if result:
            solver.sensitivity_analysis()
    
    else:
        print("Invalid choice!")
    
    print("\n" + "="*80)
    print("PROGRAM COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()