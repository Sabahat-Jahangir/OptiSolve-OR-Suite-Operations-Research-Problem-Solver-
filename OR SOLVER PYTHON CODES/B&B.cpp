#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>

using namespace std;

// Global constants
const double INF = 1e15;
const double EPS = 1e-7;
const int MAX_R = 15; // Max constraints
const int MAX_C = 15; // Max variables (including slacks)

struct LP_Result {
    bool feasible;
    double objective;
    double vars[MAX_C];
    LP_Result() : feasible(false), objective(-INF) {
        for(int i=0; i<MAX_C; ++i) vars[i] = 0;
    }
};

class SimplexSolver {
private:
    double tableau[MAX_R][MAX_C];
    int basis[MAX_R];
    int m; // Number of constraints
    int n; // Number of original variables
    int total_cols;

public:
    // Initialize tableau: c (obj), A (matrix), b (RHS), num_vars, num_constraints
    void init(double c[], double A[][2], double b[], int num_v, int num_c, 
              double extra_A[][2], double extra_b[], int num_extra) {
        
        n = num_v;
        m = num_c + num_extra;
        total_cols = n + m;

        // Clear tableau
        for(int i=0; i<MAX_R; ++i) 
            for(int j=0; j<MAX_C; ++j) tableau[i][j] = 0;

        // Fill original constraints
        for(int i=0; i<num_c; ++i) {
            for(int j=0; j<n; ++j) tableau[i][j] = A[i][j];
            tableau[i][total_cols] = b[i];
        }

        // Fill branching constraints
        for(int i=0; i<num_extra; ++i) {
            for(int j=0; j<n; ++j) tableau[num_c + i][j] = extra_A[i][j];
            tableau[num_c + i][total_cols] = extra_b[i];
        }

        // Add slack variables and setup basis
        for(int i=0; i<m; ++i) {
            tableau[i][n + i] = 1.0;
            basis[i] = n + i;
        }

        // Fill objective row (Maximization: -c)
        for(int j=0; j<n; ++j) tableau[m][j] = -c[j];
    }

    void pivot(int row, int col) {
        double divisor = tableau[row][col];
        for(int j=0; j<=total_cols; ++j) tableau[row][j] /= divisor;
        for(int i=0; i<=m; ++i) {
            if(i != row) {
                double multiplier = tableau[i][col];
                for(int j=0; j<=total_cols; ++j) tableau[i][j] -= multiplier * tableau[row][j];
            }
        }
        basis[row] = col;
    }

    void printTableau(int iteration, int p_row, int p_col) {
        cout << "\n=== Iteration " << iteration << " ===\n";
        cout << setw(8) << "Basis |";
        for(int j=0; j<total_cols; ++j) cout << setw(10) << "x" << (j+1);
        cout << setw(10) << "RHS\n";
        cout << "------------------------------------------------------------\n";
        for(int i=0; i<m; ++i) {
            cout << setw(6) << "x" << (basis[i]+1) << " |";
            for(int j=0; j<=total_cols; ++j) cout << setw(10) << fixed << setprecision(2) << tableau[i][j];
            cout << "\n";
        }
        cout << "------------------------------------------------------------\n";
        cout << setw(6) << "Z" << " |";
        for(int j=0; j<=total_cols; ++j) cout << setw(10) << tableau[m][j];
        cout << "\n";
        if(p_col != -1) cout << "Pivot: x" << (p_col+1) << " enters, x" << (basis[p_row]+1) << " leaves\n";
    }

    LP_Result solve(bool verbose) {
        int iter = 0;
        // Dual Simplex for feasibility (if RHS is negative)
        while(true) {
            int pr = -1; double min_b = -EPS;
            for(int i=0; i<m; ++i) if(tableau[i][total_cols] < min_b) { min_b = tableau[i][total_cols]; pr = i; }
            if(pr == -1) break;
            int pc = -1;
            for(int j=0; j<total_cols; ++j) if(tableau[pr][j] < -EPS) { pc = j; break; }
            if(pc == -1) return LP_Result(); // Infeasible
            pivot(pr, pc);
        }

        // Standard Primal Simplex
        while(true) {
            int pc = -1; double min_c = -EPS;
            for(int j=0; j<total_cols; ++j) if(tableau[m][j] < min_c) { min_c = tableau[m][j]; pc = j; }
            if(pc == -1) break;
            int pr = -1; double min_ratio = INF;
            for(int i=0; i<m; ++i) {
                if(tableau[i][pc] > EPS) {
                    double ratio = tableau[i][total_cols] / tableau[i][pc];
                    if(ratio < min_ratio) { min_ratio = ratio; pr = i; }
                }
            }
            if(verbose) printTableau(iter++, pr, pc);
            if(pr == -1) { LP_Result res; res.feasible = true; res.objective = INF; return res; }
            pivot(pr, pc);
        }
        if(verbose) { printTableau(iter, -1, -1); cout << "Optimal solution found!\n"; }
        
        LP_Result res;
        res.feasible = true;
        res.objective = tableau[m][total_cols];
        for(int i=0; i<m; ++i) if(basis[i] < n) res.vars[basis[i]] = tableau[i][total_cols];
        return res;
    }
};

