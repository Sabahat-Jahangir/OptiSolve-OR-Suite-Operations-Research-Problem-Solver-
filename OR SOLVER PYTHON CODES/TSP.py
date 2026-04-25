########### Code in Python language
## Code with Simplex BIG M

class TravelingSalesmanDP:
    
    def __init__(self):
        self.distance_matrix = []
        self.n = 0
        self.memo = {}
        self.path_memo = {}
        
    def get_problem_input(self):
        print("\n" + "="*60)
        print("TRAVELING SALESPERSON PROBLEM - DYNAMIC PROGRAMMING")
        print("="*60)
        
        while True:
            try:
                self.n = int(input("\nEnter number of cities: "))
                if self.n > 0:
                    break
                print("Please enter a positive number.")
            except:
                print("Please enter a valid number.")
        
        print(f"\nEnter distance matrix ({self.n} x {self.n}):")
        print("(Use a large number like 99999 for infinity/no direct path)")
        
        self.distance_matrix = []
        for i in range(self.n):
            while True:
                try:
                    row_input = input(f"Row {i+1} (from city {i+1}): ")
                    values = row_input.split()
                    if len(values) != self.n:
                        print(f"Error: Expected {self.n} values, got {len(values)}")
                        continue
                    
                    row = []
                    for val in values:
                        num = float(val)
                        row.append(num)
                    
                    self.distance_matrix.append(row)
                    break
                except:
                    print("Please enter valid numbers separated by spaces.")
        
        # Set diagonal to infinity (99999)
        for i in range(self.n):
            self.distance_matrix[i][i] = 99999
        
        return True
    
    def g(self, visited_set_tuple, current_city):
        """
        Recursive DP function: g(S, i)
        Minimum cost to visit all cities in set S starting from city 1,
        visiting each city exactly once, and ending at city i
        
        Using formula: g(S, i) = min_{j ∈ S, j ≠ i} [g(S - {i}, j) + C(j, i)]
        """
        
        # Convert tuple to set for easier manipulation
        visited_set = set(visited_set_tuple)
        
        # Create memo key
        key = (visited_set_tuple, current_city)
        
        # Check memo
        if key in self.memo:
            return self.memo[key]
        
        # Base case: if only starting city is visited and we're at starting city
        if visited_set == {0} and current_city == 0:
            self.memo[key] = 0
            self.path_memo[key] = [1]
            return 0
        
        # If set doesn't contain current city or doesn't contain starting city
        if current_city not in visited_set or 0 not in visited_set:
            return 99999
        
        min_cost = 99999
        best_prev_city = -1
        best_path = []
        
        # Try all possible previous cities (j in the formula)
        for prev_city in visited_set:
            if prev_city == current_city:
                continue
            
            # Remove current city from visited set
            prev_set = visited_set - {current_city}
            
            # Convert set to sorted tuple for memo key
            prev_set_tuple = tuple(sorted(prev_set))
            
            # Recursive call
            prev_cost = self.g(prev_set_tuple, prev_city)
            
            # Total cost if we came from prev_city
            total_cost = prev_cost + self.distance_matrix[prev_city][current_city]
            
            if total_cost < min_cost:
                min_cost = total_cost
                best_prev_city = prev_city
                
                # Get the path
                prev_key = (prev_set_tuple, prev_city)
                if prev_key in self.path_memo:
                    best_path = self.path_memo[prev_key].copy()
                    best_path.append(current_city + 1)
        
        # Store in memo
        self.memo[key] = min_cost
        if best_path:
            self.path_memo[key] = best_path
        
        return min_cost
    
    def solve_tsp_dp(self):
        """
        Solve TSP using the exact DP formula from the image
        """
        print("\n" + "="*60)
        print("SOLVING USING DYNAMIC PROGRAMMING FORMULA")
        print("="*60)
        
        n = self.n
        
        # All cities visited (set {0,1,...,n-1}) where 0 is city 1
        all_cities = list(range(n))
        all_cities_tuple = tuple(sorted(all_cities))
        
        print(f"\nComputing g(S, i) for all subsets S containing city 1...")
        print(f"Full set of cities: ", end="")
        cities_display = [str(i+1) for i in range(n)]
        print("{" + ",".join(cities_display) + "}")
        print(f"Starting city: 1")
        
        # Display the formula being used
        print(f"\nUsing formula: g({{1,2,...,{n}}}, i) = min_[k≠i] [C(i,k) + g({{1,2,...,{n}}} - {{i}}, k)]")
        
        min_total_cost = 99999
        best_last_city = -1
        best_path = []
        
        print(f"\n\nFinal step: Complete the tour by returning to city 1")
        print("-" * 50)
        
        # Try all possible last cities before returning to start
        for last_city in range(1, n):  # last_city can't be starting city (0)
            # Cost to visit all cities ending at last_city
            cost_to_last = self.g(all_cities_tuple, last_city)
            
            # Add cost to return to starting city
            return_cost = self.distance_matrix[last_city][0]
            total_cost = cost_to_last + return_cost
            
            print(f"g({{1,...,{n}}}, {last_city+1}) = {cost_to_last:.0f}")
            print(f"  + C({last_city+1},1) = {return_cost:.0f}")
            print(f"  Total = {total_cost:.0f}")
            print()
            
            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_last_city = last_city
                
                # Get the path
                key = (all_cities_tuple, last_city)
                if key in self.path_memo:
                    best_path = self.path_memo[key].copy()
                    best_path.append(1)  # Return to start
        
        print(f"\nMinimum total cost found: {min_total_cost:.0f}")
        
        return best_path, min_total_cost
    
    def display_formula_example(self):
        """
        Display the formula example as shown in the image
        """
        print("\n" + "="*60)
        print("FORMULA FROM IMAGE (g(1,2,3,4) example)")
        print("="*60)
        
        if self.n >= 4:
            print(f"\nFor n=4 cities:")
            print("Formula from image: g({1,2,3,4}) = min_[k in {2,3,4}] [C(1,k) + g(k, {2,3,4} - {k})]")
            print("\nExpanded form:")
            print("g({1,2,3,4}, 1) = min_[k=2,3,4] [C(1,k) + g({k}, {2,3,4} - {k})]")
            print("\nBreaking it down:")
            
            # Show all possibilities
            for k in range(1, 4):
                remaining = []
                for i in range(4):
                    if i != 0 and i != k:
                        remaining.append(str(i+1))
                remaining_str = ",".join(remaining) if remaining else "∅"
                print(f"k={k+1}: C(1,{k+1}) + g({{1,{k+1}}}, {{{remaining_str}}})")
        else:
            print(f"\nGeneral formula for n={self.n}:")
            print(f"g({{1,2,...,{self.n}}}, i) = min_[j∈{{1,...,{self.n}}}, j≠i] [C(i,j) + g({{1,...,{self.n}}} - {{i}}, j)]")
    
    def display_intermediate_calculations(self):
        """
        Display intermediate g(S,i) calculations
        """
        print("\n" + "="*60)
        print("INTERMEDIATE DP CALCULATIONS")
        print("="*60)
        
        # Get all memo keys and sort by set size
        memo_items = []
        for key, value in self.memo.items():
            visited_set_tuple, current_city = key
            memo_items.append((len(visited_set_tuple), visited_set_tuple, current_city, value))
        
        # Sort by set size
        memo_items.sort()
        
        count = 0
        for _, visited_set_tuple, current_city, value in memo_items:
            if value < 99999 and value >= 0:
                # Convert tuple to display format
                cities = []
                for city in visited_set_tuple:
                    cities.append(str(city + 1))
                
                print(f"g({{{','.join(cities)}}}, {current_city+1}) = {value:.0f}")
                count += 1
                
                if count >= 50:  # Limit output
                    print(f"\n... and {len(self.memo) - count} more calculations")
                    break
        
        if count == 0:
            print("No intermediate calculations to display.")
    
    def display_matrix(self):
        """Display the distance matrix"""
        print("\n" + "="*60)
        print("DISTANCE MATRIX")
        print("="*60)
        
        n = self.n
        
        # Header
        header = " " * 8
        for j in range(n):
            header += f"To {j+1:>8}"
        print(header)
        
        print("-" * (8 * (n + 1)))
        
        # Rows
        for i in range(n):
            row_str = f"From {i+1:>2} |"
            for j in range(n):
                val = self.distance_matrix[i][j]
                if val >= 99999:
                    row_str += "     INF"
                else:
                    row_str += f"{val:>8.0f}"
            print(row_str)
    
    def generate_subsets(self, n):
        """Generate all subsets of {0,1,...,n-1} that contain 0"""
        subsets = []
        # Start from 1 (binary 1) which represents {0}
        for mask in range(1, 1 << n):
            if mask & 1:  # Must contain city 0 (city 1)
                subset = []
                for i in range(n):
                    if mask & (1 << i):
                        subset.append(i)
                subsets.append(tuple(sorted(subset)))
        return subsets
    
    def run(self):
        """Main execution function"""
        if not self.get_problem_input():
            return
        
        # Display input matrix
        self.display_matrix()
        
        # Display formula example
        self.display_formula_example()
        
        # Solve TSP
        print("\n" + "="*60)
        print("COMPUTING OPTIMAL TOUR...")
        print("="*60)
        
        # Precompute all subsets to warm up memoization
        print("\nPrecomputing subsets...")
        subsets = self.generate_subsets(self.n)
        
        print(f"\nTotal subsets to compute: {len(subsets)}")
        print("Starting DP computation...")
        
        tour, min_cost = self.solve_tsp_dp()
        
        if tour:
            print("\n" + "="*60)
            print("OPTIMAL SOLUTION FOUND!")
            print("="*60)
            
            print(f"\nOptimal Tour Path:")
            path_str = ""
            for i, city in enumerate(tour):
                path_str += str(city)
                if i < len(tour) - 1:
                    path_str += " → "
            print(path_str)
            
            print(f"\nTotal Distance: {min_cost:.0f}")
            
            # Display intermediate calculations
            if self.n <= 6:
                self.display_intermediate_calculations()
            else:
                print(f"\n(Intermediate calculations omitted for n={self.n} > 6)")
            
            print("\n" + "="*60)
            print("ALGORITHM SUMMARY")
            print("="*60)
            print(f"Number of cities: {self.n}")
            print(f"Total DP states computed: {len(self.memo)}")
            print(f"Optimal tour cost: {min_cost:.0f}")
            
            # Show complexity
            print(f"\nTime complexity: O(n² × 2ⁿ)")
            print(f"For n={self.n}: O({self.n}² × 2^{self.n}) = O({self.n*self.n} × {2**self.n})")
        
        else:
            print("\nNo valid tour found!")
        
        print("\n" + "="*60)
        print("PROGRAM COMPLETED")
        print("="*60)

def main():
    print("="*70)
    print("TRAVELING SALESPERSON PROBLEM - DYNAMIC PROGRAMMING")
    print("="*70)
    print("\nThis program solves TSP using the exact DP formula from your image:")
    print("\nFormula: g(S, i) = min_{j ∈ S, j ≠ i} [g(S - {i}, j) + C(j, i)]")
    print("Where:")
    print("  g(S, i) = min cost to visit all cities in set S")
    print("            starting from city 1, ending at city i")
    print("  C(j, i) = distance from city j to city i")
    
    print("\n" + "-"*70)
    print("EXAMPLE FOR QUICK TESTING (4 cities):")
    print("-"*70)
    print("Number of cities: 4")
    print("Distance matrix:")
    print("Row 1: 0 10 15 20")
    print("Row 2: 10 0 35 25")
    print("Row 3: 15 35 0 30")
    print("Row 4: 20 25 30 0")
    print("\n(Note: 0 on diagonal will be replaced with INF)")
    
    print("\nPress Enter to continue...")
    input()
    
    solver = TravelingSalesmanDP()
    solver.run()

if __name__ == "__main__":
    main()
    

