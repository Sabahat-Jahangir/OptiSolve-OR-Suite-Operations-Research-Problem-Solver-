from typing import List, Tuple, Optional, Dict, Any
from copy import deepcopy
from itertools import permutations
import math
import sys

def print_matrix(matrix, columns=None, index=None):
    if columns:
        print(" ".join(f"{c:>10}" for c in columns))
    for i, row in enumerate(matrix):
        label = index[i] if index else f"Row {i}"
        print(f"{label:>5} " + " ".join(f"{x:>10}" for x in row))

def matrix_multiply(A, B):
    if not A or not B:
        return []
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    if cols_A != rows_B:
        raise ValueError("Incompatible dimensions")
    return [[sum(A[i][k] * B[k][j] for k in range(cols_A)) for j in range(cols_B)] for i in range(rows_A)]

def matrix_vector_multiply(A, v):
    if not A or not v:
        return []
    rows_A, cols_A = len(A), len(A[0])
    if cols_A != len(v):
        raise ValueError("Incompatible dimensions")
    return [sum(A[i][j] * v[j] for j in range(cols_A)) for i in range(rows_A)]


def zeros_like(matrix, fill_value=0.0):
    return [[fill_value for _ in row] for row in matrix]


def deep_copy_matrix(matrix):
    return [row[:] for row in matrix]

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
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("SIMPLEX METHOD - PROBLEM INPUT")
        print("="*60)
        
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
        num_slack = sum(1 for ct in constraint_types if ct in ['<=', '>='])
        num_artificial = sum(1 for ct in constraint_types if ct in ['>=', '='])
        
        total_vars = self.num_decision_vars + num_slack + num_artificial
        
        self.var_names = [f'x{i+1}' for i in range(self.num_decision_vars)]
        
        slack_idx = 0
        artificial_idx = 0
        slack_names = []
        artificial_names = []
        
        for ct in constraint_types:
            if ct == '<=':
                slack_idx += 1
                slack_names.append(f's{slack_idx}')
            elif ct == '>=':
                slack_idx += 1
                slack_names.append(f's{slack_idx}')
                artificial_idx += 1
                artificial_names.append(f'a{artificial_idx}')
            elif ct == '=':
                artificial_idx += 1
                artificial_names.append(f'a{artificial_idx}')
        
        self.var_names.extend(slack_names)
        self.var_names.extend(artificial_names)
        
        num_rows = self.num_constraints + 1
        num_cols = total_vars + 1
        
        self.tableau = [[0.0 for _ in range(num_cols)] for _ in range(num_rows)]
        
        if self.is_maximization:
            self.tableau[0][:self.num_decision_vars] = [-c for c in obj_coeffs]
        else:
            self.tableau[0][:self.num_decision_vars] = obj_coeffs
        
        slack_col = self.num_decision_vars
        artificial_col = self.num_decision_vars + len(slack_names)
        
        self.basic_vars = []
        
        for i, (coeffs, ct, rhs) in enumerate(zip(constraints, constraint_types, rhs_values)):
            row_idx = i + 1
            
            if rhs < 0:
                coeffs = [-c for c in coeffs]
                rhs = -rhs
                if ct == '<=':
                    ct = '>='
                elif ct == '>=':
                    ct = '<='
            
            self.tableau[row_idx][:self.num_decision_vars] = coeffs
            self.tableau[row_idx][-1] = rhs
            
            if ct == '<=':
                self.tableau[row_idx][slack_col] = 1
                self.basic_vars.append(self.var_names[slack_col])
                slack_col += 1
            elif ct == '>=':
                self.tableau[row_idx][slack_col] = -1
                slack_col += 1
                self.tableau[row_idx][artificial_col] = 1
                self.tableau[0][artificial_col] = self.M
                self.basic_vars.append(self.var_names[artificial_col])
                artificial_col += 1
            elif ct == '=':
                self.tableau[row_idx][artificial_col] = 1
                self.tableau[0][artificial_col] = self.M
                self.basic_vars.append(self.var_names[artificial_col])
                artificial_col += 1
        
        for i, bv in enumerate(self.basic_vars):
            if bv.startswith('a'):
                col_idx = self.var_names.index(bv)
                if self.tableau[0][col_idx] != 0:
                    for j in range(len(self.tableau[0])):
                        self.tableau[0][j] -= self.tableau[0][col_idx] * self.tableau[i+1][j]
        
        self.non_basic_vars = [v for v in self.var_names if v not in self.basic_vars]
        
    def display_tableau(self, title="Current Tableau"):
        print(f"\n{title}")
        print("-" * 80)
        
        headers = self.var_names + ['Solution']
        row_labels = ['Z'] + self.basic_vars
        
        print_matrix(self.tableau, headers, row_labels)
        print("-" * 80)
        
    def find_pivot_column(self):
        z_row = self.tableau[0][:-1]
        if self.is_maximization:
            min_val = min(z_row)
            if min_val >= -1e-10:
                return -1
            return z_row.index(min_val)
        else:
            min_val = min(z_row)
            if min_val >= -1e-10:
                return -1
            return z_row.index(min_val)
    
    def find_pivot_row(self, pivot_col):
        ratios = []
        for i in range(1, len(self.tableau)):
            if self.tableau[i][pivot_col] > 1e-10:
                ratio = self.tableau[i][-1] / self.tableau[i][pivot_col]
                ratios.append((ratio, i))
            else:
                ratios.append((float('inf'), i))
        
        if not ratios or all(r[0] == float('inf') for r in ratios):
            return -1
        
        min_ratio = min(ratios, key=lambda x: x[0])
        if min_ratio[0] == float('inf'):
            return -1
        return min_ratio[1]
    
    def perform_pivot_operation(self, pivot_row, pivot_col):
        pivot_element = self.tableau[pivot_row][pivot_col]
        
        for j in range(len(self.tableau[pivot_row])):
            self.tableau[pivot_row][j] /= pivot_element
        
        for i in range(len(self.tableau)):
            if i != pivot_row:
                factor = self.tableau[i][pivot_col]
                for j in range(len(self.tableau[i])):
                    self.tableau[i][j] -= factor * self.tableau[pivot_row][j]
        
        leaving_var = self.basic_vars[pivot_row - 1]
        entering_var = self.var_names[pivot_col]
        self.basic_vars[pivot_row - 1] = entering_var
        self.non_basic_vars = [v for v in self.var_names if v not in self.basic_vars]
        
        return entering_var, leaving_var
    
    def solve(self):
        self.iteration = 0
        print("\n" + "="*60)
        print("SIMPLEX METHOD - SOLUTION PROCESS")
        print("="*60)
        
        self.display_tableau(f"Initial Tableau (Iteration {self.iteration})")
        self.history.append(self.tableau.copy())
        
        while True:
            pivot_col = self.find_pivot_column()
            
            if pivot_col == -1:
                print("\n*** OPTIMAL SOLUTION FOUND ***")
                break
            
            pivot_row = self.find_pivot_row(pivot_col)
            
            if pivot_row == -1:
                print("\n*** UNBOUNDED SOLUTION ***")
                return None
            
            self.iteration += 1
            
            print(f"\nIteration {self.iteration}:")
            print(f"  Pivot Column: {self.var_names[pivot_col]} (column {pivot_col})")
            print(f"  Pivot Row: {self.basic_vars[pivot_row-1]} (row {pivot_row})")
            print(f"  Pivot Element: {self.tableau[pivot_row][pivot_col]:.4f}")
            
            entering, leaving = self.perform_pivot_operation(pivot_row, pivot_col)
            print(f"  Entering Variable: {entering}")
            print(f"  Leaving Variable: {leaving}")
            
            self.display_tableau(f"Tableau after Iteration {self.iteration}")
            self.history.append([row[:] for row in self.tableau])
        
        return self.get_solution()
    
    def solve_n_iterations(self, n_iterations):
        self.iteration = 0
        print("\n" + "="*60)
        print(f"SIMPLEX METHOD - SOLVING {n_iterations} ITERATION(S)")
        print("="*60)
        
        print("\n*** SOLUTION AT ZERO ITERATION (Initial BFS) ***")
        self.display_tableau(f"Iteration {self.iteration}")
        
        print("\nZero Iteration Solution:")
        for i, bv in enumerate(self.basic_vars):
            print(f"  {bv} = {self.tableau[i+1][-1]:.4f}")
        for v in self.non_basic_vars:
            print(f"  {v} = 0")
        print(f"  Z = {self.tableau[0][-1]:.4f}")
        
        self.history.append([row[:] for row in self.tableau])
        
        for iter_count in range(n_iterations):
            pivot_col = self.find_pivot_column()
            
            if pivot_col == -1:
                print(f"\n*** OPTIMAL SOLUTION FOUND at iteration {self.iteration} ***")
                break
            
            pivot_row = self.find_pivot_row(pivot_col)
            
            if pivot_row == -1:
                print("\n*** UNBOUNDED SOLUTION ***")
                return None
            
            self.iteration += 1
            
            print(f"\n" + "="*60)
            print(f"ITERATION {self.iteration}")
            print("="*60)
            
            print(f"\nStep 1: Identify Entering Variable")
            print(f"  Most negative in Z row: {self.var_names[pivot_col]} with value {self.tableau[0][pivot_col]:.4f}")
            
            print(f"\nStep 2: Ratio Test for Leaving Variable")
            for i in range(1, len(self.tableau)):
                if self.tableau[i][pivot_col] > 1e-10:
                    ratio = self.tableau[i][-1] / self.tableau[i][pivot_col]
                    print(f"  {self.basic_vars[i-1]}: {self.tableau[i][-1]:.4f} / {self.tableau[i][pivot_col]:.4f} = {ratio:.4f}")
                else:
                    print(f"  {self.basic_vars[i-1]}: Not eligible (coefficient <= 0)")
            
            print(f"\nStep 3: Pivot Operation")
            print(f"  Pivot Element: {self.tableau[pivot_row][pivot_col]:.4f} at row {pivot_row}, col {pivot_col}")
            
            entering, leaving = self.perform_pivot_operation(pivot_row, pivot_col)
            print(f"  Entering Variable: {entering}")
            print(f"  Leaving Variable: {leaving}")
            
            print(f"\n*** SOLUTION AFTER ITERATION {self.iteration} ***")
            self.display_tableau(f"Tableau after Iteration {self.iteration}")
            
            print(f"\nIteration {self.iteration} Solution:")
            for i, bv in enumerate(self.basic_vars):
                print(f"  {bv} = {self.tableau[i+1][-1]:.4f}")
            for v in self.non_basic_vars:
                print(f"  {v} = 0")
            print(f"  Z = {self.tableau[0][-1]:.4f}")
            
            self.history.append([row[:] for row in self.tableau])
        
        return self.get_solution()
    
    def get_solution(self):
        solution = {}
        for i, var in enumerate(self.var_names):
            if var in self.basic_vars:
                row_idx = self.basic_vars.index(var) + 1
                solution[var] = self.tableau[row_idx][-1]
            else:
                solution[var] = 0
        
        z_value = self.tableau[0][-1]
        if not self.is_maximization:
            z_value = -z_value if self.tableau[0][-1] < 0 else z_value
        
        print("\n" + "="*60)
        print("OPTIMAL SOLUTION")
        print("="*60)
        
        print("\nDecision Variables:")
        for i in range(self.num_decision_vars):
            var = f'x{i+1}'
            print(f"  {var} = {solution.get(var, 0):.4f}")
        
        print(f"\nOptimal Z value: {z_value:.4f}")
        
        print("\nBasic Variables:", self.basic_vars)
        print("Non-Basic Variables:", self.non_basic_vars)
        
        return solution, z_value
    
    def sensitivity_analysis(self):
        print("\n" + "="*60)
        print("SENSITIVITY ANALYSIS")
        print("="*60)
        
        while True:
            print("\nSensitivity Analysis Options:")
            print("1. Change in RHS (Resource Availability)")
            print("2. Change in Objective Coefficient")
            print("3. Add New Constraint")
            print("4. Add New Variable")
            print("5. Multiple Parameter Changes")
            print("6. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.rhs_sensitivity()
            elif choice == '2':
                self.objective_coefficient_sensitivity()
            elif choice == '3':
                self.add_new_constraint()
            elif choice == '4':
                self.add_new_variable()
            elif choice == '5':
                self.multiple_parameter_changes()
            elif choice == '6':
                break
    
    def rhs_sensitivity(self):
        print("\n--- RHS Sensitivity Analysis ---")
        print("(Rate of change and feasibility range computation)")
        
        constraint_num = int(input("Enter constraint number to analyze (e.g., 1 for R1): ")) - 1
        
        b_inv = self.get_b_inverse()
        
        if b_inv is None:
            print("Cannot compute B inverse from current tableau")
            return
        
        print(f"\nB inverse matrix:")
        print_matrix(b_inv)
        
        current_rhs = [row[-1] for row in self.tableau[1:]]
        
        slack_col = self.num_decision_vars + constraint_num
        shadow_price = self.tableau[0][slack_col]
        
        print(f"\nCurrent solution values (b_bar): {current_rhs}")
        print(f"\nShadow price (y{constraint_num + 1}) for constraint {constraint_num + 1}: {shadow_price:.4f}")
        
        print(f"\n--- Rate of Change Analysis ---")
        print(f"For unit increase in b{constraint_num + 1} (RHS of constraint {constraint_num + 1}):")
        print(f"  Change in Z = Shadow price = {shadow_price:.4f}")
        
        if self.is_maximization:
            print(f"  If b{constraint_num + 1} increases by 1, Z increases by {shadow_price:.4f}")
            print(f"  If b{constraint_num + 1} decreases by 1, Z decreases by {shadow_price:.4f}")
        else:
            print(f"  If b{constraint_num + 1} increases by 1, Z changes by {-shadow_price:.4f}")
        
        print(f"\n--- Feasibility Range Computation ---")
        
        b_inv_col = [row[constraint_num] for row in b_inv]
        
        lower_bound = -float('inf')
        upper_bound = float('inf')
        
        for i in range(len(current_rhs)):
            if b_inv_col[i] > 1e-10:
                upper_limit = current_rhs[i] / b_inv_col[i]
                upper_bound = min(upper_bound, upper_limit)
            elif b_inv_col[i] < -1e-10:
                lower_limit = current_rhs[i] / b_inv_col[i]
                lower_bound = max(lower_bound, lower_limit)
        
        current_b = float(input(f"Enter current value of b{constraint_num + 1}: "))
        
        feasible_min = current_b - upper_bound if upper_bound != float('inf') else -float('inf')
        feasible_max = current_b - lower_bound if lower_bound != -float('inf') else float('inf')
        
        print(f"\nFeasibility range for b{constraint_num + 1}:")
        print(f"  Allowable decrease: {upper_bound:.4f}" if upper_bound != float('inf') else "  Allowable decrease: Unlimited")
        print(f"  Allowable increase: {-lower_bound:.4f}" if lower_bound != -float('inf') else "  Allowable increase: Unlimited")
        print(f"  Range: [{current_b - upper_bound:.4f}, {current_b - lower_bound:.4f}]" if upper_bound != float('inf') and lower_bound != -float('inf') else f"  Range: Partially unbounded")
        
        do_change = input("\nCompute solution for specific RHS change? [y/n]: ").strip().lower()
        if do_change == 'y':
            delta = float(input("Enter change in RHS (delta): "))
            
            new_rhs = [x + delta * y for x, y in zip(current_rhs, b_inv_col)]
            
            print(f"\nNew solution values: {new_rhs}")
            
            if all(x >= -1e-10 for x in new_rhs):
                print("Solution remains FEASIBLE")
                new_z = self.tableau[0][-1] + delta * shadow_price
                print(f"New Z value: {new_z:.4f}")
            else:
                print("Solution becomes INFEASIBLE - Dual Simplex needed")
    
    def get_b_inverse(self):
        num_basic = len(self.basic_vars)
        b_inv = [[0.0 for _ in range(num_basic)] for _ in range(num_basic)]
        
        for i, bv in enumerate(self.basic_vars):
            col_idx = self.var_names.index(bv)
            if bv.startswith('s') or bv.startswith('a'):
                original_col = int(bv[1:]) - 1
                if original_col < num_basic:
                    b_inv[i] = self.tableau[i + 1][self.num_decision_vars:self.num_decision_vars + num_basic][:]
        
        if all(all(abs(x) < 1e-10 for x in row) for row in b_inv):
            b_inv = [row[self.num_decision_vars:self.num_decision_vars + num_basic] for row in self.tableau[1:]]
        
        return b_inv
    
    def objective_coefficient_sensitivity(self):
        print("\n--- Objective Coefficient Sensitivity Analysis ---")
        
        var_num = int(input("Enter variable number to analyze (e.g., 1 for x1): ")) - 1
        var_name = f'x{var_num + 1}'
        
        reduced_cost = self.tableau[0][var_num]
        
        if var_name in self.basic_vars:
            print(f"\n{var_name} is a BASIC variable (currently in solution)")
            row_idx = self.basic_vars.index(var_name) + 1
            current_value = self.tableau[row_idx][-1]
            print(f"Current value: {var_name} = {current_value:.4f}")
            print(f"Reduced cost: 0 (basic variable)")
            
            print("\nCalculating allowable range for objective coefficient...")
            
            cb = []
            for bv in self.basic_vars:
                if bv.startswith('x'):
                    idx = int(bv[1:]) - 1
                    cb.append(-self.tableau[0][idx] if self.is_maximization else self.tableau[0][idx])
                else:
                    cb.append(0)
            
            print(f"Current c_B vector: {cb}")
            
        else:
            print(f"\n{var_name} is a NON-BASIC variable (not in current solution)")
            print(f"Current value: {var_name} = 0")
            print(f"Reduced cost (c_j - z_j): {reduced_cost:.4f}")
            
            col = [row[var_num] for row in self.tableau[1:]]
            print(f"\nColumn for {var_name} in optimal tableau: {col}")
            
            if self.is_maximization:
                print(f"\n--- Why {var_name} is not in optimal solution? ---")
                if reduced_cost >= 0:
                    print(f"Reduced cost ({reduced_cost:.4f}) >= 0")
                    print(f"Increasing {var_name} would DECREASE Z (for maximization)")
                    print(f"Therefore, {var_name} stays at 0")
                    
                    print(f"\n--- Minimum coefficient for {var_name} to enter basis ---")
                    z_j = -reduced_cost if self.is_maximization else reduced_cost
                    
                    current_obj_coeff = float(input(f"Enter current objective coefficient c{var_num + 1}: "))
                    
                    min_required = current_obj_coeff + abs(reduced_cost)
                    print(f"\nFor {var_name} to enter the basis:")
                    print(f"  Current coefficient: {current_obj_coeff}")
                    print(f"  Reduced cost: {reduced_cost:.4f}")
                    print(f"  Minimum coefficient required: {min_required:.4f}")
                    print(f"  Coefficient must increase by at least: {abs(reduced_cost):.4f}")
            else:
                print(f"\n--- Why {var_name} is not in optimal solution? ---")
                if reduced_cost <= 0:
                    print(f"Reduced cost ({reduced_cost:.4f}) <= 0")
                    print(f"Increasing {var_name} would INCREASE Z (for minimization)")
                    print(f"Therefore, {var_name} stays at 0")
    
    def add_new_constraint(self):
        print("\n--- Adding New Constraint ---")
        print("(e.g., adding a new resource or capacity constraint)")
        
        print(f"\nEnter coefficients for x1 to x{self.num_decision_vars}:")
        coeffs = list(map(float, input("Coefficients (space-separated): ").split()))
        
        ctype = input("Constraint type (<=, >=, =): ").strip()
        rhs = float(input("RHS value (available capacity): "))
        
        current_solution = {}
        for i, var in enumerate(self.var_names[:self.num_decision_vars]):
            if var in self.basic_vars:
                row_idx = self.basic_vars.index(var) + 1
                current_solution[var] = self.tableau[row_idx][-1]
            else:
                current_solution[var] = 0
        
        print(f"\n--- Current Optimal Solution ---")
        for var, val in current_solution.items():
            print(f"  {var} = {val:.4f}")
        
        lhs_value = sum(coeffs[i] * current_solution[f'x{i+1}'] for i in range(self.num_decision_vars))
        
        print(f"\n--- Constraint Evaluation ---")
        print(f"LHS = ", end="")
        terms = [f"{coeffs[i]}*{current_solution[f'x{i+1}']:.4f}" for i in range(self.num_decision_vars) if current_solution[f'x{i+1}'] > 0]
        print(" + ".join(terms) + f" = {lhs_value:.4f}")
        print(f"RHS = {rhs}")
        
        if ctype == '<=':
            slack = rhs - lhs_value
            print(f"Slack = {rhs} - {lhs_value:.4f} = {slack:.4f}")
            
            if lhs_value <= rhs + 1e-10:
                print(f"\n*** Constraint is SATISFIED ***")
                print(f"New constraint does not affect the current optimal solution")
                print(f"Slack variable for new constraint = {slack:.4f}")
            else:
                print(f"\n*** Constraint is VIOLATED ***")
                print(f"Current solution uses {lhs_value:.4f} but only {rhs} is available")
                print(f"Need Dual Simplex to find new optimal solution")
                self.apply_dual_simplex_for_new_constraint(coeffs, ctype, rhs, lhs_value)
                
        elif ctype == '>=':
            surplus = lhs_value - rhs
            print(f"Surplus = {lhs_value:.4f} - {rhs} = {surplus:.4f}")
            
            if lhs_value >= rhs - 1e-10:
                print(f"\n*** Constraint is SATISFIED ***")
                print(f"New constraint does not affect the current optimal solution")
            else:
                print(f"\n*** Constraint is VIOLATED ***")
                print(f"Need Dual Simplex to find new optimal solution")
                self.apply_dual_simplex_for_new_constraint(coeffs, ctype, rhs, lhs_value)
                
        elif ctype == '=':
            diff = abs(lhs_value - rhs)
            print(f"Difference = |{lhs_value:.4f} - {rhs}| = {diff:.4f}")
            
            if diff < 1e-10:
                print(f"\n*** Constraint is SATISFIED ***")
            else:
                print(f"\n*** Constraint is VIOLATED ***")
                self.apply_dual_simplex_for_new_constraint(coeffs, ctype, rhs, lhs_value)
    
    def apply_dual_simplex_for_new_constraint(self, coeffs, ctype, rhs, lhs_value):
        print("\n--- Applying Dual Simplex for New Constraint ---")
        
        b_inv = self.get_b_inverse()
        
        print(f"\nStep 1: Transform new constraint using B^-1")
        
        a_new = coeffs[:self.num_decision_vars]
        
        transformed_row = [0.0] * (len(self.var_names) + 1)
        
        for j in range(self.num_decision_vars):
            var_name = f'x{j+1}'
            if var_name in self.basic_vars:
                transformed_row[j] = 0
            else:
                col_in_optimal = [row[j] for row in self.tableau[1:]]
                transformed_row[j] = a_new[j]
                for i, bv in enumerate(self.basic_vars):
                    if bv.startswith('x'):
                        bv_idx = int(bv[1:]) - 1
                        transformed_row[j] -= a_new[bv_idx] * col_in_optimal[i]
        
        for j in range(self.num_decision_vars, len(self.var_names)):
            col_in_optimal = [row[j] for row in self.tableau[1:]]
            for i, bv in enumerate(self.basic_vars):
                if bv.startswith('x'):
                    bv_idx = int(bv[1:]) - 1
                    transformed_row[j] -= a_new[bv_idx] * col_in_optimal[i]
        
        if ctype == '<=':
            transformed_row[-1] = rhs - lhs_value
        else:
            transformed_row[-1] = lhs_value - rhs
        
        print(f"\nTransformed constraint row: {transformed_row}")
        
        print(f"\nNew tableau with added constraint:")
        
        new_tableau = self.tableau + [[0.0] * len(self.tableau[0])]
        
        headers = self.var_names + ['s_new', 'Solution']
        print(f"  Variables: {headers}")
        
        if transformed_row[-1] < 0:
            print(f"\nRHS is negative ({transformed_row[-1]:.4f})")
            print("Dual Simplex iterations needed:")
            print("1. Select leaving variable: Row with most negative RHS")
            print("2. Select entering variable: Min ratio of Z-row / constraint row for negative entries")
            print("3. Perform pivot operation")
            print("4. Repeat until all RHS >= 0")
    
    def add_new_variable(self):
        print("\n--- Adding New Variable ---")
        print("(e.g., adding a new product to production mix)")
        
        new_var_name = input("Enter name for new variable (e.g., x_new or xs): ").strip()
        obj_coeff = float(input(f"Enter objective coefficient (profit/cost) for {new_var_name}: "))
        
        print(f"\nEnter resource consumption for {new_var_name}:")
        print(f"(Coefficients for {self.num_constraints} constraints)")
        constraint_coeffs = list(map(float, input("Coefficients (space-separated): ").split()))
        
        b_inv = self.get_b_inverse()
        
        y = constraint_coeffs
        y_bar = [sum(b_inv[i][j] * y[j] for j in range(len(y))) for i in range(len(b_inv))]
        
        print(f"\n--- Computing new variable column in optimal tableau ---")
        print(f"Original column (a): {y}")
        print(f"B inverse:")
        print_matrix(b_inv)
        print(f"\nTransformed column (y_bar = B^-1 * a): {y_bar}")
        
        cb = []
        for bv in self.basic_vars:
            col_idx = self.var_names.index(bv)
            if bv.startswith('x'):
                var_idx = int(bv[1:]) - 1
                if self.is_maximization:
                    cb.append(obj_coeff if var_idx == -1 else self.get_original_obj_coeff(var_idx))
                else:
                    cb.append(self.get_original_obj_coeff(var_idx))
            else:
                cb.append(0)
        
        print(f"\nc_B (basic variable coefficients): {cb}")
        
        z_j = sum(c * y for c, y in zip(cb, y_bar))
        
        if self.is_maximization:
            reduced_cost = obj_coeff - z_j
            print(f"\nz_j = c_B * y_bar = {z_j:.4f}")
            print(f"c_j - z_j = {obj_coeff} - {z_j:.4f} = {reduced_cost:.4f}")
        else:
            reduced_cost = obj_coeff - z_j
            print(f"\nz_j = c_B * y_bar = {z_j:.4f}")
            print(f"c_j - z_j = {obj_coeff} - {z_j:.4f} = {reduced_cost:.4f}")
        
        print(f"\n--- Decision ---")
        if self.is_maximization:
            if reduced_cost <= 1e-10:
                print(f"Reduced cost ({reduced_cost:.4f}) <= 0")
                print(f"Adding {new_var_name} will NOT improve the solution")
                print(f"Current optimal solution remains optimal")
            else:
                print(f"Reduced cost ({reduced_cost:.4f}) > 0")
                print(f"Adding {new_var_name} CAN improve the solution!")
                print(f"Each unit of {new_var_name} improves Z by {reduced_cost:.4f}")
                
                self.compute_new_solution_with_variable(new_var_name, y_bar, reduced_cost, obj_coeff)
        else:
            if reduced_cost >= -1e-10:
                print(f"Reduced cost ({reduced_cost:.4f}) >= 0")
                print(f"Adding {new_var_name} will NOT improve the solution")
            else:
                print(f"Reduced cost ({reduced_cost:.4f}) < 0")
                print(f"Adding {new_var_name} CAN improve the solution!")
                
                self.compute_new_solution_with_variable(new_var_name, y_bar, reduced_cost, obj_coeff)
    
    def get_original_obj_coeff(self, var_idx):
        return 0
    
    def compute_new_solution_with_variable(self, new_var_name, y_bar, reduced_cost, obj_coeff):
        print(f"\n--- Computing optimal solution with {new_var_name} ---")
        
        current_rhs = [row[-1] for row in self.tableau[1:]]
        
        ratios = []
        for i in range(len(current_rhs)):
            if y_bar[i] > 1e-10:
                ratio = current_rhs[i] / y_bar[i]
                ratios.append((ratio, i, self.basic_vars[i]))
                print(f"Ratio for {self.basic_vars[i]}: {current_rhs[i]:.4f} / {y_bar[i]:.4f} = {ratio:.4f}")
        
        if ratios:
            min_ratio = min(ratios, key=lambda x: x[0])
            theta = min_ratio[0]
            leaving_var = min_ratio[2]
            leaving_row = min_ratio[1]
            
            print(f"\nMinimum ratio: {theta:.4f} at {leaving_var}")
            print(f"Entering variable: {new_var_name}")
            print(f"Leaving variable: {leaving_var}")
            
            new_solution = current_rhs - theta * y_bar
            new_solution[leaving_row] = theta
            
            print(f"\nNew solution:")
            for i, bv in enumerate(self.basic_vars):
                if i == leaving_row:
                    print(f"  {new_var_name} = {theta:.4f}")
                else:
                    print(f"  {bv} = {new_solution[i]:.4f}")
            
            new_z = self.tableau[0][-1] + theta * reduced_cost
            print(f"\nNew Z value: {new_z:.4f}")
        else:
            print("No valid ratios - solution may be unbounded")
    
    def multiple_parameter_changes(self):
        print("\n--- Multiple Parameter Changes ---")
        print("(Recompute using c_B and B^-1 of current optimal solution)")
        
        b_inv = self.get_b_inverse()
        
        cb = []
        cb_names = []
        for bv in self.basic_vars:
            if bv.startswith('x'):
                var_idx = int(bv[1:]) - 1
                cb_names.append(bv)
                cb.append(0)
            else:
                cb_names.append(bv)
                cb.append(0)
        
        print(f"\nCurrent B^-1:")
        print_matrix(b_inv)
        
        print(f"\nEnter the original c_B values for basic variables {cb_names}:")
        cb = list(map(float, input("c_B values (space-separated): ").split()))
        
        print(f"\nEnter the original objective coefficients c (for x1 to x{self.num_decision_vars}):")
        c_original = list(map(float, input("c values (space-separated): ").split()))
        c_original = c_original
        
        print(f"\nEnter the original constraint matrix A ({self.num_constraints} rows x {self.num_decision_vars} cols):")
        A_original = []
        for i in range(self.num_constraints):
            row = list(map(float, input(f"Row {i+1}: ").split()))
            A_original.append(row)
        
        print(f"\nEnter the original RHS values b:")
        b_original = list(map(float, input("b values (space-separated): ").split()))
        
        print("\n" + "="*60)
        print("NOW ENTER THE CHANGES")
        print("="*60)
        
        num_changes = int(input("\nHow many parameters to change? "))
        
        c_new = c_original[:]
        A_new = [row[:] for row in A_original]
        b_new = b_original[:]
        cb_new = cb[:]
        
        for i in range(num_changes):
            print(f"\nChange {i+1}:")
            change_type = input("Type (1=obj_coeff c_j, 2=constraint_coeff a_ij, 3=rhs b_i): ").strip()
            
            if change_type == '1':
                var = int(input("Variable number j: ")) - 1
                new_val = float(input("New c_j value: "))
                c_new[var] = new_val
                
                var_name = f'x{var+1}'
                if var_name in self.basic_vars:
                    basic_idx = self.basic_vars.index(var_name)
                    cb_new[basic_idx] = new_val
                    
            elif change_type == '2':
                row = int(input("Constraint number i: ")) - 1
                col = int(input("Variable number j: ")) - 1
                new_val = float(input("New a_ij value: "))
                A_new[row][col] = new_val
                
            elif change_type == '3':
                row = int(input("Constraint number i: ")) - 1
                new_val = float(input("New b_i value: "))
                b_new[row] = new_val
        
        print("\n" + "="*60)
        print("RECOMPUTING OPTIMAL TABLE")
        print("="*60)
        
        print(f"\nNew c: {c_new}")
        print(f"New c_B: {cb_new}")
        print(f"New b: {b_new}")
        print(f"\nNew A matrix:")
        print_matrix(A_new)
        
        print(f"\n--- Step 1: Compute new RHS (b_bar = B^-1 * b_new) ---")
        b_bar_new = matrix_vector_multiply(b_inv, b_new)
        print(f"b_bar_new = {b_bar_new}")
        
        print(f"\n--- Step 2: Compute new constraint columns (A_bar = B^-1 * A_new) ---")
        A_bar_new = matrix_multiply(b_inv, A_new)
        print(f"A_bar_new:")
        print_matrix(A_bar_new, columns=[f'x{j+1}' for j in range(self.num_decision_vars)])
        
        print(f"\n--- Step 3: Compute new Z row ---")
        z_row_new = [0.0] * self.num_decision_vars
        for j in range(self.num_decision_vars):
            z_j = sum(cb_new[i] * A_bar_new[i][j] for i in range(len(cb_new)))
            z_row_new[j] = c_new[j] - z_j
            print(f"For x{j+1}: z_j = {z_j:.4f}, c_j - z_j = {c_new[j]} - {z_j:.4f} = {z_row_new[j]:.4f}")
        
        print(f"\n--- Step 4: Compute new Z value ---")
        z_value_new = sum(c * b for c, b in zip(cb_new, b_bar_new))
        print(f"Z = c_B * b_bar = {z_value_new:.4f}")
        
        print("\n" + "="*60)
        print("RECOMPUTED TABLE")
        print("="*60)
        
        print(f"\nZ row (reduced costs): {z_row_new}")
        print(f"Solution column: {b_bar_new}")
        print(f"Z value: {z_value_new:.4f}")
        
        print("\n--- Feasibility Check ---")
        if all(x >= -1e-10 for x in b_bar_new):
            print("All b_bar >= 0: Solution is FEASIBLE")
        else:
            print("Some b_bar < 0: Solution is INFEASIBLE")
            print("Dual Simplex required to restore feasibility")
        
        print("\n--- Optimality Check ---")
        if self.is_maximization:
            if all(x <= 1e-10 for x in z_row_new):
                print("All reduced costs <= 0: Solution is OPTIMAL for maximization")
            else:
                print("Some reduced costs > 0: Solution is NOT OPTIMAL")
                print("Continue with Simplex iterations")
        else:
            if all(x >= -1e-10 for x in z_row_new):
                print("All reduced costs >= 0: Solution is OPTIMAL for minimization")
            else:
                print("Some reduced costs < 0: Solution is NOT OPTIMAL")
                print("Continue with Simplex iterations")


class SimplexTableauAnalyzer:
    
    def __init__(self):
        self.tableau = None
        self.var_names = []
        self.basic_vars = []
        
    def input_existing_tableau(self):
        print("\n" + "="*60)
        print("TABLEAU ANALYSIS - INPUT EXISTING TABLEAU")
        print("="*60)
        
        num_vars = int(input("Enter total number of variables (including slack/artificial): "))
        num_constraints = int(input("Enter number of constraints (rows excluding Z row): "))
        
        print(f"\nEnter variable names (space-separated, e.g., x1 x2 x3 s1 s2 a1):")
        self.var_names = input().split()
        
        print(f"\nEnter basic variables for each constraint row (space-separated):")
        self.basic_vars = input().split()
        
        self.tableau = [[0.0 for _ in range(num_vars + 1)] for _ in range(num_constraints + 1)]
        
        print("\nEnter Z row (including solution value at end):")
        z_row = list(map(float, input().split()))
        self.tableau[0] = z_row
        
        for i in range(num_constraints):
            print(f"Enter row {i+1} (basic var: {self.basic_vars[i]}) including solution:")
            row = list(map(float, input().split()))
            self.tableau[i+1] = row
        
        self.display_tableau()
        
    def display_tableau(self):
        print("\n--- Current Tableau ---")
        headers = self.var_names + ['Solution']
        row_labels = ['Z'] + self.basic_vars
        print_matrix(self.tableau, headers, row_labels)
        
    def analyze_tableau(self):
        print("\n" + "="*60)
        print("TABLEAU ANALYSIS")
        print("="*60)
        
        print("\n1. Problem Type Analysis:")
        z_row = self.tableau[0][:-1]
        
        has_negative = any(z_row < -1e-10)
        has_positive = any(z_row > 1e-10)
        
        if not has_negative:
            print("   - All Z row coefficients >= 0")
            print("   - If this is MAXIMIZATION: Solution is OPTIMAL")
            print("   - If this is MINIMIZATION: May need to check for optimality")
        elif not has_positive:
            print("   - All Z row coefficients <= 0")
            print("   - If this is MINIMIZATION: Solution is OPTIMAL")
        else:
            print("   - Mixed signs in Z row - Not yet optimal")
        
        print("\n2. Basic and Non-Basic Variables:")
        print(f"   Basic Variables: {self.basic_vars}")
        non_basic = [v for v in self.var_names if v not in self.basic_vars]
        print(f"   Non-Basic Variables: {non_basic}")
        
        print("\n3. Current Solution:")
        for i, bv in enumerate(self.basic_vars):
            print(f"   {bv} = {self.tableau[i+1][-1]:.4f}")
        for v in non_basic:
            print(f"   {v} = 0")
        print(f"   Z = {self.tableau[0][-1]:.4f}")
        
        print("\n4. Entering Variable Analysis (for Maximization):")
        min_idx = z_row.index(min(z_row))
        if z_row[min_idx] < -1e-10:
            print(f"   Entering Variable: {self.var_names[min_idx]} (most negative: {z_row[min_idx]:.4f})")
            
            print("\n5. Leaving Variable Analysis (Ratio Test):")
            ratios = []
            for i in range(1, len(self.tableau)):
                if self.tableau[i][min_idx] > 1e-10:
                    ratio = self.tableau[i][-1] / self.tableau[i][min_idx]
                    ratios.append((self.basic_vars[i-1], ratio, i))
                    print(f"   {self.basic_vars[i-1]}: {self.tableau[i][-1]:.4f} / {self.tableau[i][min_idx]:.4f} = {ratio:.4f}")
                else:
                    print(f"   {self.basic_vars[i-1]}: Not eligible (coefficient <= 0)")
            
            if ratios:
                leaving = min(ratios, key=lambda x: x[1])
                print(f"\n   Leaving Variable: {leaving[0]} (minimum ratio: {leaving[1]:.4f})")
        else:
            print("   No entering variable - Solution is optimal for maximization")
        
        return self.tableau


class TransportationProblem:
    
    def __init__(self):
        self.cost_matrix = None
        self.supply = None
        self.demand = None
        self.allocation = None
        self.num_sources = 0
        self.num_destinations = 0
        self.is_maximization = False
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("TRANSPORTATION PROBLEM - INPUT")
        print("="*60)
        
        problem_type = input("\nIs this a (1) Minimization or (2) Maximization problem? [1/2]: ").strip()
        self.is_maximization = (problem_type == '2')
        
        self.num_sources = int(input("Enter number of sources (supply points): "))
        self.num_destinations = int(input("Enter number of destinations (demand points): "))
        
        print(f"\nEnter cost/profit matrix ({self.num_sources} x {self.num_destinations}):")
        self.cost_matrix = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
        
        for i in range(self.num_sources):
            row = list(map(float, input(f"Row {i+1} (space-separated): ").split()))
            self.cost_matrix[i] = row
        
        print("\nEnter supply values (space-separated):")
        self.supply = list(map(float, input().split()))
        
        print("Enter demand values (space-separated):")
        self.demand = list(map(float, input().split()))
        
        self.balance_problem()
        
    def balance_problem(self):
        total_supply = sum(self.supply)
        total_demand = sum(self.demand)
        
        print(f"\nTotal Supply: {total_supply}")
        print(f"Total Demand: {total_demand}")
        
        if abs(total_supply - total_demand) < 1e-10:
            print("Problem is BALANCED")
        elif total_supply > total_demand:
            print(f"Supply > Demand: Adding dummy destination with demand {total_supply - total_demand}")
            dummy_demand = total_supply - total_demand
            self.demand.append(dummy_demand)
            for i in range(len(self.cost_matrix)):
                self.cost_matrix[i].append(0.0)
            self.num_destinations += 1
        else:
            print(f"Demand > Supply: Adding dummy source with supply {total_demand - total_supply}")
            dummy_supply = total_demand - total_supply
            self.supply.append(dummy_supply)
            dummy_row = [0.0] * self.num_destinations
            self.cost_matrix.append(dummy_row)
            self.num_sources += 1
        
        self.allocation = [[0.0 for _ in row] for row in self.cost_matrix]
        
    def display_transportation_table(self, title="Transportation Table"):
        print(f"\n{title}")
        print("-" * 60)
        
        headers = [f'D{j+1}' for j in range(self.num_destinations)] + ['Supply']
        data = []
        
        for i in range(self.num_sources):
            row = []
            for j in range(self.num_destinations):
                allocation_value = self.allocation[i][j]
                cost_value = self.cost_matrix[i][j]
                if allocation_value > 0:
                    row.append(f"{cost_value:.0f}({allocation_value:.0f})")
                else:
                    row.append(f"{cost_value:.0f}")
            row.append(f"{self.supply[i]:.0f}")
            data.append(row)
        
        print_matrix(data, headers, [f'S{i+1}' for i in range(self.num_sources)])
        
        total_demand = sum(self.demand)
        demand_row = [f"{d:.0f}" for d in self.demand] + [f"{total_demand:.0f}"]
        print("Demand: " + "  ".join(demand_row))
        print("-" * 60)
        
    def northwest_corner_method(self):
        print("\n" + "="*60)
        print("NORTHWEST CORNER METHOD")
        print("="*60)
        
        self.allocation = zeros_like(self.cost_matrix)
        supply = self.supply.copy()
        demand = self.demand.copy()
        
        i, j = 0, 0
        step = 1
        
        while i < self.num_sources and j < self.num_destinations:
            allocation = min(supply[i], demand[j])
            self.allocation[i][j] = allocation
            
            print(f"\nStep {step}: Allocate {allocation:.0f} to cell ({i+1}, {j+1})")
            
            supply[i] -= allocation
            demand[j] -= allocation
            
            if abs(supply[i]) < 1e-10:
                i += 1
            if abs(demand[j]) < 1e-10:
                j += 1
            
            self.display_transportation_table(f"After Step {step}")
            step += 1
        
        return self.calculate_total_cost()
    
    def least_cost_method(self):
        print("\n" + "="*60)
        print("LEAST COST METHOD")
        print("="*60)
        
        self.allocation = zeros_like(self.cost_matrix)
        supply = self.supply.copy()
        demand = self.demand.copy()
        
        cost_copy = deep_copy_matrix(self.cost_matrix)
        if self.is_maximization:
            cost_copy = [[-val for val in row] for row in cost_copy]
        
        step = 1
        
        def remaining(value_list):
            return sum(value_list) > 1e-10
        
        while remaining(supply) and remaining(demand):
            min_cell = None
            min_cost = None
            for i in range(self.num_sources):
                if supply[i] <= 1e-10:
                    continue
                for j in range(self.num_destinations):
                    if demand[j] <= 1e-10:
                        continue
                    cost_value = cost_copy[i][j]
                    if min_cost is None or cost_value < min_cost:
                        min_cost = cost_value
                        min_cell = (i, j)
            
            if min_cell is None:
                break
            
            i, j = min_cell
            
            allocation = min(supply[i], demand[j])
            self.allocation[i][j] = allocation
            
            print(f"\nStep {step}: Minimum cost cell ({i+1}, {j+1}) with cost {self.cost_matrix[i][j]:.0f}")
            print(f"Allocate {allocation:.0f} units")
            
            supply[i] -= allocation
            demand[j] -= allocation
            
            self.display_transportation_table(f"After Step {step}")
            step += 1
        
        return self.calculate_total_cost()
    
    def vogels_approximation_method(self):
        print("\n" + "="*60)
        print("VOGEL'S APPROXIMATION METHOD (VAM)")
        print("="*60)
        
        self.allocation = zeros_like(self.cost_matrix)
        supply = self.supply.copy()
        demand = self.demand.copy()
        
        cost_copy = deep_copy_matrix(self.cost_matrix)
        if self.is_maximization:
            cost_copy = [[-val for val in row] for row in cost_copy]
        
        step = 1
        
        def has_remaining(values):
            return sum(values) > 1e-10
        
        while has_remaining(supply) and has_remaining(demand):
            row_penalties = []
            for i in range(self.num_sources):
                if supply[i] > 1e-10:
                    valid_costs = [cost_copy[i][j] for j in range(self.num_destinations) if demand[j] > 1e-10]
                    if len(valid_costs) >= 2:
                        sorted_costs = sorted(valid_costs)
                        row_penalties.append((sorted_costs[1] - sorted_costs[0], i, 'row'))
                    elif len(valid_costs) == 1:
                        row_penalties.append((valid_costs[0], i, 'row'))
            
            col_penalties = []
            for j in range(self.num_destinations):
                if demand[j] > 1e-10:
                    valid_costs = [cost_copy[i][j] for i in range(self.num_sources) if supply[i] > 1e-10]
                    if len(valid_costs) >= 2:
                        sorted_costs = sorted(valid_costs)
                        col_penalties.append((sorted_costs[1] - sorted_costs[0], j, 'col'))
                    elif len(valid_costs) == 1:
                        col_penalties.append((valid_costs[0], j, 'col'))
            
            all_penalties = row_penalties + col_penalties
            if not all_penalties:
                break
            
            max_penalty = max(all_penalties, key=lambda x: x[0])
            
            print(f"\nStep {step}:")
            print(f"Row penalties: {[(p[0], f'S{p[1]+1}') for p in row_penalties]}")
            print(f"Column penalties: {[(p[0], f'D{p[1]+1}') for p in col_penalties]}")
            print(f"Maximum penalty: {max_penalty[0]:.0f} in {max_penalty[2]} {max_penalty[1]+1}")
            
            if max_penalty[2] == 'row':
                i = max_penalty[1]
                valid_j = [(cost_copy[i][j], j) for j in range(self.num_destinations) if demand[j] > 1e-10]
                j = min(valid_j, key=lambda x: x[0])[1]
            else:
                j = max_penalty[1]
                valid_i = [(cost_copy[i][j], i) for i in range(self.num_sources) if supply[i] > 1e-10]
                i = min(valid_i, key=lambda x: x[0])[1]
            
            allocation = min(supply[i], demand[j])
            self.allocation[i][j] = allocation
            
            print(f"Allocate {allocation:.0f} to cell ({i+1}, {j+1})")
            
            supply[i] -= allocation
            demand[j] -= allocation
            
            self.display_transportation_table(f"After Step {step}")
            step += 1
        
        return self.calculate_total_cost()
    
    def calculate_total_cost(self):
        total = 0.0
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                total += self.allocation[i][j] * self.cost_matrix[i][j]
        if self.is_maximization:
            print(f"\nTotal Profit: {total:.2f}")
        else:
            print(f"\nTotal Cost: {total:.2f}")
        return total
    
    def modi_method(self):
        print("\n" + "="*60)
        print("MODI METHOD (UV METHOD) - OPTIMIZATION")
        print("="*60)
        
        iteration = 0
        
        while True:
            iteration += 1
            print(f"\n--- MODI Iteration {iteration} ---")
            
            self.display_transportation_table(f"Current Allocation")
            
            u, v = self.calculate_uv_values()
            
            if u is None:
                print("Cannot calculate u-v values. Check allocation.")
                break
            
            print(f"\nu values: {u}")
            print(f"v values: {v}")
            
            opportunity_costs = [[0.0 for _ in row] for row in self.cost_matrix]
            for i in range(self.num_sources):
                for j in range(self.num_destinations):
                    if self.allocation[i][j] == 0:
                        opportunity_costs[i][j] = self.cost_matrix[i][j] - u[i] - v[j]
            
            print("\nOpportunity Costs (for non-basic cells):")
            print_matrix(opportunity_costs, columns=[f'D{j+1}' for j in range(self.num_destinations)], index=[f'S{i+1}' for i in range(self.num_sources)])
            
            if self.is_maximization:
                max_opp = max(x for row in opportunity_costs for x in row)
                if max_opp <= 1e-10:
                    print("\n*** OPTIMAL SOLUTION REACHED ***")
                    break
                flat = [x for row in opportunity_costs for x in row]
                idx = flat.index(max_opp)
                entering_cell = (idx // self.num_destinations, idx % self.num_destinations)
            else:
                min_opp = min(x for row in opportunity_costs for x in row)
                if min_opp >= -1e-10:
                    print("\n*** OPTIMAL SOLUTION REACHED ***")
                    break
                flat = [x for row in opportunity_costs for x in row]
                idx = flat.index(min_opp)
                entering_cell = (idx // self.num_destinations, idx % self.num_destinations)
            
            print(f"\nEntering cell: ({entering_cell[0]+1}, {entering_cell[1]+1}) with opportunity cost {opportunity_costs[entering_cell[0]][entering_cell[1]]:.2f}")
            
            loop = self.find_loop(entering_cell)
            if loop is None:
                print("Could not find closed loop")
                break
            
            print(f"Closed loop: {[(c[0]+1, c[1]+1) for c in loop]}")
            
            theta_values = []
            for idx, cell in enumerate(loop):
                if idx % 2 == 1:
                    theta_values.append(self.allocation[cell[0]][cell[1]])
            
            theta = min(theta_values)
            print(f"Theta (minimum allocation in negative positions): {theta:.0f}")
            
            for idx, cell in enumerate(loop):
                if idx % 2 == 0:
                    self.allocation[cell[0]][cell[1]] += theta
                else:
                    self.allocation[cell[0]][cell[1]] -= theta
            
            for r in range(self.num_sources):
                for c in range(self.num_destinations):
                    if abs(self.allocation[r][c]) < 1e-10:
                        self.allocation[r][c] = 0.0
        
        return self.calculate_total_cost()
    
    def calculate_uv_values(self):
        basic_cells = []
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > 0:
                    basic_cells.append((i, j))
        
        u = [None] * self.num_sources
        v = [None] * self.num_destinations
        u[0] = 0.0
        
        max_iterations = self.num_sources + self.num_destinations
        for _ in range(max_iterations):
            updated = False
            for i, j in basic_cells:
                if u[i] is not None and v[j] is None:
                    v[j] = self.cost_matrix[i][j] - u[i]
                    updated = True
                elif u[i] is None and v[j] is not None:
                    u[i] = self.cost_matrix[i][j] - v[j]
                    updated = True
            if not updated:
                break
        
        if any(value is None for value in u) or any(value is None for value in v):
            return None, None
        
        return u, v
    
    def find_loop(self, start_cell):
        basic_cells = set()
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > 0:
                    basic_cells.add((i, j))
        
        def dfs(current, path, is_horizontal):
            if len(path) > 2 and current == start_cell:
                return path
            
            if current in path[1:]:
                return None
            
            i, j = current
            
            if is_horizontal:
                for new_j in range(self.num_destinations):
                    if new_j != j:
                        next_cell = (i, new_j)
                        if next_cell == start_cell and len(path) > 2:
                            return path
                        if next_cell in basic_cells and next_cell not in path:
                            result = dfs(next_cell, path + [next_cell], False)
                            if result:
                                return result
            else:
                for new_i in range(self.num_sources):
                    if new_i != i:
                        next_cell = (new_i, j)
                        if next_cell == start_cell and len(path) > 2:
                            return path
                        if next_cell in basic_cells and next_cell not in path:
                            result = dfs(next_cell, path + [next_cell], True)
                            if result:
                                return result
            
            return None
        
        for first_direction in [True, False]:
            result = dfs(start_cell, [start_cell], first_direction)
            if result:
                return result
        
        return None
    
    def input_existing_allocation(self):
        print("\n" + "="*60)
        print("INPUT EXISTING IBFS ALLOCATION")
        print("="*60)
        
        problem_type = input("\nIs this a (1) Minimization or (2) Maximization problem? [1/2]: ").strip()
        self.is_maximization = (problem_type == '2')
        
        self.num_sources = int(input("Enter number of sources: "))
        self.num_destinations = int(input("Enter number of destinations: "))
        
        print(f"\nEnter cost matrix ({self.num_sources} x {self.num_destinations}):")
        self.cost_matrix = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
        for i in range(self.num_sources):
            row = list(map(float, input(f"Row {i+1}: ").split()))
            self.cost_matrix[i] = row
        
        print("\nEnter supply values:")
        self.supply = list(map(float, input().split()))
        
        print("Enter demand values:")
        self.demand = list(map(float, input().split()))
        
        print(f"\nEnter allocation matrix ({self.num_sources} x {self.num_destinations}):")
        print("(Enter 0 for unallocated cells)")
        self.allocation = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
        for i in range(self.num_sources):
            row = list(map(float, input(f"Row {i+1}: ").split()))
            self.allocation[i] = row
        
        self.display_transportation_table("Input IBFS")
        
        self.verify_ibfs()
    
    def verify_ibfs(self):
        print("\n--- IBFS Verification ---")
        
        row_sums = [sum(row) for row in self.allocation]
        col_sums = [sum(self.allocation[i][j] for i in range(self.num_sources)) for j in range(self.num_destinations)]
        
        print("\nSupply Check:")
        supply_ok = True
        for i in range(self.num_sources):
            status = "✓" if abs(row_sums[i] - self.supply[i]) < 1e-10 else "✗"
            print(f"  Source {i+1}: Allocated {row_sums[i]:.0f} / Supply {self.supply[i]:.0f} {status}")
            if abs(row_sums[i] - self.supply[i]) >= 1e-10:
                supply_ok = False
        
        print("\nDemand Check:")
        demand_ok = True
        for j in range(self.num_destinations):
            status = "✓" if abs(col_sums[j] - self.demand[j]) < 1e-10 else "✗"
            print(f"  Destination {j+1}: Allocated {col_sums[j]:.0f} / Demand {self.demand[j]:.0f} {status}")
            if abs(col_sums[j] - self.demand[j]) >= 1e-10:
                demand_ok = False
        
        num_basic = sum(1 for i in range(self.num_sources) for j in range(self.num_destinations) if self.allocation[i][j] > 0)
        required_basic = self.num_sources + self.num_destinations - 1
        
        print(f"\nBasic Variables Check:")
        print(f"  Number of basic cells: {int(num_basic)}")
        print(f"  Required (m + n - 1): {required_basic}")
        
        if num_basic == required_basic:
            print("  Status: Non-degenerate BFS ✓")
        elif num_basic < required_basic:
            print("  Status: Degenerate BFS (need epsilon allocation)")
        else:
            print("  Status: Invalid - too many allocations")
        
        if supply_ok and demand_ok:
            print("\n*** IBFS is VALID and FEASIBLE ***")
            total_cost = self.calculate_total_cost()
        else:
            print("\n*** IBFS has errors - Check allocations ***")
    
    def interpret_solution(self):
        print("\n" + "="*60)
        print("SOLUTION INTERPRETATION")
        print("="*60)
        
        print("\nFinal Allocation:")
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > 0:
                    print(f"  Ship {self.allocation[i][j]:.0f} units from Source {i+1} to Destination {j+1} (cost: {self.cost_matrix[i][j]:.0f})")
        
        dummy_row = self.num_sources - 1 if self.num_sources > len(self.supply) else -1
        dummy_col = self.num_destinations - 1 if self.num_destinations > len(self.demand) else -1
        
        if dummy_row >= 0:
            dummy_alloc = sum(self.allocation[dummy_row][j] for j in range(self.num_destinations))
            if dummy_alloc > 0:
                print(f"\n  Note: {dummy_alloc:.0f} units of UNMET DEMAND (dummy source allocation)")
        
        if dummy_col >= 0:
            dummy_alloc = sum(self.allocation[i][dummy_col] for i in range(self.num_sources))
            if dummy_alloc > 0:
                print(f"\n  Note: {dummy_alloc:.0f} units of UNUSED SUPPLY (dummy destination allocation)")
        
        total = self.calculate_total_cost()
        
        print("\n--- Feasibility Discussion ---")
        print("The solution is FEASIBLE because:")
        print("1. All supply constraints are satisfied")
        print("2. All demand constraints are satisfied")
        print("3. All allocations are non-negative")
        print("4. Number of basic variables = m + n - 1")


class AssignmentProblem:
    
    def __init__(self):
        self.cost_matrix = None
        self.original_matrix = None
        self.n = 0
        self.is_maximization = False
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("ASSIGNMENT PROBLEM - INPUT")
        print("="*60)
        
        problem_type = input("\nIs this a (1) Minimization or (2) Maximization problem? [1/2]: ").strip()
        self.is_maximization = (problem_type == '2')
        
        num_rows = int(input("Enter number of agents/workers: "))
        num_cols = int(input("Enter number of tasks/jobs: "))
        
        print(f"\nEnter cost/profit matrix ({num_rows} x {num_cols}):")
        matrix = []
        for i in range(num_rows):
            row = list(map(float, input(f"Row {i+1}: ").split()))
            matrix.append(row)
        
        self.cost_matrix = [row[:] for row in matrix]
        self.original_matrix = [row[:] for row in matrix]
        self.original_rows = len(matrix)
        self.original_cols = len(matrix[0]) if matrix else 0
        
        self.balance_problem()
        
    def balance_problem(self):
        rows = len(self.cost_matrix)
        cols = len(self.cost_matrix[0]) if self.cost_matrix else 0
        
        if rows != cols:
            print(f"\nMatrix is not square ({rows} x {cols}). Adding dummy row/column.")
            
            if rows < cols:
                for _ in range(cols - rows):
                    self.cost_matrix.append([0.0 for _ in range(cols)])
                print(f"Added {cols - rows} dummy row(s)")
            else:
                for row in self.cost_matrix:
                    row.extend([0.0 for _ in range(rows - cols)])
                print(f"Added {rows - cols} dummy column(s)")
        
        self.n = len(self.cost_matrix)
        
        if self.is_maximization:
            print("\nConverting maximization to minimization...")
            max_val = max(max(row) for row in self.cost_matrix)
            self.cost_matrix = [[max_val - val for val in row] for row in self.cost_matrix]
            print(f"Subtracted all values from {max_val}")
        
    def hungarian_method(self):
        print("\n" + "="*60)
        print("HUNGARIAN METHOD (ASSIGNMENT ALGORITHM)")
        print("="*60)
        
        matrix = deep_copy_matrix(self.cost_matrix)
        
        print("\nStep 1: Row Reduction")
        for i in range(self.n):
            min_val = min(matrix[i])
            matrix[i] = [val - min_val for val in matrix[i]]
            print(f"  Row {i+1}: Subtract {min_val:.0f}")
        
        self.display_matrix(matrix, "After Row Reduction")
        
        print("\nStep 2: Column Reduction")
        for j in range(self.n):
            column = [matrix[i][j] for i in range(self.n)]
            min_val = min(column)
            for i in range(self.n):
                matrix[i][j] -= min_val
            print(f"  Column {j+1}: Subtract {min_val:.0f}")
        
        self.display_matrix(matrix, "After Column Reduction")
        
        iteration = 0
        while True:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            assignment, num_lines = self.find_optimal_assignment(matrix)
            
            print(f"Minimum lines to cover zeros: {num_lines}")
            
            if num_lines == self.n:
                print("\n*** OPTIMAL ASSIGNMENT FOUND ***")
                break
            
            print("\nStep 3: Improving the matrix")
            matrix = self.improve_matrix(matrix)
            self.display_matrix(matrix, f"After Improvement (Iteration {iteration})")
        
        self.display_assignment(assignment)
        return assignment
    
    def display_matrix(self, matrix, title="Matrix"):
        print(f"\n{title}")
        print_matrix(matrix, columns=[f'Task {j+1}' for j in range(self.n)], index=[f'Agent {i+1}' for i in range(self.n)])
    
    def find_optimal_assignment(self, matrix):
        n = self.n
        assignment = [-1] * n
        
        row_covered = [False] * n
        col_covered = [False] * n
        
        for i in range(n):
            for j in range(n):
                if matrix[i][j] == 0 and not row_covered[i] and not col_covered[j]:
                    assignment[i] = j
                    row_covered[i] = True
                    col_covered[j] = True
                    break
        
        num_assigned = sum(1 for a in assignment if a != -1)
        
        marked_rows = set()
        marked_cols = set()
        
        for i in range(n):
            if assignment[i] == -1:
                marked_rows.add(i)
        
        changed = True
        while changed:
            changed = False
            
            for i in marked_rows:
                for j in range(n):
                    if matrix[i][j] == 0 and j not in marked_cols:
                        marked_cols.add(j)
                        changed = True
            
            for j in marked_cols:
                for i in range(n):
                    if assignment[i] == j and i not in marked_rows:
                        marked_rows.add(i)
                        changed = True
        
        lines_through_rows = set(range(n)) - marked_rows
        lines_through_cols = marked_cols
        
        num_lines = len(lines_through_rows) + len(lines_through_cols)
        
        return assignment, num_lines
    
    def improve_matrix(self, matrix):
        n = self.n
        
        row_covered = [False] * n
        col_covered = [False] * n
        
        assignment = [-1] * n
        for i in range(n):
            for j in range(n):
                if matrix[i][j] == 0 and not row_covered[i] and not col_covered[j]:
                    assignment[i] = j
                    row_covered[i] = True
                    col_covered[j] = True
                    break
        
        row_covered = [False] * n
        col_covered = [False] * n
        
        marked_rows = set()
        for i in range(n):
            if assignment[i] == -1:
                marked_rows.add(i)
        
        changed = True
        while changed:
            changed = False
            for i in list(marked_rows):
                for j in range(n):
                    if matrix[i][j] == 0 and j not in col_covered:
                        col_covered[j] = True
                        changed = True
            
            for j in range(n):
                if col_covered[j]:
                    for i in range(n):
                        if assignment[i] == j and i not in marked_rows:
                            marked_rows.add(i)
                            changed = True
        
        for i in range(n):
            if i not in marked_rows:
                row_covered[i] = True
        
        uncovered_elements = []
        for i in range(n):
            for j in range(n):
                if not row_covered[i] and not col_covered[j]:
                    uncovered_elements.append(matrix[i][j])
        
        if uncovered_elements:
            min_uncovered = min(uncovered_elements)
        else:
            min_uncovered = 0
        
        print(f"  Minimum uncovered element: {min_uncovered:.0f}")
        
        for i in range(n):
            for j in range(n):
                if not row_covered[i] and not col_covered[j]:
                    matrix[i][j] -= min_uncovered
                elif row_covered[i] and col_covered[j]:
                    matrix[i][j] += min_uncovered
        
        return matrix
    
    def display_assignment(self, assignment):
        print("\n" + "="*60)
        print("OPTIMAL ASSIGNMENT")
        print("="*60)
        
        total_cost = 0
        orig_rows = getattr(self, 'original_rows', len(self.original_matrix))
        orig_cols = getattr(self, 'original_cols', len(self.original_matrix[0]) if self.original_matrix else 0)
        for i, j in enumerate(assignment):
            if j != -1 and i < orig_rows and j < orig_cols:
                cost = self.original_matrix[i][j]
                total_cost += cost
                print(f"Agent {i+1} -> Task {j+1} (Cost/Profit: {cost:.0f})")
        
        if self.is_maximization:
            print(f"\nTotal Profit: {total_cost:.0f}")
        else:
            print(f"\nTotal Cost: {total_cost:.0f}")


class IntegerProgramming:
    
    def __init__(self):
        self.simplex_solver = None
        
    def branch_and_bound(self):
        print("\n" + "="*60)
        print("INTEGER PROGRAMMING - BRANCH AND BOUND")
        print("="*60)
        
        self.simplex_solver = SimplexSolver()
        obj_coeffs, constraints, constraint_types, rhs_values = self.simplex_solver.get_problem_input()
        
        integer_vars_input = input("\nWhich variables must be integers? (e.g., '1 2' for x1, x2, or 'all'): ").strip()
        if integer_vars_input.lower() == 'all':
            integer_vars = list(range(self.simplex_solver.num_decision_vars))
        else:
            integer_vars = [int(x) - 1 for x in integer_vars_input.split()]
        
        binary_only = input("Are these binary (0-1) variables? [y/n]: ").strip().lower() == 'y'
        
        self.simplex_solver.setup_initial_tableau(obj_coeffs, constraints, constraint_types, rhs_values)
        solution, z_value = self.simplex_solver.solve()
        
        if solution is None:
            print("LP relaxation has no solution")
            return None
        
        print("\n" + "="*60)
        print("BRANCH AND BOUND PROCESS")
        print("="*60)
        
        all_integer = True
        fractional_var = None
        fractional_value = None
        
        for var_idx in integer_vars:
            var_name = f'x{var_idx + 1}'
            value = solution.get(var_name, 0)
            if abs(value - round(value)) > 1e-6:
                all_integer = False
                if fractional_var is None:
                    fractional_var = var_idx
                    fractional_value = value
        
        if all_integer:
            print("\nLP solution is already integer - OPTIMAL")
            return solution, z_value
        
        print(f"\nFractional variable found: x{fractional_var + 1} = {fractional_value:.4f}")
        
        floor_val = int(math.floor(fractional_value))
        ceil_val = int(math.ceil(fractional_value))
        
        print(f"\nBranching on x{fractional_var + 1}:")
        print(f"  Branch 1: x{fractional_var + 1} <= {floor_val}")
        print(f"  Branch 2: x{fractional_var + 1} >= {ceil_val}")
        
        if binary_only:
            print(f"\nFor binary problem:")
            print(f"  Branch 1: x{fractional_var + 1} = 0")
            print(f"  Branch 2: x{fractional_var + 1} = 1")
        
        print("\nNote: Full branch and bound tree exploration requires solving subproblems.")
        print("The optimal integer solution would be found by exploring all branches.")
        
        return solution, z_value


class KnapsackProblem:
    
    def __init__(self):
        self.items = []
        self.capacity = 0
        self.allow_multiple = False
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("KNAPSACK PROBLEM - INPUT")
        print("="*60)
        
        n = int(input("\nEnter number of items: "))
        
        self.items = []
        for i in range(n):
            print(f"\nItem {i+1}:")
            value = float(input("  Value/Profit: "))
            weight = float(input("  Weight: "))
            self.items.append({'id': i+1, 'value': value, 'weight': weight})
        
        self.capacity = float(input("\nEnter knapsack capacity: "))
        
        self.allow_multiple = input("Allow selecting each item multiple times? [y/n]: ").strip().lower() == 'y'
        
    def solve_01_knapsack(self):
        print("\n" + "="*60)
        print("0-1 KNAPSACK - DYNAMIC PROGRAMMING")
        print("="*60)
        
        n = len(self.items)
        W = int(self.capacity)
        
        dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
        
        print("\nBuilding DP table...")
        
        for i in range(1, n + 1):
            item = self.items[i-1]
            w = int(item['weight'])
            v = item['value']
            
            for j in range(W + 1):
                if w <= j:
                    dp[i][j] = max(dp[i-1][j], dp[i-1][j-w] + v)
                else:
                    dp[i][j] = dp[i-1][j]
        
        headers = ['Item\\Cap'] + list(range(W + 1))
        print("\nDP Table:")
        for i in range(n + 1):
            row_label = f"Item {i}" if i > 0 else "None"
            print(f"{row_label}: {dp[i][:min(W+1, 20)]}" + ("..." if W > 19 else ""))
        
        selected = []
        j = W
        for i in range(n, 0, -1):
            if dp[i][j] != dp[i-1][j]:
                selected.append(self.items[i-1])
                j -= int(self.items[i-1]['weight'])
        
        print("\n" + "="*60)
        print("OPTIMAL SOLUTION")
        print("="*60)
        
        print("\nSelected Items:")
        total_weight = 0
        total_value = 0
        for item in selected:
            print(f"  Item {item['id']}: Value = {item['value']}, Weight = {item['weight']}")
            total_weight += item['weight']
            total_value += item['value']
        
        print(f"\nTotal Value: {total_value}")
        print(f"Total Weight: {total_weight} / {self.capacity}")
        
        return dp[n][W], selected
    
    def solve_unbounded_knapsack(self):
        print("\n" + "="*60)
        print("UNBOUNDED KNAPSACK - DYNAMIC PROGRAMMING")
        print("="*60)
        
        W = int(self.capacity)
        
        dp = [0] * (W + 1)
        item_used = [-1] * (W + 1)
        
        for j in range(1, W + 1):
            for i, item in enumerate(self.items):
                w = int(item['weight'])
                v = item['value']
                
                if w <= j and dp[j - w] + v > dp[j]:
                    dp[j] = dp[j - w] + v
                    item_used[j] = i
        
        print("\nDP Array (Maximum value for each capacity):")
        print(dp[:min(W+1, 20)], "..." if W > 19 else "")
        
        selected = {}
        j = W
        while j > 0 and item_used[j] != -1:
            item_idx = item_used[j]
            item = self.items[item_idx]
            
            if item_idx not in selected:
                selected[item_idx] = 0
            selected[item_idx] += 1
            
            j -= int(item['weight'])
        
        print("\n" + "="*60)
        print("OPTIMAL SOLUTION")
        print("="*60)
        
        print("\nSelected Items:")
        total_weight = 0
        total_value = 0
        for item_idx, count in selected.items():
            item = self.items[item_idx]
            print(f"  Item {item['id']}: {count} times (Value = {item['value']} each, Weight = {item['weight']} each)")
            total_weight += count * item['weight']
            total_value += count * item['value']
        
        print(f"\nTotal Value: {total_value}")
        print(f"Total Weight: {total_weight} / {self.capacity}")
        
        return dp[W], selected
    
    def solve(self):
        if self.allow_multiple:
            return self.solve_unbounded_knapsack()
        else:
            return self.solve_01_knapsack()


class TravellingSalesmanProblem:
    
    def __init__(self):
        self.distance_matrix = None
        self.n = 0
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("TRAVELLING SALESMAN PROBLEM - INPUT")
        print("="*60)
        
        self.n = int(input("\nEnter number of cities: "))
        
        print(f"\nEnter distance matrix ({self.n} x {self.n}):")
        print("(Use a large number like 99999 for infinity/no direct path)")
        
        self.distance_matrix = [[0.0 for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.n):
            row = list(map(float, input(f"Row {i+1} (from city {i+1}): ").split()))
            self.distance_matrix[i] = row
        
        for i in range(self.n):
            self.distance_matrix[i][i] = float('inf')
        
    def prims_algorithm(self):
        print("\n" + "="*60)
        print("PRIM'S ALGORITHM - MINIMUM SPANNING TREE")
        print("="*60)
        
        n = self.n
        selected = [False] * n
        mst_edges = []
        total_weight = 0
        
        selected[0] = True
        print("\nStarting from city 1")
        
        for step in range(n - 1):
            min_edge = float('inf')
            min_i, min_j = -1, -1
            
            for i in range(n):
                if selected[i]:
                    for j in range(n):
                        if not selected[j] and self.distance_matrix[i][j] < min_edge:
                            min_edge = self.distance_matrix[i][j]
                            min_i, min_j = i, j
            
            if min_i != -1:
                selected[min_j] = True
                mst_edges.append((min_i + 1, min_j + 1, min_edge))
                total_weight += min_edge
                print(f"\nStep {step + 1}: Add edge ({min_i + 1}, {min_j + 1}) with weight {min_edge:.0f}")
                print(f"  Selected cities: {[i+1 for i in range(n) if selected[i]]}")
        
        print("\n" + "="*60)
        print("MINIMUM SPANNING TREE")
        print("="*60)
        
        print("\nMST Edges:")
        for edge in mst_edges:
            print(f"  City {edge[0]} -- City {edge[1]}: {edge[2]:.0f}")
        
        print(f"\nTotal MST Weight: {total_weight:.0f}")
        
        print("\n" + "-"*60)
        print("TSP APPROXIMATION (2-approximation using MST)")
        print("-"*60)
        
        adj_list = {i: [] for i in range(n)}
        for i, j, w in mst_edges:
            adj_list[i-1].append(j-1)
            adj_list[j-1].append(i-1)
        
        visited = [False] * n
        tour = []
        
        def dfs(node):
            visited[node] = True
            tour.append(node + 1)
            for neighbor in adj_list[node]:
                if not visited[neighbor]:
                    dfs(neighbor)
        
        dfs(0)
        tour.append(1)
        
        print(f"\nApproximate TSP Tour: {' -> '.join(map(str, tour))}")
        
        tour_cost = 0
        for i in range(len(tour) - 1):
            tour_cost += self.distance_matrix[tour[i]-1][tour[i+1]-1]
        
        print(f"Tour Cost: {tour_cost:.0f}")
        
        return mst_edges, total_weight
    
    def branch_and_bound_tsp(self):
        print("\n" + "="*60)
        print("TSP - BRANCH AND BOUND (REDUCED MATRIX METHOD)")
        print("="*60)
        
        matrix = [row[:] for row in self.distance_matrix]
        
        print("\nInitial Cost Matrix:")
        self.display_tsp_matrix(matrix)
        
        print("\nStep 1: Row Reduction")
        row_min = [0.0] * self.n
        for i in range(self.n):
            valid_vals = [val for val in matrix[i] if not math.isinf(val)]
            if valid_vals:
                row_min[i] = min(valid_vals)
                matrix[i] = [val - row_min[i] if not math.isinf(val) else val for val in matrix[i]]
        
        print(f"Row minimums: {row_min}")
        self.display_tsp_matrix(matrix, "After Row Reduction")
        
        print("\nStep 2: Column Reduction")
        col_min = [0.0] * self.n
        for j in range(self.n):
            column_vals = [matrix[i][j] for i in range(self.n) if not math.isinf(matrix[i][j])]
            if column_vals:
                col_min[j] = min(column_vals)
                for i in range(self.n):
                    if not math.isinf(matrix[i][j]):
                        matrix[i][j] -= col_min[j]
        
        print(f"Column minimums: {col_min}")
        self.display_tsp_matrix(matrix, "After Column Reduction")
        
        lower_bound = sum(row_min) + sum(col_min)
        print(f"\nInitial Lower Bound: {lower_bound:.0f}")
        
        print("\nNote: Full B&B requires exploring the solution tree.")
        print("For small problems, brute force can find optimal:")
        
        if self.n <= 8:
            self.brute_force_tsp()
        
        return lower_bound
    
    def brute_force_tsp(self):
        print("\n" + "-"*60)
        print("BRUTE FORCE TSP SOLUTION")
        print("-"*60)
        
        cities = list(range(1, self.n))
        min_cost = float('inf')
        best_tour = None
        
        for perm in permutations(cities):
            tour = [0] + list(perm) + [0]
            cost = 0
            
            for i in range(len(tour) - 1):
                cost += self.distance_matrix[tour[i]][tour[i+1]]
            
            if cost < min_cost:
                min_cost = cost
                best_tour = tour
        
        if best_tour:
            tour_display = [x + 1 for x in best_tour]
            print(f"\nOptimal Tour: {' -> '.join(map(str, tour_display))}")
            print(f"Optimal Cost: {min_cost:.0f}")
        
        return best_tour, min_cost
    
    def display_tsp_matrix(self, matrix, title="Matrix"):
        print(f"\n{title}")
        print_matrix(matrix, columns=[f'To {j+1}' for j in range(self.n)], index=[f'From {i+1}' for i in range(self.n)])


def main_menu():
    print("\n" + "="*70)
    print("         OPERATIONS RESEARCH SOLVER")
    print("         Comprehensive Menu-Based Solution System")
    print("="*70)
    
    while True:
        print("\n" + "-"*70)
        print("MAIN MENU")
        print("-"*70)
        print("1.  Simplex Method (Maximization/Minimization)")
        print("2.  Simplex - Analyze Existing Tableau")
        print("3.  Simplex - Sensitivity Analysis")
        print("4.  Transportation Problem")
        print("5.  Assignment Problem (Hungarian Method)")
        print("6.  Integer Programming (Branch and Bound)")
        print("7.  Knapsack Problem")
        print("8.  Travelling Salesman Problem")
        print("9.  Exit")
        print("-"*70)
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            simplex_menu()
        elif choice == '2':
            tableau_analysis_menu()
        elif choice == '3':
            sensitivity_analysis_menu()
        elif choice == '4':
            transportation_menu()
        elif choice == '5':
            assignment_menu()
        elif choice == '6':
            integer_programming_menu()
        elif choice == '7':
            knapsack_menu()
        elif choice == '8':
            tsp_menu()
        elif choice == '9':
            print("\nThank you for using the OR Solver!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")


def simplex_menu():
    print("\n" + "="*60)
    print("SIMPLEX METHOD")
    print("="*60)
    print("1. Solve complete problem")
    print("2. Solve specific number of iterations (show zero and first iteration)")
    
    choice = input("\nChoice: ").strip()
    
    solver = SimplexSolver()
    obj_coeffs, constraints, constraint_types, rhs_values = solver.get_problem_input()
    solver.setup_initial_tableau(obj_coeffs, constraints, constraint_types, rhs_values)
    
    if choice == '2':
        n_iter = int(input("\nHow many iterations to perform? (e.g., 1 for zero and first iteration): "))
        solution, z_value = solver.solve_n_iterations(n_iter)
    else:
        solution, z_value = solver.solve()
    
    if solution:
        do_sensitivity = input("\nPerform sensitivity analysis? [y/n]: ").strip().lower()
        if do_sensitivity == 'y':
            solver.sensitivity_analysis()


def tableau_analysis_menu():
    print("\n" + "="*60)
    print("TABLEAU ANALYSIS")
    print("="*60)
    
    analyzer = SimplexTableauAnalyzer()
    analyzer.input_existing_tableau()
    analyzer.analyze_tableau()
    
    continue_simplex = input("\nContinue simplex from this tableau? [y/n]: ").strip().lower()
    if continue_simplex == 'y':
        solver = SimplexSolver()
        solver.tableau = analyzer.tableau
        solver.var_names = analyzer.var_names
        solver.basic_vars = analyzer.basic_vars
        solver.non_basic_vars = [v for v in analyzer.var_names if v not in analyzer.basic_vars]
        
        is_max = input("Is this a maximization problem? [y/n]: ").strip().lower()
        solver.is_maximization = (is_max == 'y')
        
        solver.num_decision_vars = sum(1 for v in analyzer.var_names if v.startswith('x'))
        solver.num_constraints = len(analyzer.basic_vars)
        
        solver.solve()


def sensitivity_analysis_menu():
    print("\n" + "="*60)
    print("SENSITIVITY ANALYSIS (from optimal tableau)")
    print("="*60)
    
    analyzer = SimplexTableauAnalyzer()
    analyzer.input_existing_tableau()
    
    solver = SimplexSolver()
    solver.tableau = analyzer.tableau
    solver.var_names = analyzer.var_names
    solver.basic_vars = analyzer.basic_vars
    solver.non_basic_vars = [v for v in analyzer.var_names if v not in analyzer.basic_vars]
    
    is_max = input("Is this a maximization problem? [y/n]: ").strip().lower()
    solver.is_maximization = (is_max == 'y')
    
    solver.num_decision_vars = sum(1 for v in analyzer.var_names if v.startswith('x'))
    solver.num_constraints = len(analyzer.basic_vars)
    
    solver.sensitivity_analysis()


def transportation_menu():
    print("\n" + "="*60)
    print("TRANSPORTATION PROBLEM")
    print("="*60)
    print("1. Enter new problem")
    print("2. Enter existing IBFS allocation (for MODI optimization)")
    
    choice = input("\nChoice: ").strip()
    
    tp = TransportationProblem()
    
    if choice == '1':
        tp.get_problem_input()
        
        print("\nSelect Initial Basic Feasible Solution (IBFS) Method:")
        print("1. Northwest Corner Method")
        print("2. Least Cost Method")
        print("3. Vogel's Approximation Method (VAM)")
        
        ibfs_choice = input("\nChoice: ").strip()
        
        if ibfs_choice == '1':
            tp.northwest_corner_method()
        elif ibfs_choice == '2':
            tp.least_cost_method()
        elif ibfs_choice == '3':
            tp.vogels_approximation_method()
    else:
        tp.input_existing_allocation()
    
    optimize = input("\nOptimize using MODI method? [y/n]: ").strip().lower()
    if optimize == 'y':
        tp.modi_method()
        
        interpret = input("\nShow solution interpretation? [y/n]: ").strip().lower()
        if interpret == 'y':
            tp.interpret_solution()


def assignment_menu():
    print("\n" + "="*60)
    print("ASSIGNMENT PROBLEM")
    print("="*60)
    
    ap = AssignmentProblem()
    ap.get_problem_input()
    ap.hungarian_method()


def integer_programming_menu():
    print("\n" + "="*60)
    print("INTEGER PROGRAMMING")
    print("="*60)
    print("1. Binary Integer Programming (0-1)")
    print("2. General Integer Programming")
    print("3. Mixed Integer Programming")
    
    choice = input("\nChoice: ").strip()
    
    ip = IntegerProgramming()
    ip.branch_and_bound()


def knapsack_menu():
    print("\n" + "="*60)
    print("KNAPSACK PROBLEM")
    print("="*60)
    
    kp = KnapsackProblem()
    kp.get_problem_input()
    kp.solve()


def tsp_menu():
    print("\n" + "="*60)
    print("TRAVELLING SALESMAN PROBLEM")
    print("="*60)
    print("1. Prim's Algorithm (MST-based approximation)")
    print("2. Branch and Bound (Reduced Matrix)")
    
    choice = input("\nChoice: ").strip()
    
    tsp = TravellingSalesmanProblem()
    tsp.get_problem_input()
    
    if choice == '1':
        tsp.prims_algorithm()
    elif choice == '2':
        tsp.branch_and_bound_tsp()


if __name__ == "__main__":
    main_menu()
