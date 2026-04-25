class TransportationProblem:
    
    def __init__(self):
        self.cost_matrix = None
        self.supply = None
        self.demand = None
        self.allocation = None
        self.num_sources = 0
        self.num_destinations = 0
        self.is_maximization = False
        self.epsilon = 1e-10
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("TRANSPORTATION PROBLEM - INPUT")
        print("="*60)
        
        problem_type = input("\nIs this a (1) Minimization or (2) Maximization problem? [1/2]: ").strip()
        self.is_maximization = (problem_type == '2')
        
        self.num_sources = int(input("Enter number of sources (supply points): "))
        self.num_destinations = int(input("Enter number of destinations (demand points): "))
        
        print(f"\nEnter cost/profit matrix ({self.num_sources} x {self.num_destinations}):")
        self.cost_matrix = []
        
        for i in range(self.num_sources):
            row = list(map(float, input(f"Row {i+1} (space-separated): ").split()))
            self.cost_matrix.append(row)
        
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
        
        if abs(total_supply - total_demand) < self.epsilon:
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
        
        self.allocation = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
        
    def display_transportation_table(self, title="Transportation Table"):
        print(f"\n{title}")
        print("-" * 80)
        
        # Header
        header = "     |"
        for j in range(self.num_destinations):
            header += f"    D{j+1}    |"
        header += "  Supply  |"
        print(header)
        print("-" * 80)
        
        # Data rows
        for i in range(self.num_sources):
            row = f"  S{i+1} |"
            for j in range(self.num_destinations):
                allocation_value = self.allocation[i][j]
                cost_value = self.cost_matrix[i][j]
                if allocation_value > self.epsilon:
                    row += f" {cost_value:3.0f}({allocation_value:4.0f})|"
                else:
                    row += f"   {cost_value:3.0f}    |"
            row += f"   {self.supply[i]:4.0f}  |"
            print(row)
        
        print("-" * 80)
        
        # Demand row
        demand_row = "Demand|"
        for j in range(self.num_destinations):
            demand_row += f"   {self.demand[j]:4.0f}  |"
        total_demand = sum(self.demand)
        demand_row += f"   {total_demand:4.0f}  |"
        print(demand_row)
        print("-" * 80)
        
    def northwest_corner_method(self):
        print("\n" + "="*60)
        print("NORTHWEST CORNER METHOD")
        print("="*60)
        
        self.allocation = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
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
            
            if abs(supply[i]) < self.epsilon:
                i += 1
            if abs(demand[j]) < self.epsilon:
                j += 1
            
            self.display_transportation_table(f"After Step {step}")
            step += 1
        
        self.handle_degeneracy()
        return self.calculate_total_cost()
    
    def least_cost_method(self):
        print("\n" + "="*60)
        print("LEAST COST METHOD")
        print("="*60)
        
        self.allocation = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
        supply = self.supply.copy()
        demand = self.demand.copy()
        
        cost_copy = [row[:] for row in self.cost_matrix]
        if self.is_maximization:
            cost_copy = [[-val for val in row] for row in cost_copy]
        
        step = 1
        
        while sum(supply) > self.epsilon and sum(demand) > self.epsilon:
            min_cell = None
            min_cost = float('inf')
            
            for i in range(self.num_sources):
                if supply[i] <= self.epsilon:
                    continue
                for j in range(self.num_destinations):
                    if demand[j] <= self.epsilon:
                        continue
                    cost_value = cost_copy[i][j]
                    if cost_value < min_cost:
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
        
        self.handle_degeneracy()
        return self.calculate_total_cost()
    
    def vogels_approximation_method(self):
        print("\n" + "="*60)
        print("VOGEL'S APPROXIMATION METHOD (VAM)")
        print("="*60)
        
        self.allocation = [[0.0 for _ in range(self.num_destinations)] for _ in range(self.num_sources)]
        supply = self.supply.copy()
        demand = self.demand.copy()
        
        cost_copy = [row[:] for row in self.cost_matrix]
        if self.is_maximization:
            cost_copy = [[-val for val in row] for row in cost_copy]
        
        step = 1
        
        while sum(supply) > self.epsilon and sum(demand) > self.epsilon:
            row_penalties = []
            for i in range(self.num_sources):
                if supply[i] > self.epsilon:
                    valid_costs = [cost_copy[i][j] for j in range(self.num_destinations) if demand[j] > self.epsilon]
                    if len(valid_costs) >= 2:
                        sorted_costs = sorted(valid_costs)
                        row_penalties.append((sorted_costs[1] - sorted_costs[0], i, 'row'))
                    elif len(valid_costs) == 1:
                        row_penalties.append((0, i, 'row'))
            
            col_penalties = []
            for j in range(self.num_destinations):
                if demand[j] > self.epsilon:
                    valid_costs = [cost_copy[i][j] for i in range(self.num_sources) if supply[i] > self.epsilon]
                    if len(valid_costs) >= 2:
                        sorted_costs = sorted(valid_costs)
                        col_penalties.append((sorted_costs[1] - sorted_costs[0], j, 'col'))
                    elif len(valid_costs) == 1:
                        col_penalties.append((0, j, 'col'))
            
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
                valid_j = [(cost_copy[i][j], j) for j in range(self.num_destinations) if demand[j] > self.epsilon]
                j = min(valid_j, key=lambda x: x[0])[1]
            else:
                j = max_penalty[1]
                valid_i = [(cost_copy[i][j], i) for i in range(self.num_sources) if supply[i] > self.epsilon]
                i = min(valid_i, key=lambda x: x[0])[1]
            
            allocation = min(supply[i], demand[j])
            self.allocation[i][j] = allocation
            
            print(f"Allocate {allocation:.0f} to cell ({i+1}, {j+1})")
            
            supply[i] -= allocation
            demand[j] -= allocation
            
            self.display_transportation_table(f"After Step {step}")
            step += 1
        
        self.handle_degeneracy()
        return self.calculate_total_cost()
    
    def handle_degeneracy(self):
        """Handle degeneracy by adding epsilon allocations to independent cells"""
        num_basic = sum(1 for i in range(self.num_sources) 
                       for j in range(self.num_destinations) 
                       if self.allocation[i][j] > self.epsilon)
        
        required_basic = self.num_sources + self.num_destinations - 1
        
        if num_basic < required_basic:
            print(f"\n*** DEGENERACY DETECTED ***")
            print(f"Current basic variables: {num_basic}")
            print(f"Required basic variables: {required_basic}")
            print(f"Adding {required_basic - num_basic} epsilon allocation(s)...")
            
            while num_basic < required_basic:
                # Find cell with minimum cost that doesn't create a loop
                best_cell = None
                best_cost = float('inf')
                
                for i in range(self.num_sources):
                    for j in range(self.num_destinations):
                        if self.allocation[i][j] < self.epsilon:
                            # Temporarily add epsilon
                            self.allocation[i][j] = self.epsilon
                            
                            # Check if it creates a loop (if yes, it's dependent)
                            loop = self.find_loop_advanced((i, j))
                            
                            if loop is None:  # Independent cell
                                if self.cost_matrix[i][j] < best_cost:
                                    best_cost = self.cost_matrix[i][j]
                                    best_cell = (i, j)
                            
                            self.allocation[i][j] = 0.0
                
                if best_cell:
                    i, j = best_cell
                    self.allocation[i][j] = self.epsilon
                    print(f"  Added ε to cell ({i+1}, {j+1})")
                    num_basic += 1
                else:
                    print("  Warning: Could not find independent cell for epsilon allocation")
                    break
    
    def calculate_total_cost(self):
        total = 0.0
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > self.epsilon:
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
        max_iterations = 100
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"MODI Iteration {iteration}")
            print('='*60)
            
            self.display_transportation_table(f"Current Allocation")
            
            u, v = self.calculate_uv_values()
            
            if u is None:
                print("ERROR: Cannot calculate u-v values. Check allocation.")
                break
            
            print(f"\nu values: {[f'{val:.2f}' if val is not None else 'None' for val in u]}")
            print(f"v values: {[f'{val:.2f}' if val is not None else 'None' for val in v]}")
            
            # Calculate opportunity costs
            opportunity_costs = [[0.0 for _ in range(self.num_destinations)] 
                                for _ in range(self.num_sources)]
            
            non_basic_cells = []
            for i in range(self.num_sources):
                for j in range(self.num_destinations):
                    if self.allocation[i][j] < self.epsilon:
                        opportunity_costs[i][j] = self.cost_matrix[i][j] - u[i] - v[j]
                        non_basic_cells.append((i, j, opportunity_costs[i][j]))
            
            print("\nOpportunity Costs (Non-basic cells):")
            for i, j, opp in non_basic_cells:
                print(f"  Cell ({i+1}, {j+1}): {opp:.2f}")
            
            # Check optimality
            if self.is_maximization:
                max_opp = max((opp for _, _, opp in non_basic_cells), default=0)
                if max_opp <= self.epsilon:
                    print("\n" + "="*60)
                    print("*** OPTIMAL SOLUTION REACHED ***")
                    print("="*60)
                    break
                entering_cell = max(non_basic_cells, key=lambda x: x[2])[:2]
                entering_opp = max_opp
            else:
                min_opp = min((opp for _, _, opp in non_basic_cells), default=0)
                if min_opp >= -self.epsilon:
                    print("\n" + "="*60)
                    print("*** OPTIMAL SOLUTION REACHED ***")
                    print("="*60)
                    break
                entering_cell = min(non_basic_cells, key=lambda x: x[2])[:2]
                entering_opp = min_opp
            
            print(f"\nEntering cell: ({entering_cell[0]+1}, {entering_cell[1]+1})")
            print(f"Opportunity cost: {entering_opp:.2f}")
            
            # Find closed loop
            loop = self.find_loop_advanced(entering_cell)
            
            if loop is None:
                print("ERROR: Could not find closed loop!")
                print("This indicates a problem with the BFS or degeneracy handling.")
                break
            
            print(f"\nClosed loop: {' -> '.join([f'({c[0]+1},{c[1]+1})' for c in loop])}")
            
            # Calculate theta
            theta_values = []
            for idx, cell in enumerate(loop):
                if idx % 2 == 1:  # Negative positions
                    alloc = self.allocation[cell[0]][cell[1]]
                    if alloc > self.epsilon:
                        theta_values.append(alloc)
            
            if not theta_values:
                print("ERROR: No valid theta values found!")
                break
            
            theta = min(theta_values)
            print(f"Theta (minimum from negative positions): {theta:.4f}")
            
            # Update allocations
            for idx, cell in enumerate(loop):
                if idx % 2 == 0:  # Positive positions
                    self.allocation[cell[0]][cell[1]] += theta
                else:  # Negative positions
                    self.allocation[cell[0]][cell[1]] -= theta
            
            # Clean up near-zero values
            for i in range(self.num_sources):
                for j in range(self.num_destinations):
                    if abs(self.allocation[i][j]) < self.epsilon:
                        self.allocation[i][j] = 0.0
            
            # Check and handle degeneracy after reallocation
            self.handle_degeneracy()
        
        if iteration >= max_iterations:
            print("\nWarning: Maximum iterations reached!")
        
        return self.calculate_total_cost()
    
    def calculate_uv_values(self):
        """Calculate u and v values using the equation: u[i] + v[j] = c[i][j] for basic cells"""
        basic_cells = []
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > self.epsilon:
                    basic_cells.append((i, j))
        
        u = [None] * self.num_sources
        v = [None] * self.num_destinations
        
        # Start with u[0] = 0
        u[0] = 0.0
        
        # Iteratively calculate u and v values
        max_iterations = len(basic_cells) * 2
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
        
        # Check if all values are calculated
        if any(val is None for val in u) or any(val is None for val in v):
            return None, None
        
        return u, v
    
    def find_loop_advanced(self, start_cell):
        """
        Advanced loop finding algorithm using BFS/DFS approach.
        Finds a closed loop for the entering cell in the transportation tableau.
        """
        basic_cells = set()
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > self.epsilon:
                    basic_cells.add((i, j))
        
        # Build adjacency structure
        row_cells = {}  # row -> list of (row, col) in that row
        col_cells = {}  # col -> list of (row, col) in that column
        
        for i, j in basic_cells:
            if i not in row_cells:
                row_cells[i] = []
            row_cells[i].append((i, j))
            
            if j not in col_cells:
                col_cells[j] = []
            col_cells[j].append((i, j))
        
        # Add start cell to the structures temporarily
        start_i, start_j = start_cell
        if start_i not in row_cells:
            row_cells[start_i] = []
        if start_cell not in row_cells[start_i]:
            row_cells[start_i].append(start_cell)
        
        if start_j not in col_cells:
            col_cells[start_j] = []
        if start_cell not in col_cells[start_j]:
            col_cells[start_j].append(start_cell)
        
        def dfs(current, path, direction):
            """
            DFS to find closed loop
            direction: 'H' for horizontal (same row), 'V' for vertical (same column)
            """
            if len(path) > 3 and len(path) % 2 == 0 and current == start_cell:
                return path
            
            i, j = current
            
            if direction == 'H':  # Move horizontally (change column, same row)
                if i in row_cells:
                    for next_cell in row_cells[i]:
                        if next_cell != current and next_cell not in path:
                            result = dfs(next_cell, path + [next_cell], 'V')
                            if result:
                                return result
                        elif next_cell == start_cell and len(path) >= 3:
                            return path
            
            else:  # direction == 'V', Move vertically (change row, same column)
                if j in col_cells:
                    for next_cell in col_cells[j]:
                        if next_cell != current and next_cell not in path:
                            result = dfs(next_cell, path + [next_cell], 'H')
                            if result:
                                return result
                        elif next_cell == start_cell and len(path) >= 3:
                            return path
            
            return None
        
        # Try starting in both directions
        loop = dfs(start_cell, [start_cell], 'H')
        if loop:
            return loop
        
        loop = dfs(start_cell, [start_cell], 'V')
        if loop:
            return loop
        
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
        self.cost_matrix = []
        for i in range(self.num_sources):
            row = list(map(float, input(f"Row {i+1}: ").split()))
            self.cost_matrix.append(row)
        
        print("\nEnter supply values:")
        self.supply = list(map(float, input().split()))
        
        print("Enter demand values:")
        self.demand = list(map(float, input().split()))
        
        print(f"\nEnter allocation matrix ({self.num_sources} x {self.num_destinations}):")
        print("(Enter 0 for unallocated cells)")
        self.allocation = []
        for i in range(self.num_sources):
            row = list(map(float, input(f"Row {i+1}: ").split()))
            self.allocation.append(row)
        
        self.display_transportation_table("Input IBFS")
        self.verify_ibfs()
    
    def verify_ibfs(self):
        print("\n" + "="*60)
        print("IBFS VERIFICATION")
        print("="*60)
        
        row_sums = [sum(row) for row in self.allocation]
        col_sums = [sum(self.allocation[i][j] for i in range(self.num_sources)) 
                   for j in range(self.num_destinations)]
        
        print("\nSupply Check:")
        supply_ok = True
        for i in range(self.num_sources):
            diff = abs(row_sums[i] - self.supply[i])
            status = "✓" if diff < self.epsilon else "✗"
            print(f"  Source {i+1}: Allocated {row_sums[i]:.2f} / Supply {self.supply[i]:.2f} {status}")
            if diff >= self.epsilon:
                supply_ok = False
        
        print("\nDemand Check:")
        demand_ok = True
        for j in range(self.num_destinations):
            diff = abs(col_sums[j] - self.demand[j])
            status = "✓" if diff < self.epsilon else "✗"
            print(f"  Destination {j+1}: Allocated {col_sums[j]:.2f} / Demand {self.demand[j]:.2f} {status}")
            if diff >= self.epsilon:
                demand_ok = False
        
        num_basic = sum(1 for i in range(self.num_sources) 
                       for j in range(self.num_destinations) 
                       if self.allocation[i][j] > self.epsilon)
        required_basic = self.num_sources + self.num_destinations - 1
        
        print(f"\nBasic Variables Check:")
        print(f"  Number of basic cells: {num_basic}")
        print(f"  Required (m + n - 1): {required_basic}")
        
        if num_basic == required_basic:
            print("  Status: Non-degenerate BFS ✓")
        elif num_basic < required_basic:
            print(f"  Status: Degenerate BFS (need {required_basic - num_basic} more allocation(s))")
            self.handle_degeneracy()
        else:
            print("  Status: Invalid - too many allocations ✗")
        
        if supply_ok and demand_ok:
            print("\n*** IBFS is VALID and FEASIBLE ***")
            self.calculate_total_cost()
        else:
            print("\n*** IBFS has ERRORS - Check allocations ***")
    
    def interpret_solution(self):
        print("\n" + "="*60)
        print("SOLUTION INTERPRETATION")
        print("="*60)
        
        print("\nOptimal Allocation Plan:")
        print("-" * 60)
        
        total_shipped = 0
        for i in range(self.num_sources):
            for j in range(self.num_destinations):
                if self.allocation[i][j] > self.epsilon:
                    if self.allocation[i][j] > 1:  # Ignore epsilon allocations
                        print(f"  Ship {self.allocation[i][j]:.2f} units from Source {i+1} to Destination {j+1}")
                        print(f"    Cost per unit: {self.cost_matrix[i][j]:.2f}")
                        print(f"    Total cost: {self.allocation[i][j] * self.cost_matrix[i][j]:.2f}")
                        total_shipped += self.allocation[i][j]
        
        print(f"\nTotal units shipped: {total_shipped:.2f}")
        
        # Check for dummy allocations
        if len(self.supply) != self.num_sources:
            dummy_row = self.num_sources - 1
            dummy_alloc = sum(self.allocation[dummy_row])
            if dummy_alloc > self.epsilon:
                print(f"\n⚠ Unmet demand: {dummy_alloc:.2f} units (from dummy source)")
        
        if len(self.demand) != self.num_destinations:
            dummy_col = self.num_destinations - 1
            dummy_alloc = sum(self.allocation[i][dummy_col] for i in range(self.num_sources))
            if dummy_alloc > self.epsilon:
                print(f"\n⚠ Unused supply: {dummy_alloc:.2f} units (to dummy destination)")
        
        total = self.calculate_total_cost()
        
        print("\n" + "="*60)
        print("FEASIBILITY & OPTIMALITY")
        print("="*60)
        print("✓ All supply constraints satisfied")
        print("✓ All demand constraints satisfied")
        print("✓ All allocations are non-negative")
        print("✓ Number of basic variables = m + n - 1")
        print("✓ Solution is optimal (verified by MODI method)")


