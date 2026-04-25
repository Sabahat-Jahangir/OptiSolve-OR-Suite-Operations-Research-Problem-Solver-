def print_dp_table(dp, capacity, items, title="DYNAMIC PROGRAMMING TABLE"):
    """Print the DP table in a formatted manner"""
    print("\n" + "="*80)
    print(title)
    print("="*80)
    print(f"Rows represent items (0 to {items})")
    print(f"Columns represent capacity (0 to {capacity})")
    print("-"*80)

    header = "Item\\Cap"
    for w in range(int(capacity) + 1):
        header += f"\t{w}"
    print(header)
    print("-"*80)

    for i in range(items + 1):
        row = f"  {i}"
        for w in range(int(capacity) + 1):
            row += f"\t{dp[i][w]}"
        print(row)
    print("-"*80)

def print_iteration_step(i, w, dp, weight, value, include, exclude, item_type=""):
    """Print details of each iteration step"""
    print(f"\n{item_type}Item {i}, Capacity {w}:")
    print(f"  Weight: {weight}, Value: {value}")
    print(f"  Exclude item: {exclude}")
    if include >= 0:
        print(f"  Include item: {value} + previous = {include}")
        print(f"  -> Maximum: {max(include, exclude)}")
    else:
        print(f"  Cannot include (weight > capacity)")
        print(f"  -> Maximum: {exclude}")

def knapsack_01_dp(weights, values, capacity, show_iterations=True):
    """
    0/1 Knapsack Problem - Each item can be taken at most once
    """
    n = len(weights)

    print("\n" + "="*80)
    print("0/1 KNAPSACK PROBLEM - DYNAMIC PROGRAMMING SOLUTION")
    print("="*80)
    print(f"Number of items: {n}")
    print(f"Knapsack capacity: {capacity}")
    print("Rule: Each item can be taken at most ONCE")
    print("-"*80)

    print("\nITEM DETAILS:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Value/Weight':<15}")
    print("-"*80)
    for i in range(n):
        if weights[i] > 0:
            ratio = values[i] / weights[i]
        else:
            ratio = 0
        print(f"{i+1:<8} {weights[i]:<10} {values[i]:<10} {ratio:<15.2f}")
    print("-"*80)

    # Initialize DP table
    dp = [[0 for _ in range(int(capacity) + 1)] for _ in range(n + 1)]

    print("\n" + "="*80)
    print("BUILDING DP TABLE")
    print("="*80)
    print("Formula: dp[i][w] = max(dp[i-1][w], value[i-1] + dp[i-1][w-weight[i-1]])")
    print("-"*80)

    for i in range(1, n + 1):
        item_idx = i - 1
        weight = weights[item_idx]
        value = values[item_idx]

        if show_iterations:
            print(f"\n{'='*80}")
            print(f"PROCESSING ITEM {i} (Weight: {weight}, Value: {value})")
            print(f"{'='*80}")

        for w in range(int(capacity) + 1):
            exclude = dp[i-1][w]

            if weight <= w:
                include = value + dp[i-1][w-int(weight)]
                dp[i][w] = max(include, exclude)

                if show_iterations and w > 0 and (w % 5 == 0 or w == int(capacity)):
                    print_iteration_step(i, w, dp, weight, value, include, exclude)
            else:
                dp[i][w] = exclude
                if show_iterations and w == int(capacity):
                    print_iteration_step(i, w, dp, weight, value, -1, exclude)

    print_dp_table(dp, capacity, n)

    # Backtrack to find selected items
    print("\n" + "="*80)
    print("BACKTRACKING TO FIND SELECTED ITEMS")
    print("="*80)

    selected_items = []
    w = int(capacity)
    total_weight = 0
    total_value = 0

    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            item_idx = i - 1
            selected_items.append(item_idx)
            total_weight += weights[item_idx]
            total_value += values[item_idx]
            print(f"Item {i} SELECTED (Weight: {weights[item_idx]}, Value: {values[item_idx]})")
            w -= int(weights[item_idx])
        else:
            print(f"Item {i} NOT selected")

    selected_items.reverse()

    print("\n" + "="*80)
    print("FINAL SOLUTION")
    print("="*80)
    print(f"Maximum value: {dp[n][int(capacity)]}")
    print(f"Total weight: {total_weight}/{capacity}")
    print(f"Selected items: {[i+1 for i in selected_items]}")
    print("-"*80)

    print("\nDETAILED SELECTION:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10}")
    print("-"*80)
    for idx in selected_items:
        print(f"{idx+1:<8} {weights[idx]:<10} {values[idx]:<10}")
    print("-"*80)
    print(f"{'TOTAL':<8} {total_weight:<10} {total_value:<10}")
    print("="*80)

    return dp[n][int(capacity)], selected_items

