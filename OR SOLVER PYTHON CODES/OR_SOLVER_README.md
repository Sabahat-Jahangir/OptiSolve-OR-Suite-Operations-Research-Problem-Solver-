# Operations Research Solver

A comprehensive, menu-based Python program for solving Operations Research problems. Compatible with Python 3.9 - 3.14.

## Requirements
- Python 3.9+
- NumPy
- Pandas

Install dependencies:
```bash
pip install numpy pandas
```

## Running the Program
```bash
python or_solver.py
```

## Features Covered

### 1. Simplex Method
- **Maximization and Minimization** problems
- Handles **≤, ≥, =** constraints
- Big-M method for artificial variables
- Shows **all tableaus step by step**
- Option to solve specific iterations (zero and first iteration)
- Complete sensitivity analysis

### 2. Sensitivity Analysis (From Teacher's Question Style)
- **Rate of change** in optimal solution for RHS changes
- **Feasibility range** computation
- Why a variable is **not in optimal solution**
- **Minimum coefficient** for variable to enter basis
- **Adding new constraints** (with Dual Simplex indication)
- **Adding new variables** (with reduced cost calculation)
- **Multiple parameter changes** (recompute using c_B and B⁻¹)

### 3. Tableau Analyzer
- Input an **existing tableau** (from mid-exam questions)
- Analyze if **maximization or minimization**
- Identify **basic and non-basic variables**
- Find **entering and leaving variables**
- Continue simplex from given tableau

### 4. Transportation Problem
- **Northwest Corner Method** (NWCM)
- **Least Cost Method** (LCM)
- **Vogel's Approximation Method** (VAM)
- **MODI Method** for optimization
- Input **existing IBFS** allocation
- **Dummy handling** for unbalanced problems
- IBFS verification and solution interpretation

### 5. Assignment Problem
- **Hungarian Method**
- Maximization and Minimization
- **Dummy row/column** handling for non-square matrices
- Step-by-step display

### 6. Integer Programming
- **Branch and Bound** method
- Binary (0-1) Integer Programming
- LP relaxation solution

### 7. Knapsack Problem
- **0-1 Knapsack** (Dynamic Programming)
- **Unbounded Knapsack** (items selectable multiple times)
- Complete DP table display

### 8. Travelling Salesman Problem
- **Prim's Algorithm** for MST
- **2-approximation** using MST
- **Branch and Bound** (Reduced Matrix Method)
- Brute force for small problems

## Example Usage

### Solving Question 1 from Teacher's Mid (Simplex Tableau Analysis)

From the image, the tableau is:
```
       x1   x2   x3   x4   x5   x6   x7   x8   Solution
Z       0   -5    0    4    1  -10    5    0      620
x8      0    0    0   -8   -3    0    0    1       12
x3      0    3    1    0    1   -1    3    0        6
x1      1   -1    0    1    0    4    0    0        0
```

1. Select Option 2 (Analyze Existing Tableau)
2. Enter total variables: 8
3. Enter constraints: 3
4. Enter variable names: x1 x2 x3 x4 x5 x6 x7 x8
5. Enter basic variables: x8 x3 x1
6. Enter the rows

The program will:
- Identify basic and non-basic variables
- Determine if maximization/minimization
- Find entering variable (most negative in Z row)
- Compute ratios and find leaving variable

### Solving Question 2 from Teacher's Mid (GPU Allocation)

```
Maximize Z = 0.8*xA + 0.75*xB + 0.85*xC
Subject to:
3xA + 1xB + 4xC = 600    (GPU-hours: exactly)
2xA + 4xB + 2xC >= 480   (Memory: at least)
2xA + 3xB + 3xC <= 540   (Storage: at most)
xA, xB, xC >= 0
```

1. Select Option 1 (Simplex Method)
2. Choose Maximization
3. Enter 3 decision variables
4. Enter 3 constraints
5. Select "solve specific iterations" to see zero and first iteration

### Solving Sensitivity Analysis (Teacher's Past Paper Question 2)

After solving, use the sensitivity analysis menu:
- Option 1: Change in RHS (for part a)
- Option 2: Objective coefficient change (for part b - why x2 not in solution)
- Option 3: Add new constraint (for part c - QC procedure)
- Option 4: Add new variable (for part d - Lithium Sulphur battery)
- Option 5: Multiple parameter changes (for part e - simultaneous changes)

### Transportation Problem with Existing IBFS

From Teacher's Question 1 (Cloud Dynamics):
1. Select Option 4 (Transportation Problem)
2. Choose "Enter existing IBFS allocation"
3. Enter cost matrix, supply, demand
4. Enter the allocation matrix with values in parentheses
5. Apply MODI method for optimization

## Menu Structure

```
MAIN MENU
1. Simplex Method (Maximization/Minimization)
2. Simplex - Analyze Existing Tableau
3. Simplex - Sensitivity Analysis
4. Transportation Problem
5. Assignment Problem (Hungarian Method)
6. Integer Programming (Branch and Bound)
7. Knapsack Problem
8. Travelling Salesman Problem
9. Exit
```

## Notes

- All inputs are taken dynamically - no code modification needed
- Every step and tableau is displayed
- Compatible with exam-style questions where partial data is given
- Handles special cases like degeneracy, infeasibility, unboundedness
