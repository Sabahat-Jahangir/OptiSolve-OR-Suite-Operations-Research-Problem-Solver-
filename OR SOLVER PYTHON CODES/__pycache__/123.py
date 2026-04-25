## Code for Duality (Primal to Dual Conversion)

print("=" * 60)
print("DUALITY - PRIMAL TO DUAL CONVERSION")
print("=" * 60)
print()

obj_type = input("Enter primal objective (max/min): ").strip().lower()
num_vars = int(input("Enter number of primal variables: "))
num_constraints = int(input("Enter number of primal constraints: "))

print(f"\nEnter primal objective function coefficients:")
c = list(map(float, input().split()))

print(f"\nEnter primal constraint matrix (A):")
A = []
for i in range(num_constraints):
    print(f"Row {i+1}:")
    row = list(map(float, input().split()))
    A.append(row)

print(f"\nEnter constraint operators (<=, >=, ==):")
operators = []
for i in range(num_constraints):
    op = input(f"Constraint {i+1} operator: ").strip()
    operators.append(op)

print(f"\nEnter RHS values (b):")
b = list(map(float, input().split()))

print(f"\nVariable restrictions (type 'unrestricted' for unrestricted variables):")
var_types = []
for i in range(num_vars):
    vtype = input(f"x{i+1}: ").strip().lower()
    var_types.append(vtype)

print("\n" + "=" * 60)
print("DUAL FORMULATION")
print("=" * 60)

# Dual objective
if obj_type == 'max':
    print("\nDual Objective: Minimize")
    dual_obj = 'min'
else:
    print("\nDual Objective: Maximize")
    dual_obj = 'max'

print(f"\nDual objective function:")
print(f"W = ", end="")
for i, bi in enumerate(b):
    if i > 0:
        print(f" + {bi}*y{i+1}", end="")
    else:
        print(f"{bi}*y{i+1}", end="")
print()

# Dual constraints
print(f"\nSubject to:")
for j in range(num_vars):
    constraint_str = ""
    for i in range(num_constraints):
        if i > 0:
            constraint_str += f" + {A[i][j]}*y{i+1}"
        else:
            constraint_str += f"{A[i][j]}*y{i+1}"
    
    # Determine dual constraint sign
    if obj_type == 'max':
        if var_types[j] == 'unrestricted':
            constraint_str += f" = {c[j]}"
        else:
            constraint_str += f" >= {c[j]}"
    else:
        if var_types[j] == 'unrestricted':
            constraint_str += f" = {c[j]}"
        else:
            constraint_str += f" <= {c[j]}"
    
    print(f"  {constraint_str}")

# Dual variable restrictions
print(f"\nDual variable restrictions:")
for i in range(num_constraints):
    if obj_type == 'max':
        if operators[i] == '<=':
            print(f"  y{i+1} >= 0")
        elif operators[i] == '>=':
            print(f"  y{i+1} <= 0")
        else:
            print(f"  y{i+1} unrestricted")
    else:
        if operators[i] == '<=':
            print(f"  y{i+1} <= 0")
        elif operators[i] == '>=':
            print(f"  y{i+1} >= 0")
        else:
            print(f"  y{i+1} unrestricted")

print("\n" + "=" * 60)
print("CONVERSION COMPLETE")
print("=" * 60)