def knapsack_unbounded_dp(weights, values, capacity, show_iterations=True):
    """
    Unbounded Knapsack Problem - Each item can be taken unlimited times
    """
    n = len(weights)

    print("\n" + "="*80)
    print("UNBOUNDED KNAPSACK PROBLEM - DYNAMIC PROGRAMMING SOLUTION")
    print("="*80)
    print(f"Number of items: {n}")
    print(f"Knapsack capacity: {capacity}")
    print("Rule: Each item can be taken UNLIMITED times")
    print("-"*80)

    print("\nITEM DETAILS:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Value/Weight':<15}")
    print("-"*80)
    for i in range(n):
        if weights[i] > 0:
            ratio = values[i] / weights[i]
        else:
            ratio = 0
        print(f"{i+1:<8} {weights[i]:<10} {values[i]:<10} {ratio:<15.2f}")
    print("-"*80)

    # Initialize DP array (1D for unbounded)
    dp = [0] * (int(capacity) + 1)

    print("\n" + "="*80)
    print("BUILDING DP TABLE")
    print("="*80)
    print("Formula: dp[w] = max(dp[w], value[i] + dp[w-weight[i]]) for all items")
    print("Note: We can use the same item multiple times")
    print("-"*80)

    # Keep track of which item was used for each capacity
    item_used = [-1] * (int(capacity) + 1)

    for w in range(1, int(capacity) + 1):
        if show_iterations:
            print(f"\n{'='*60}")
            print(f"CAPACITY {w}")
            print('='*60)

        for i in range(n):
            if weights[i] <= w:
                new_value = values[i] + dp[w - int(weights[i])]
                if new_value > dp[w]:
                    if show_iterations:
                        print(f"  Item {i+1}: {values[i]} + dp[{w-int(weights[i])}]({dp[w-int(weights[i])]}) = {new_value} > current({dp[w]})")
                    dp[w] = new_value
                    item_used[w] = i
                elif show_iterations and new_value == dp[w]:
                    print(f"  Item {i+1}: {values[i]} + dp[{w-int(weights[i])}]({dp[w-int(weights[i])]}) = {new_value} (equal)")

        if show_iterations:
            print(f"  -> dp[{w}] = {dp[w]}")

    print("\n" + "="*80)
    print("DP ARRAY (Final Values)")
    print("="*80)
    print("Capacity:", end=" ")
    for w in range(int(capacity) + 1):
        print(f"{w:5}", end=" ")
    print("\nValue:   ", end=" ")
    for w in range(int(capacity) + 1):
        print(f"{dp[w]:5}", end=" ")
    print("\n" + "-"*80)

    # Backtrack to find selected items
    print("\n" + "="*80)
    print("BACKTRACKING TO FIND SELECTED ITEMS")
    print("="*80)

    selected_items = []
    w = int(capacity)
    total_weight = 0
    total_value = 0

    while w > 0 and item_used[w] != -1:
        item_idx = item_used[w]
        selected_items.append(item_idx)
        total_weight += weights[item_idx]
        total_value += values[item_idx]
        print(f"At capacity {w}: Item {item_idx+1} used (Weight: {weights[item_idx]}, Value: {values[item_idx]})")
        w -= int(weights[item_idx])

    # Count occurrences of each item
    item_count = [0] * n
    for item_idx in selected_items:
        item_count[item_idx] += 1

    print("\n" + "="*80)
    print("FINAL SOLUTION")
    print("="*80)
    print(f"Maximum value: {dp[int(capacity)]}")
    print(f"Total weight: {total_weight}/{capacity}")
    print("-"*80)

    print("\nDETAILED SELECTION:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Quantity':<10} {'Total Value':<12}")
    print("-"*80)

    for i in range(n):
        if item_count[i] > 0:
            print(f"{i+1:<8} {weights[i]:<10} {values[i]:<10} {item_count[i]:<10} {values[i]*item_count[i]:<12}")

    print("-"*80)
    print(f"{'TOTAL':<8} {total_weight:<10} {'':<10} {sum(item_count):<10} {total_value:<12}")
    print("="*80)

    return dp[int(capacity)], selected_items