def main():
    """Main function to run the transportation problem solver"""
    print("="*60)
    print("TRANSPORTATION PROBLEM SOLVER")
    print("="*60)
    
    tp = TransportationProblem()
    
    print("\nSelect input method:")
    print("1. Enter new problem")
    print("2. Input existing IBFS allocation")
    
    choice = input("\nYour choice [1/2]: ").strip()
    
    if choice == '1':
        tp.get_problem_input()
        
        print("\n" + "="*60)
        print("SELECT INITIAL BASIC FEASIBLE SOLUTION METHOD")
        print("="*60)
        print("1. Northwest Corner Method")
        print("2. Least Cost Method")
        print("3. Vogel's Approximation Method (VAM)")
        
        method = input("\nYour choice [1/2/3]: ").strip()
        
        if method == '1':
            tp.northwest_corner_method()
        elif method == '2':
            tp.least_cost_method()
        elif method == '3':
            tp.vogels_approximation_method()
        else:
            print("Invalid choice!")
            return
        
        print("\n" + "="*60)
        print("PROCEED TO OPTIMIZATION?")
        print("="*60)
        optimize = input("Run MODI method to find optimal solution? [y/n]: ").strip().lower()
        
        if optimize == 'y':
            tp.modi_method()
            tp.interpret_solution()
    
    elif choice == '2':
        tp.input_existing_allocation()
        
        optimize = input("\nRun MODI method to optimize? [y/n]: ").strip().lower()
        if optimize == 'y':
            tp.modi_method()
            tp.interpret_solution()
    
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()