class BranchAndBound {
    double c[2], A[2][2], b[2];
    double inc_z;
    double inc_sol[2];
    int nodes;

public:
    BranchAndBound() {
        // Define specific problem: Z = 1x1 + 4x2
        c[0] = 1.0; c[1] = 4.0;
        // 2x1 + 4x2 <= 7
        A[0][0] = 2.0; A[0][1] = 4.0; b[0] = 7.0;
        // 5x1 + 3x2 <= 15
        A[1][0] = 5.0; A[1][1] = 3.0; b[1] = 15.0;
        
        inc_z = -INF;
        nodes = 0;
    }

    void start() {
        cout << "***********************************************\n";
        cout << "*  INTEGER PROGRAMMING PROBLEM               *\n";
        cout << "*  Maximize: Z = x1 + 4x2                    *\n";
        cout << "***********************************************\n\n";
        cout << "########## BRANCH AND BOUND ##########\n";
        
        double lower[2] = {0.0, 0.0}, upper[2] = {INF, INF};
        explore(lower, upper, 0);

        cout << "\n########## COMPLETE ##########\n";
        cout << "Total nodes explored: " << nodes << "\n\n";
        cout << "=============================\n";
        cout << "OPTIMAL INTEGER SOLUTION\n";
        cout << "=============================\n";
        cout << "x1 = " << (int)(inc_sol[0] + 0.5) << "\n";
        cout << "x2 = " << (int)(inc_sol[1] + 0.5) << "\n";
        cout << "-----------------------------\n";
        cout << "Z = " << fixed << setprecision(4) << inc_z << "\n";
        cout << "=============================\n";
    }

private:
    void explore(double L[], double U[], int level) {
        nodes++;
        int current_id = nodes;
        
        // Prepare extra constraints for bounds
        double extra_A[4][2], extra_b[4];
        int num_extra = 0;
        for(int i=0; i<2; ++i) {
            if(L[i] > 0) { // xi >= L -> -xi <= -L
                extra_A[num_extra][i] = -1.0; extra_A[num_extra][1-i] = 0.0;
                extra_b[num_extra] = -L[i]; num_extra++;
            }
            if(U[i] < INF) { // xi <= U
                extra_A[num_extra][i] = 1.0; extra_A[num_extra][1-i] = 0.0;
                extra_b[num_extra] = U[i]; num_extra++;
            }
        }

        if(current_id == 1) cout << "\n=== ROOT NODE ===\n";
        
        SimplexSolver lp;
        lp.init(c, A, b, 2, 2, extra_A, extra_b, num_extra);
        LP_Result res = lp.solve(current_id == 1);

        cout << "\n--- Node " << current_id << " (Level " << level << ", Bound=";
        if(!res.feasible) { cout << "Infeasible) ---\nSolution: Infeasible\n"; return; }
        cout << res.objective << ") ---\n";
        cout << "Solution: x1=" << res.vars[0] << " x2=" << res.vars[1] << " Z=" << res.objective << "\n";

        if(res.objective <= inc_z + EPS) { cout << "Pruned (Bound <= Incumbent)\n"; return; }

        int frac_idx = -1;
        for(int i=0; i<2; ++i) {
            if(abs(res.vars[i] - floor(res.vars[i] + 0.5)) > EPS) { frac_idx = i; break; }
        }

        if(frac_idx == -1) {
            inc_z = res.objective; inc_sol[0] = res.vars[0]; inc_sol[1] = res.vars[1];
            cout << "*** INTEGER SOLUTION FOUND ***\n*** NEW INCUMBENT: Z = " << inc_z << " ***\n";
            return;
        }

        double val = res.vars[frac_idx];
        cout << "Branching on x" << (frac_idx+1) << " = " << val << "\n";
        
        // Manual copy for branches
        double nextL[2], nextU[2];
        
        // Left: xi <= floor(val)
        for(int i=0; i<2; ++i) { nextL[i] = L[i]; nextU[i] = U[i]; }
        nextU[frac_idx] = min(nextU[frac_idx], floor(val));
        cout << "  Left branch: x" << (frac_idx+1) << " <= " << (int)nextU[frac_idx] << "\n";
        explore(nextL, nextU, level + 1);

        // Right: xi >= ceil(val)
        for(int i=0; i<2; ++i) { nextL[i] = L[i]; nextU[i] = U[i]; }
        nextL[frac_idx] = max(nextL[frac_idx], ceil(val));
        cout << "  Right branch: x" << (frac_idx+1) << " >= " << (int)nextL[frac_idx] << "\n";
        explore(nextL, nextU, level + 1);
    }
};

int main() {
    BranchAndBound solver;
    solver.start();
    return 0;
}