def knapsack_bounded_dp(weights, values, quantities, capacity, show_iterations=True):
    """
    Bounded Knapsack Problem - Each item has a limited quantity
    """
    n = len(weights)

    print("\n" + "="*80)
    print("BOUNDED KNAPSACK PROBLEM - DYNAMIC PROGRAMMING SOLUTION")
    print("="*80)
    print(f"Number of items: {n}")
    print(f"Knapsack capacity: {capacity}")
    print("Rule: Each item has a LIMITED quantity")
    print("-"*80)

    print("\nITEM DETAILS:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Quantity':<12} {'Value/Weight':<15}")
    print("-"*80)
    for i in range(n):
        if weights[i] > 0:
            ratio = values[i] / weights[i]
        else:
            ratio = 0
        print(f"{i+1:<8} {weights[i]:<10} {values[i]:<10} {quantities[i]:<12} {ratio:<15.2f}")
    print("-"*80)

    # Initialize DP table
    dp = [[0 for _ in range(int(capacity) + 1)] for _ in range(n + 1)]

    # Track how many of each item at each capacity
    item_counts = [[0 for _ in range(int(capacity) + 1)] for _ in range(n + 1)]

    print("\n" + "="*80)
    print("BUILDING DP TABLE")
    print("="*80)
    print("For each item, we consider taking 0, 1, 2, ..., min(quantity, capacity//weight) copies")
    print("-"*80)

    for i in range(1, n + 1):
        item_idx = i - 1
        weight = weights[item_idx]
        value = values[item_idx]
        max_qty = quantities[item_idx]

        if show_iterations:
            print(f"\n{'='*80}")
            print(f"PROCESSING ITEM {i} (Weight: {weight}, Value: {value}, Max Quantity: {max_qty})")
            print(f"{'='*80}")

        for w in range(int(capacity) + 1):
            # Start with not taking this item
            dp[i][w] = dp[i-1][w]
            item_counts[i][w] = 0

            # Try taking k copies of this item
            max_copies = min(max_qty, w // int(weight)) if weight > 0 else 0

            for k in range(1, max_copies + 1):
                if weight * k <= w:
                    new_value = value * k + dp[i-1][w - int(weight*k)]
                    if new_value > dp[i][w]:
                        dp[i][w] = new_value
                        item_counts[i][w] = k

                        if show_iterations and w > 0 and (w % 5 == 0 or w == int(capacity)):
                            print(f"  Capacity {w}: Taking {k} copies -> Value = {value}*{k} + dp[{i-1}][{w-int(weight*k)}] = {new_value}")

            if show_iterations and w == int(capacity):
                print(f"  -> Best at capacity {w}: {item_counts[i][w]} copies, Total value: {dp[i][w]}")

    print_dp_table(dp, capacity, n, "BOUNDED KNAPSACK DP TABLE")

    # Backtrack to find selected items
    print("\n" + "="*80)
    print("BACKTRACKING TO FIND SELECTED ITEMS")
    print("="*80)

    selected_counts = [0] * n
    total_weight = 0
    total_value = 0

    w = int(capacity)
    for i in range(n, 0, -1):
        item_idx = i - 1
        count = item_counts[i][w]

        if count > 0:
            selected_counts[item_idx] = count
            total_weight += weights[item_idx] * count
            total_value += values[item_idx] * count
            print(f"Item {i}: Selected {count} copies (Weight: {weights[item_idx]}*{count}={weights[item_idx]*count}, Value: {values[item_idx]}*{count}={values[item_idx]*count})")
            w -= int(weights[item_idx]) * count
        else:
            print(f"Item {i}: NOT selected")

    print("\n" + "="*80)
    print("FINAL SOLUTION")
    print("="*80)
    print(f"Maximum value: {dp[n][int(capacity)]}")
    print(f"Total weight: {total_weight}/{capacity}")
    print("-"*80)

    print("\nDETAILED SELECTION:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Quantity':<12} {'Total Weight':<14} {'Total Value':<12}")
    print("-"*80)

    for i in range(n):
        if selected_counts[i] > 0:
            print(f"{i+1:<8} {weights[i]:<10} {values[i]:<10} {selected_counts[i]:<12} {weights[i]*selected_counts[i]:<14} {values[i]*selected_counts[i]:<12}")

    print("-"*80)
    print(f"{'TOTAL':<8} {'':<10} {'':<10} {sum(selected_counts):<12} {total_weight:<14} {total_value:<12}")
    print("="*80)

    return dp[n][int(capacity)], selected_counts

def fractional_knapsack(weights, values, capacity, show_iterations=True):
    """
    Fractional Knapsack Problem - Items can be taken partially
    """
    n = len(weights)

    print("\n" + "="*80)
    print("FRACTIONAL KNAPSACK PROBLEM - GREEDY SOLUTION")
    print("="*80)
    print(f"Number of items: {n}")
    print(f"Knapsack capacity: {capacity}")
    print("Rule: Items can be taken in FRACTIONS (Greedy approach)")
    print("-"*80)

    # Create list of items with their ratios
    items = []
    for i in range(n):
        if weights[i] > 0:
            ratio = values[i] / weights[i]
        else:
            ratio = 0
        items.append([i, weights[i], values[i], ratio])

    # Sort by ratio (descending)
    items.sort(key=lambda x: x[3], reverse=True)

    print("\nITEMS SORTED BY VALUE/WEIGHT RATIO (Descending):")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Ratio':<15}")
    print("-"*80)
    for item in items:
        print(f"{item[0]+1:<8} {item[1]:<10} {item[2]:<10} {item[3]:<15.2f}")
    print("-"*80)

    print("\n" + "="*80)
    print("GREEDY SELECTION PROCESS")
    print("="*80)

    total_value = 0.0
    remaining_capacity = capacity
    selected = []

    for item in items:
        item_idx = item[0]
        weight = item[1]
        value = item[2]
        ratio = item[3]

        if remaining_capacity >= weight:
            # Take full item
            fraction = 1.0
            total_value += value
            remaining_capacity -= weight
            selected.append([item_idx, weight, value, fraction, value])

            if show_iterations:
                print(f"\nItem {item_idx+1}: Take FULL item")
                print(f"  Weight: {weight}, Value: {value}, Ratio: {ratio:.2f}")
                print(f"  Remaining capacity: {remaining_capacity}")
                print(f"  Total value so far: {total_value:.2f}")

        elif remaining_capacity > 0:
            # Take fraction of item
            fraction = remaining_capacity / weight
            value_taken = value * fraction
            total_value += value_taken
            selected.append([item_idx, weight, value, fraction, value_taken])

            if show_iterations:
                print(f"\nItem {item_idx+1}: Take FRACTION of item")
                print(f"  Weight: {weight}, Value: {value}, Ratio: {ratio:.2f}")
                print(f"  Fraction taken: {fraction:.4f} ({fraction*100:.2f}%)")
                print(f"  Weight taken: {remaining_capacity:.2f}")
                print(f"  Value taken: {value_taken:.2f}")
                print(f"  Total value so far: {total_value:.2f}")

            remaining_capacity = 0

        else:
            if show_iterations:
                print(f"\nItem {item_idx+1}: SKIP (no capacity left)")
            break

    print("\n" + "="*80)
    print("FINAL SOLUTION")
    print("="*80)
    print(f"Maximum value (Fractional): {total_value:.2f}")
    print(f"Capacity used: {capacity - remaining_capacity}/{capacity}")
    print("-"*80)

    print("\nDETAILED SELECTION:")
    print(f"{'Item':<8} {'Weight':<10} {'Value':<10} {'Fraction':<12} {'Value Taken':<15}")
    print("-"*80)

    total_weight = 0
    for sel in selected:
        item_idx, weight, value, fraction, value_taken = sel
        weight_taken = weight * fraction
        total_weight += weight_taken
        print(f"{item_idx+1:<8} {weight:<10} {value:<10} {fraction:<12.4f} {value_taken:<15.2f}")

    print("-"*80)
    print(f"{'TOTAL':<8} {total_weight:<10.2f} {'':<10} {'':<12} {total_value:<15.2f}")
    print("="*80)

    return total_value

def get_input_data():
    """Get input data from user"""
    print("\n" + "="*80)
    print("INPUT DATA")
    print("="*80)

    n = int(input("Enter number of items: "))

    weights = []
    values = []
    quantities = []

    print(f"\nEnter details for {n} items:")
    for i in range(n):
        print(f"\nItem {i+1}:")
        w = float(input("  Weight: "))
        v = float(input("  Value: "))
        weights.append(w)
        values.append(v)
        quantities.append(0)  # Will be filled if needed

    capacity = float(input("\nEnter knapsack capacity: "))

    return weights, values, quantities, capacity, n

def main():
    """Main function to run the knapsack solver"""
    print("="*80)
    print("COMPLETE KNAPSACK PROBLEM SOLVER")
    print("="*80)

    print("\n" + "="*80)
    print("SELECT INPUT METHOD")
    print("="*80)
    print("1. Use sample data")
    print("2. Enter custom data")

    input_choice = input("\nYour choice [1/2]: ").strip()

    if input_choice == '2':
        weights, values, quantities, capacity, n = get_input_data()
    else:
        # Sample data
        weights = [3, 4, 5, 6]
        values = [2, 3, 4, 1]
        quantities = [2, 1, 3, 4]  # For bounded knapsack
        capacity = 8
        n = len(weights)

        print("\n" + "="*80)
        print("USING SAMPLE DATA")
        print("="*80)
        print(f"Weights: {weights}")
        print(f"Values:  {values}")
        print(f"Quantities (for bounded): {quantities}")
        print(f"Capacity: {capacity}")

    print("\n" + "="*80)
    print("SELECT KNAPSACK TYPE")
    print("="*80)
    print("1. 0/1 Knapsack (Each item at most once) - with detailed steps")
    print("2. 0/1 Knapsack (Each item at most once) - final result only")
    print("3. Unbounded Knapsack (Unlimited quantity) - with detailed steps")
    print("4. Unbounded Knapsack (Unlimited quantity) - final result only")
    print("5. Bounded Knapsack (Limited quantity) - with detailed steps")
    print("6. Bounded Knapsack (Limited quantity) - final result only")
    print("7. Fractional Knapsack (Items can be fractional) - with detailed steps")
    print("8. Fractional Knapsack (Items can be fractional) - final result only")
    print("9. Solve ALL types and compare")
    print("="*80)

    choice = input("\nYour choice [1-9]: ").strip()

    if choice == '1':
        knapsack_01_dp(weights, values, capacity, show_iterations=True)

    elif choice == '2':
        knapsack_01_dp(weights, values, capacity, show_iterations=False)

    elif choice == '3':
        knapsack_unbounded_dp(weights, values, capacity, show_iterations=True)

    elif choice == '4':
        knapsack_unbounded_dp(weights, values, capacity, show_iterations=False)

    elif choice == '5':
        if input_choice != '2':
            # Use predefined quantities for sample data
            pass
        else:
            # Get quantities from user
            print("\nEnter quantities for bounded knapsack:")
            quantities = []
            for i in range(n):
                q = int(input(f"  Maximum quantity for item {i+1}: "))
                quantities.append(q)

        knapsack_bounded_dp(weights, values, quantities, capacity, show_iterations=True)

    elif choice == '6':
        if input_choice != '2':
            pass
        else:
            print("\nEnter quantities for bounded knapsack:")
            quantities = []
            for i in range(n):
                q = int(input(f"  Maximum quantity for item {i+1}: "))
                quantities.append(q)

        knapsack_bounded_dp(weights, values, quantities, capacity, show_iterations=False)

    elif choice == '7':
        fractional_knapsack(weights, values, capacity, show_iterations=True)

    elif choice == '8':
        fractional_knapsack(weights, values, capacity, show_iterations=False)

    elif choice == '9':
        print("\n" + "="*80)
        print("SOLVING ALL KNAPSACK TYPES")
        print("="*80)

        print("\n\n" + "#"*80)
        print("# 1. 0/1 KNAPSACK")
        print("#"*80)
        val_01, _ = knapsack_01_dp(weights, values, capacity, show_iterations=False)

        print("\n\n" + "#"*80)
        print("# 2. UNBOUNDED KNAPSACK")
        print("#"*80)
        val_unbounded, _ = knapsack_unbounded_dp(weights, values, capacity, show_iterations=False)

        print("\n\n" + "#"*80)
        print("# 3. BOUNDED KNAPSACK")
        print("#"*80)
        if input_choice != '2':
            pass
        else:
            print("\nEnter quantities for bounded knapsack:")
            quantities = []
            for i in range(n):
                q = int(input(f"  Maximum quantity for item {i+1}: "))
                quantities.append(q)
        val_bounded, _ = knapsack_bounded_dp(weights, values, quantities, capacity, show_iterations=False)

        print("\n\n" + "#"*80)
        print("# 4. FRACTIONAL KNAPSACK")
        print("#"*80)
        val_fractional = fractional_knapsack(weights, values, capacity, show_iterations=False)

        print("\n\n" + "="*80)
        print("COMPARISON OF ALL METHODS")
        print("="*80)
        print(f"{'Method':<30} {'Maximum Value':<20}")
        print("-"*80)
        print(f"{'0/1 Knapsack':<30} {val_01:<20}")
        print(f"{'Unbounded Knapsack':<30} {val_unbounded:<20}")
        print(f"{'Bounded Knapsack':<30} {val_bounded:<20}")
        print(f"{'Fractional Knapsack':<30} {val_fractional:<20.2f}")
        print("="*80)

        print("\nNOTE:")
        print("- Fractional >= Unbounded >= Bounded >= 0/1 (in terms of max value)")
        print("- 0/1: Each item can be taken at most once")
        print("- Bounded: Each item has a limited quantity")
        print("- Unbounded: Each item can be taken unlimited times")
        print("- Fractional: Items can be taken in fractions (usually gives highest value)")

    else:
        print("Invalid choice! Running 0/1 Knapsack with detailed steps.")
        knapsack_01_dp(weights, values, capacity, show_iterations=True)

    print("\n" + "="*80)
    print("PROGRAM COMPLETED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    main()
