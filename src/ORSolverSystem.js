import React, { useState } from 'react';
import { Calculator, Truck, Users, FileText, AlertCircle, CheckCircle, Download } from 'lucide-react';

const ORSolverSystem = () => {
  const [activeTab, setActiveTab] = useState('simplex');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Simplex State
  const [simplexData, setSimplexData] = useState({
    numVars: 10,
    numConstraints: 10,
    objective: Array(10).fill(0),
    constraints: Array(10).fill(null).map(() => Array(11).fill(0)),
    constraintTypes: Array(10).fill('<='),
    isMaximization: true
  });

  // Assignment State
  const [assignmentData, setAssignmentData] = useState({
    size: 10,
    matrix: Array(10).fill(null).map(() => Array(10).fill(0))
  });

  // Transportation State
  const [transportationData, setTransportationData] = useState({
    sources: 10,
    destinations: 10,
    supply: Array(10).fill(0),
    demand: Array(10).fill(0),
    costs: Array(10).fill(null).map(() => Array(10).fill(0))
  });

  // Simplex Method Implementation
  const solveSimplex = () => {
    try {
      setError(null);
      const { numVars, numConstraints, objective, constraints, constraintTypes, isMaximization } = simplexData;

      // Convert to standard form
      let tableau = [];
      let slackVars = 0;
      let artificialVars = 0;

      // Prepare objective function
      let objRow = [...objective];
      if (isMaximization) {
        objRow = objRow.map(x => -x);
      }

      // Add constraints to tableau
      for (let i = 0; i < numConstraints; i++) {
        let row = [...constraints[i].slice(0, numVars)];
        const rhs = constraints[i][numVars];
        const type = constraintTypes[i];

        if (type === '<=') {
          // Add slack variable
          for (let j = 0; j < numConstraints; j++) {
            row.push(i === j ? 1 : 0);
          }
          slackVars++;
        } else if (type === '>=') {
          // Add surplus and artificial variable
          for (let j = 0; j < numConstraints; j++) {
            row.push(i === j ? -1 : 0);
          }
          for (let j = 0; j < numConstraints; j++) {
            row.push(i === j ? 1 : 0);
          }
          slackVars++;
          artificialVars++;
        } else { // '='
          // Add artificial variable
          for (let j = 0; j < numConstraints; j++) {
            row.push(i === j ? 1 : 0);
          }
          artificialVars++;
        }

        row.push(rhs);
        tableau.push(row);
      }

      // Add objective row
      while (objRow.length < tableau[0].length - 1) {
        objRow.push(0);
      }
      objRow.push(0);
      tableau.unshift(objRow);

      // Solve using simplex iterations
      let iteration = 0;
      const maxIterations = 100;

      while (iteration < maxIterations) {
        // Find pivot column (most negative in objective row)
        let pivotCol = -1;
        let minValue = 0;
        for (let j = 0; j < tableau[0].length - 1; j++) {
          if (tableau[0][j] < minValue) {
            minValue = tableau[0][j];
            pivotCol = j;
          }
        }

        if (pivotCol === -1) break; // Optimal solution found

        // Find pivot row (minimum ratio test)
        let pivotRow = -1;
        let minRatio = Infinity;
        for (let i = 1; i < tableau.length; i++) {
          if (tableau[i][pivotCol] > 0) {
            const ratio = tableau[i][tableau[i].length - 1] / tableau[i][pivotCol];
            if (ratio < minRatio) {
              minRatio = ratio;
              pivotRow = i;
            }
          }
        }

        if (pivotRow === -1) {
          throw new Error('Unbounded solution');
        }

        // Perform pivot operation
        const pivotElement = tableau[pivotRow][pivotCol];
        for (let j = 0; j < tableau[pivotRow].length; j++) {
          tableau[pivotRow][j] /= pivotElement;
        }

        for (let i = 0; i < tableau.length; i++) {
          if (i !== pivotRow) {
            const factor = tableau[i][pivotCol];
            for (let j = 0; j < tableau[i].length; j++) {
              tableau[i][j] -= factor * tableau[pivotRow][j];
            }
          }
        }

        iteration++;
      }

      // Extract solution
      const solution = Array(numVars).fill(0);
      for (let j = 0; j < numVars; j++) {
        let isBasic = true;
        let basicRow = -1;
        for (let i = 1; i < tableau.length; i++) {
          if (Math.abs(tableau[i][j] - 1) < 1e-6) {
            if (basicRow === -1) {
              basicRow = i;
            } else {
              isBasic = false;
              break;
            }
          } else if (Math.abs(tableau[i][j]) > 1e-6) {
            isBasic = false;
            break;
          }
        }
        if (isBasic && basicRow !== -1) {
          solution[j] = tableau[basicRow][tableau[basicRow].length - 1];
        }
      }

      const optimalValue = isMaximization ? -tableau[0][tableau[0].length - 1] : tableau[0][tableau[0].length - 1];

      // Sensitivity Analysis
      const sensitivity = {
        shadowPrices: [],
        reducedCosts: [],
        rhsRanges: []
      };

      // Shadow prices (dual values)
      for (let i = 0; i < numConstraints; i++) {
        sensitivity.shadowPrices.push({
          constraint: i + 1,
          value: Math.abs(tableau[0][numVars + i]) < 1e-6 ? 0 : tableau[0][numVars + i]
        });
      }

      // Reduced costs
      for (let j = 0; j < numVars; j++) {
        sensitivity.reducedCosts.push({
          variable: j + 1,
          value: Math.abs(tableau[0][j]) < 1e-6 ? 0 : tableau[0][j]
        });
      }

      setResult({
        type: 'simplex',
        solution,
        optimalValue,
        iterations: iteration,
        sensitivity
      });
    } catch (err) {
      setError(err.message);
    }
  };

  // Hungarian Algorithm for Assignment Problem
  const solveAssignment = () => {
    try {
      setError(null);
      const { size, matrix } = assignmentData;
      
      // Create a copy of the cost matrix
      let costMatrix = matrix.map(row => [...row]);
      
      // Step 1: Row reduction
      for (let i = 0; i < size; i++) {
        const minVal = Math.min(...costMatrix[i]);
        for (let j = 0; j < size; j++) {
          costMatrix[i][j] -= minVal;
        }
      }
      
      // Step 2: Column reduction
      for (let j = 0; j < size; j++) {
        let minVal = Infinity;
        for (let i = 0; i < size; i++) {
          minVal = Math.min(minVal, costMatrix[i][j]);
        }
        for (let i = 0; i < size; i++) {
          costMatrix[i][j] -= minVal;
        }
      }
      
      let assignment = Array(size).fill(-1);
      let iterations = 0;
      const maxIterations = 100;
      
      while (iterations < maxIterations) {
        // Try to find optimal assignment
        let rowCovered = Array(size).fill(false);
        let colCovered = Array(size).fill(false);
        assignment = Array(size).fill(-1);
        
        // Find zeros and try to assign
        for (let i = 0; i < size; i++) {
          for (let j = 0; j < size; j++) {
            if (costMatrix[i][j] === 0 && !rowCovered[i] && !colCovered[j]) {
              assignment[i] = j;
              rowCovered[i] = true;
              colCovered[j] = true;
              break;
            }
          }
        }
        
        // Check if we have a complete assignment
        let assigned = assignment.filter(x => x !== -1).length;
        if (assigned === size) break;
        
        // Cover zeros
        rowCovered = Array(size).fill(false);
        colCovered = Array(size).fill(false);
        
        for (let i = 0; i < size; i++) {
          if (assignment[i] !== -1) {
            rowCovered[i] = true;
          }
        }
        
        for (let i = 0; i < size; i++) {
          if (!rowCovered[i]) {
            for (let j = 0; j < size; j++) {
              if (costMatrix[i][j] === 0) {
                colCovered[j] = true;
              }
            }
          }
        }
        
        // Find minimum uncovered value
        let minUncovered = Infinity;
        for (let i = 0; i < size; i++) {
          for (let j = 0; j < size; j++) {
            if (!rowCovered[i] && !colCovered[j]) {
              minUncovered = Math.min(minUncovered, costMatrix[i][j]);
            }
          }
        }
        
        // Update matrix
        for (let i = 0; i < size; i++) {
          for (let j = 0; j < size; j++) {
            if (!rowCovered[i] && !colCovered[j]) {
              costMatrix[i][j] -= minUncovered;
            }
            if (rowCovered[i] && colCovered[j]) {
              costMatrix[i][j] += minUncovered;
            }
          }
        }
        
        iterations++;
      }
      
      // Calculate total cost
      let totalCost = 0;
      for (let i = 0; i < size; i++) {
        if (assignment[i] !== -1) {
          totalCost += matrix[i][assignment[i]];
        }
      }
      
      setResult({
        type: 'assignment',
        assignment,
        totalCost,
        iterations
      });
    } catch (err) {
      setError(err.message);
    }
  };

  // Vogel's Approximation Method for Transportation Problem
  const solveTransportation = () => {
    try {
      setError(null);
      const { sources, destinations, supply, demand, costs } = transportationData;
      
      // Check if problem is balanced
      const totalSupply = supply.reduce((a, b) => a + b, 0);
      const totalDemand = demand.reduce((a, b) => a + b, 0);
      
      if (Math.abs(totalSupply - totalDemand) > 1e-6) {
        throw new Error('Problem is not balanced. Total supply must equal total demand.');
      }
      
      // Initialize allocation matrix
      let allocation = Array(sources).fill(null).map(() => Array(destinations).fill(0));
      let remainingSupply = [...supply];
      let remainingDemand = [...demand];
      
      // Vogel's Approximation Method
      while (remainingSupply.some(s => s > 0) && remainingDemand.some(d => d > 0)) {
        // Calculate penalties for rows
        let rowPenalties = [];
        for (let i = 0; i < sources; i++) {
          if (remainingSupply[i] > 0) {
            let availableCosts = [];
            for (let j = 0; j < destinations; j++) {
              if (remainingDemand[j] > 0) {
                availableCosts.push(costs[i][j]);
              }
            }
            availableCosts.sort((a, b) => a - b);
            const penalty = availableCosts.length > 1 ? availableCosts[1] - availableCosts[0] : availableCosts[0];
            rowPenalties.push({ index: i, penalty, type: 'row' });
          }
        }
        
        // Calculate penalties for columns
        let colPenalties = [];
        for (let j = 0; j < destinations; j++) {
          if (remainingDemand[j] > 0) {
            let availableCosts = [];
            for (let i = 0; i < sources; i++) {
              if (remainingSupply[i] > 0) {
                availableCosts.push(costs[i][j]);
              }
            }
            availableCosts.sort((a, b) => a - b);
            const penalty = availableCosts.length > 1 ? availableCosts[1] - availableCosts[0] : availableCosts[0];
            colPenalties.push({ index: j, penalty, type: 'col' });
          }
        }
        
        // Find maximum penalty
        let allPenalties = [...rowPenalties, ...colPenalties];
        allPenalties.sort((a, b) => b.penalty - a.penalty);
        
        if (allPenalties.length === 0) break;
        
        let maxPenalty = allPenalties[0];
        
        // Allocate based on maximum penalty
        let minCost = Infinity;
        let allocRow = -1, allocCol = -1;
        
        if (maxPenalty.type === 'row') {
          let i = maxPenalty.index;
          for (let j = 0; j < destinations; j++) {
            if (remainingDemand[j] > 0 && costs[i][j] < minCost) {
              minCost = costs[i][j];
              allocRow = i;
              allocCol = j;
            }
          }
        } else {
          let j = maxPenalty.index;
          for (let i = 0; i < sources; i++) {
            if (remainingSupply[i] > 0 && costs[i][j] < minCost) {
              minCost = costs[i][j];
              allocRow = i;
              allocCol = j;
            }
          }
        }
        
        if (allocRow !== -1 && allocCol !== -1) {
          const allocAmount = Math.min(remainingSupply[allocRow], remainingDemand[allocCol]);
          allocation[allocRow][allocCol] = allocAmount;
          remainingSupply[allocRow] -= allocAmount;
          remainingDemand[allocCol] -= allocAmount;
        }
      }
      
      // Calculate total cost
      let totalCost = 0;
      for (let i = 0; i < sources; i++) {
        for (let j = 0; j < destinations; j++) {
          totalCost += allocation[i][j] * costs[i][j];
        }
      }
      
      setResult({
        type: 'transportation',
        allocation,
        totalCost,
        method: 'Vogel\'s Approximation Method'
      });
    } catch (err) {
      setError(err.message);
    }
  };

  // Generate report
  const generateReport = () => {
    if (!result) return;
    
    let reportText = "OPERATIONS RESEARCH SOLVER - REPORT\n";
    reportText += "=" .repeat(50) + "\n\n";
    reportText += `Date: ${new Date().toLocaleString()}\n\n`;
    
    if (result.type === 'simplex') {
      reportText += "SIMPLEX METHOD RESULTS\n";
      reportText += "-".repeat(50) + "\n";
      reportText += `Optimal Value: ${result.optimalValue.toFixed(4)}\n`;
      reportText += `Iterations: ${result.iterations}\n\n`;
      reportText += "Decision Variables:\n";
      result.solution.forEach((val, idx) => {
        reportText += `  x${idx + 1} = ${val.toFixed(4)}\n`;
      });
      reportText += "\nSensitivity Analysis:\n";
      reportText += "Shadow Prices:\n";
      result.sensitivity.shadowPrices.forEach(sp => {
        reportText += `  Constraint ${sp.constraint}: ${sp.value.toFixed(4)}\n`;
      });
    } else if (result.type === 'assignment') {
      reportText += "ASSIGNMENT PROBLEM RESULTS\n";
      reportText += "-".repeat(50) + "\n";
      reportText += `Total Cost: ${result.totalCost}\n`;
      reportText += `Iterations: ${result.iterations}\n\n`;
      reportText += "Assignments:\n";
      result.assignment.forEach((task, worker) => {
        reportText += `  Worker ${worker + 1} → Task ${task + 1}\n`;
      });
    } else if (result.type === 'transportation') {
      reportText += "TRANSPORTATION PROBLEM RESULTS\n";
      reportText += "-".repeat(50) + "\n";
      reportText += `Total Cost: ${result.totalCost}\n`;
      reportText += `Method: ${result.method}\n\n`;
      reportText += "Allocations:\n";
      result.allocation.forEach((row, i) => {
        row.forEach((val, j) => {
          if (val > 0) {
            reportText += `  Source ${i + 1} → Destination ${j + 1}: ${val} units\n`;
          }
        });
      });
    }
    
    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `OR_Report_${result.type}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <div className="header">
        <h1>
          <Calculator style={{color: '#4a6bff'}} />
          Operations Research Solver System
        </h1>
        <p>Comprehensive solver for Simplex, Assignment, and Transportation problems</p>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <div className="tabs-header">
          <button
            onClick={() => setActiveTab('simplex')}
            className={`tab-button ${activeTab === 'simplex' ? 'active' : ''}`}
          >
            <Calculator size={20} />
            Simplex Method
          </button>
          <button
            onClick={() => setActiveTab('assignment')}
            className={`tab-button ${activeTab === 'assignment' ? 'active' : ''}`}
          >
            <Users size={20} />
            Assignment Problem
          </button>
          <button
            onClick={() => setActiveTab('transportation')}
            className={`tab-button ${activeTab === 'transportation' ? 'active' : ''}`}
          >
            <Truck size={20} />
            Transportation Problem
          </button>
        </div>

        {/* Content Area */}
        <div className="tab-content">
          {activeTab === 'simplex' && (
            <SimplexTab 
              data={simplexData} 
              setData={setSimplexData} 
              onSolve={solveSimplex}
            />
          )}
          {activeTab === 'assignment' && (
            <AssignmentTab 
              data={assignmentData} 
              setData={setAssignmentData} 
              onSolve={solveAssignment}
            />
          )}
          {activeTab === 'transportation' && (
            <TransportationTab 
              data={transportationData} 
              setData={setTransportationData} 
              onSolve={solveTransportation}
            />
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="alert alert-error">
          <AlertCircle style={{color: '#c00', marginTop: '2px'}} size={20} />
          <div>
            <h3 style={{fontWeight: '600', color: '#c00', margin: '0 0 4px 0'}}>Error</h3>
            <p style={{color: '#c00', margin: 0}}>{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="results-container">
          <div className="results-header">
            <h2>
              <CheckCircle style={{color: '#080'}} />
              Results
            </h2>
            <button
              onClick={generateReport}
              className="button button-primary"
              style={{width: 'auto'}}
            >
              <Download size={20} />
              Download Report
            </button>
          </div>
          <ResultsDisplay result={result} />
        </div>
      )}
    </div>
  );
};

// Simplex Tab Component
const SimplexTab = ({ data, setData, onSolve }) => {
  const updateObjective = (index, value) => {
    const newObjective = [...data.objective];
    newObjective[index] = parseFloat(value) || 0;
    setData({ ...data, objective: newObjective });
  };

  const updateConstraint = (row, col, value) => {
    const newConstraints = data.constraints.map(r => [...r]);
    newConstraints[row][col] = parseFloat(value) || 0;
    setData({ ...data, constraints: newConstraints });
  };

  const updateConstraintType = (index, type) => {
    const newTypes = [...data.constraintTypes];
    newTypes[index] = type;
    setData({ ...data, constraintTypes: newTypes });
  };

  const loadExample = () => {
    setData({
      numVars: 10,
      numConstraints: 10,
      objective: [5, 4, 3, 5, 6, 4, 3, 5, 4, 3],
      constraints: [
        [2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 100],
        [1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 80],
        [1, 1, 3, 1, 1, 2, 1, 1, 3, 1, 90],
        [2, 1, 1, 3, 1, 1, 2, 1, 1, 2, 120],
        [1, 2, 1, 1, 2, 1, 1, 3, 1, 1, 85],
        [1, 1, 2, 1, 1, 3, 1, 1, 2, 1, 95],
        [2, 1, 1, 2, 1, 1, 3, 1, 1, 2, 110],
        [1, 3, 1, 1, 2, 1, 1, 2, 1, 1, 75],
        [1, 1, 2, 1, 1, 2, 1, 1, 3, 1, 105],
        [2, 1, 1, 2, 1, 1, 2, 1, 1, 3, 115]
      ],
      constraintTypes: Array(10).fill('<='),
      isMaximization: true
    });
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
      <div className="flex justify-between items-center">
        <div>
          <label style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', fontWeight: '600', color: '#333'}}>
            <input
              type="checkbox"
              checked={data.isMaximization}
              onChange={(e) => setData({ ...data, isMaximization: e.target.checked })}
              style={{width: '20px', height: '20px'}}
            />
            Maximize (uncheck for Minimize)
          </label>
        </div>
        <button
          onClick={loadExample}
          className="button button-secondary"
          style={{width: 'auto'}}
        >
          Load Example
        </button>
      </div>

      <div>
        <h3 className="section-title">Objective Function Coefficients</h3>
        <div className="input-grid">
          {data.objective.map((val, idx) => (
            <div key={idx} className="input-group">
              <label className="input-label">x{idx + 1}</label>
              <input
                type="number"
                value={val}
                onChange={(e) => updateObjective(idx, e.target.value)}
                className="input-field"
              />
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="section-title">Constraints</h3>
        <div style={{overflowX: 'auto'}}>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                {Array(data.numVars).fill(0).map((_, idx) => (
                  <th key={idx}>x{idx + 1}</th>
                ))}
                <th>Type</th>
                <th>RHS</th>
              </tr>
            </thead>
            <tbody>
              {data.constraints.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  <td style={{fontWeight: '600', textAlign: 'center'}}>{rowIdx + 1}</td>
                  {row.slice(0, data.numVars).map((val, colIdx) => (
                    <td key={colIdx}>
                      <input
                        type="number"
                        value={val}
                        onChange={(e) => updateConstraint(rowIdx, colIdx, e.target.value)}
                        style={{width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'center'}}
                      />
                    </td>
                  ))}
                  <td>
                    <select
                      value={data.constraintTypes[rowIdx]}
                      onChange={(e) => updateConstraintType(rowIdx, e.target.value)}
                      style={{width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px'}}
                    >
                      <option value="<=">≤</option>
                      <option value=">=">≥</option>
                      <option value="=">=</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      value={row[data.numVars]}
                      onChange={(e) => updateConstraint(rowIdx, data.numVars, e.target.value)}
                      style={{width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'center'}}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <button
        onClick={onSolve}
        className="button button-primary"
      >
        Solve Simplex Problem
      </button>
    </div>
  );
};

// Assignment Tab Component
const AssignmentTab = ({ data, setData, onSolve }) => {
  const updateMatrix = (row, col, value) => {
    const newMatrix = data.matrix.map(r => [...r]);
    newMatrix[row][col] = parseFloat(value) || 0;
    setData({ ...data, matrix: newMatrix });
  };

  const loadExample = () => {
    const exampleMatrix = [
      [9, 2, 7, 8, 6, 5, 4, 3, 7, 8],
      [6, 4, 3, 7, 8, 9, 2, 5, 6, 4],
      [5, 8, 1, 8, 4, 7, 6, 9, 3, 2],
      [7, 6, 9, 2, 5, 3, 8, 4, 1, 7],
      [8, 3, 6, 4, 7, 2, 9, 1, 5, 6],
      [4, 7, 2, 5, 9, 6, 3, 8, 4, 1],
      [3, 5, 8, 6, 2, 4, 1, 7, 9, 5],
      [2, 9, 4, 1, 3, 8, 7, 6, 2, 3],
      [1, 1, 5, 3, 1, 1, 5, 2, 8, 9],
      [5, 4, 6, 9, 8, 7, 2, 3, 4, 6]
    ];
    setData({ ...data, matrix: exampleMatrix });
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
      <div className="flex justify-between items-center">
        <h3 className="section-title">Cost Matrix (Workers × Tasks)</h3>
        <button
          onClick={loadExample}
          className="button button-secondary"
          style={{width: 'auto'}}
        >
          Load Example
        </button>
      </div>

      <div style={{overflowX: 'auto'}}>
        <table className="data-table">
          <thead>
            <tr>
              <th>W\T</th>
              {Array(data.size).fill(0).map((_, idx) => (
                <th key={idx}>T{idx + 1}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.matrix.map((row, rowIdx) => (
              <tr key={rowIdx}>
                <td style={{fontWeight: '600', textAlign: 'center', background: '#f8f9fa'}}>W{rowIdx + 1}</td>
                {row.map((val, colIdx) => (
                  <td key={colIdx}>
                    <input
                      type="number"
                      value={val}
                      onChange={(e) => updateMatrix(rowIdx, colIdx, e.target.value)}
                      style={{width: '64px', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'center'}}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        onClick={onSolve}
        className="button button-primary"
      >
        Solve Assignment Problem
      </button>
    </div>
  );
};

// Transportation Tab Component
const TransportationTab = ({ data, setData, onSolve }) => {
  const updateSupply = (index, value) => {
    const newSupply = [...data.supply];
    newSupply[index] = parseFloat(value) || 0;
    setData({ ...data, supply: newSupply });
  };

  const updateDemand = (index, value) => {
    const newDemand = [...data.demand];
    newDemand[index] = parseFloat(value) || 0;
    setData({ ...data, demand: newDemand });
  };

  const updateCost = (row, col, value) => {
    const newCosts = data.costs.map(r => [...r]);
    newCosts[row][col] = parseFloat(value) || 0;
    setData({ ...data, costs: newCosts });
  };

  const loadExample = () => {
    setData({
      sources: 10,
      destinations: 10,
      supply: [50, 60, 70, 55, 65, 75, 50, 60, 70, 55],
      demand: [45, 55, 65, 50, 60, 70, 55, 65, 75, 50],
      costs: [
        [8, 6, 10, 9, 7, 5, 8, 6, 9, 7],
        [9, 12, 13, 7, 8, 6, 9, 11, 8, 10],
        [14, 9, 16, 5, 10, 12, 7, 9, 11, 8],
        [11, 8, 15, 10, 12, 9, 6, 8, 10, 9],
        [7, 9, 12, 8, 11, 10, 5, 7, 9, 8],
        [10, 11, 14, 6, 9, 8, 10, 12, 7, 9],
        [13, 10, 17, 9, 14, 11, 8, 10, 12, 7],
        [9, 7, 11, 10, 8, 12, 9, 6, 8, 11],
        [12, 8, 15, 11, 13, 10, 7, 9, 6, 10],
        [8, 10, 13, 7, 9, 11, 12, 8, 10, 6]
      ]
    });
  };

  const totalSupply = data.supply.reduce((a, b) => a + b, 0);
  const totalDemand = data.demand.reduce((a, b) => a + b, 0);
  const isBalanced = Math.abs(totalSupply - totalDemand) < 0.01;

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
      <div className="flex justify-between items-center">
        <h3 className="section-title">Transportation Problem Data</h3>
        <button
          onClick={loadExample}
          className="button button-secondary"
          style={{width: 'auto'}}
        >
          Load Example
        </button>
      </div>

      {/* Balance Check */}
      <div className={`alert ${isBalanced ? 'alert-success' : 'alert-warning'}`}>
        {isBalanced ? (
          <CheckCircle style={{color: '#080'}} size={20} />
        ) : (
          <AlertCircle style={{color: '#856404'}} size={20} />
        )}
        <span style={{fontWeight: '600'}}>
          Total Supply: {totalSupply} | Total Demand: {totalDemand}
          {isBalanced ? ' (Balanced ✓)' : ' (Unbalanced - Please adjust)'}
        </span>
      </div>

      {/* Supply and Demand */}
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px'}}>
        <div>
          <h4 style={{fontWeight: '600', color: '#333', marginBottom: '12px'}}>Supply (Sources)</h4>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
            {data.supply.map((val, idx) => (
              <div key={idx} className="input-group">
                <label className="input-label">S{idx + 1}</label>
                <input
                  type="number"
                  value={val}
                  onChange={(e) => updateSupply(idx, e.target.value)}
                  className="input-field"
                />
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4 style={{fontWeight: '600', color: '#333', marginBottom: '12px'}}>Demand (Destinations)</h4>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
            {data.demand.map((val, idx) => (
              <div key={idx} className="input-group">
                <label className="input-label">D{idx + 1}</label>
                <input
                  type="number"
                  value={val}
                  onChange={(e) => updateDemand(idx, e.target.value)}
                  className="input-field"
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cost Matrix */}
      <div>
        <h4 style={{fontWeight: '600', color: '#333', marginBottom: '12px'}}>Cost Matrix (Sources × Destinations)</h4>
        <div style={{overflowX: 'auto'}}>
          <table className="data-table">
            <thead>
              <tr>
                <th>S\D</th>
                {Array(data.destinations).fill(0).map((_, idx) => (
                  <th key={idx}>D{idx + 1}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.costs.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  <td style={{fontWeight: '600', textAlign: 'center', background: '#f8f9fa'}}>S{rowIdx + 1}</td>
                  {row.map((val, colIdx) => (
                    <td key={colIdx}>
                      <input
                        type="number"
                        value={val}
                        onChange={(e) => updateCost(rowIdx, colIdx, e.target.value)}
                        style={{width: '64px', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'center'}}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <button
        onClick={onSolve}
        disabled={!isBalanced}
        className="button button-primary"
        style={{background: isBalanced ? '#4a6bff' : '#ccc', cursor: isBalanced ? 'pointer' : 'not-allowed'}}
      >
        Solve Transportation Problem
      </button>
    </div>
  );
};

// Results Display Component
const ResultsDisplay = ({ result }) => {
  if (result.type === 'simplex') {
    return (
      <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
          <div style={{background: '#f0f5ff', padding: '16px', borderRadius: '8px'}}>
            <p style={{fontSize: '14px', color: '#666', margin: '0 0 4px 0'}}>Optimal Value</p>
            <p style={{fontSize: '24px', fontWeight: 'bold', color: '#4a6bff', margin: 0}}>{result.optimalValue.toFixed(4)}</p>
          </div>
          <div style={{background: '#f0fff5', padding: '16px', borderRadius: '8px'}}>
            <p style={{fontSize: '14px', color: '#666', margin: '0 0 4px 0'}}>Iterations</p>
            <p style={{fontSize: '24px', fontWeight: 'bold', color: '#080', margin: 0}}>{result.iterations}</p>
          </div>
        </div>

        <div>
          <h3 style={{fontWeight: '600', color: '#333', marginBottom: '8px'}}>Decision Variables</h3>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px'}}>
            {result.solution.map((val, idx) => (
              <div key={idx} style={{background: '#f8f9fa', padding: '12px', borderRadius: '6px'}}>
                <span style={{fontSize: '14px', color: '#666'}}>x{idx + 1}</span>
                <p style={{fontWeight: '600', margin: '4px 0 0 0'}}>{val.toFixed(4)}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 style={{fontWeight: '600', color: '#333', marginBottom: '8px'}}>Sensitivity Analysis</h3>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
            <div>
              <h4 style={{fontSize: '14px', fontWeight: '600', color: '#666', marginBottom: '8px'}}>Shadow Prices</h4>
              <div style={{display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '192px', overflowY: 'auto'}}>
                {result.sensitivity.shadowPrices.map((sp, idx) => (
                  <div key={idx} style={{display: 'flex', justifyContent: 'space-between', background: '#f8f9fa', padding: '8px', borderRadius: '4px'}}>
                    <span style={{fontSize: '14px'}}>Constraint {sp.constraint}</span>
                    <span style={{fontWeight: '600'}}>{sp.value.toFixed(4)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 style={{fontSize: '14px', fontWeight: '600', color: '#666', marginBottom: '8px'}}>Reduced Costs</h4>
              <div style={{display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '192px', overflowY: 'auto'}}>
                {result.sensitivity.reducedCosts.map((rc, idx) => (
                  <div key={idx} style={{display: 'flex', justifyContent: 'space-between', background: '#f8f9fa', padding: '8px', borderRadius: '4px'}}>
                    <span style={{fontSize: '14px'}}>Variable {rc.variable}</span>
                    <span style={{fontWeight: '600'}}>{rc.value.toFixed(4)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (result.type === 'assignment') {
    return (
      <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
          <div style={{background: '#f0f5ff', padding: '16px', borderRadius: '8px'}}>
            <p style={{fontSize: '14px', color: '#666', margin: '0 0 4px 0'}}>Total Cost</p>
            <p style={{fontSize: '24px', fontWeight: 'bold', color: '#4a6bff', margin: 0}}>{result.totalCost}</p>
          </div>
          <div style={{background: '#f0fff5', padding: '16px', borderRadius: '8px'}}>
            <p style={{fontSize: '14px', color: '#666', margin: '0 0 4px 0'}}>Iterations</p>
            <p style={{fontSize: '24px', fontWeight: 'bold', color: '#080', margin: 0}}>{result.iterations}</p>
          </div>
        </div>

        <div>
          <h3 style={{fontWeight: '600', color: '#333', marginBottom: '8px'}}>Optimal Assignment</h3>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'}}>
            {result.assignment.map((task, worker) => (
              <div key={worker} style={{background: '#f8f9fa', padding: '12px', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <span style={{fontSize: '14px'}}>Worker {worker + 1}</span>
                <span style={{fontWeight: '600', color: '#4a6bff'}}>→ Task {task + 1}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (result.type === 'transportation') {
    return (
      <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
          <div style={{background: '#f0f5ff', padding: '16px', borderRadius: '8px'}}>
            <p style={{fontSize: '14px', color: '#666', margin: '0 0 4px 0'}}>Total Cost</p>
            <p style={{fontSize: '24px', fontWeight: 'bold', color: '#4a6bff', margin: 0}}>{result.totalCost.toFixed(2)}</p>
          </div>
          <div style={{background: '#f0fff5', padding: '16px', borderRadius: '8px'}}>
            <p style={{fontSize: '14px', color: '#666', margin: '0 0 4px 0'}}>Method</p>
            <p style={{fontSize: '18px', fontWeight: 'bold', color: '#080', margin: 0}}>{result.method}</p>
          </div>
        </div>

        <div>
          <h3 style={{fontWeight: '600', color: '#333', marginBottom: '8px'}}>Allocation Matrix</h3>
          <div style={{overflowX: 'auto'}}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>S\D</th>
                  {result.allocation[0].map((_, idx) => (
                    <th key={idx}>D{idx + 1}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.allocation.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    <td style={{fontWeight: '600', textAlign: 'center', background: '#f8f9fa'}}>S{rowIdx + 1}</td>
                    {row.map((val, colIdx) => (
                      <td 
                        key={colIdx} 
                        style={{
                          textAlign: 'center',
                          background: val > 0 ? '#f0fff5' : 'transparent',
                          fontWeight: val > 0 ? '600' : 'normal'
                        }}
                      >
                        {val > 0 ? val.toFixed(2) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h3 style={{fontWeight: '600', color: '#333', marginBottom: '8px'}}>Non-Zero Allocations</h3>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'}}>
            {result.allocation.flatMap((row, i) =>
              row.map((val, j) => val > 0 ? { source: i + 1, dest: j + 1, amount: val } : null)
            ).filter(Boolean).map((alloc, idx) => (
              <div key={idx} style={{background: '#f8f9fa', padding: '12px', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <span style={{fontSize: '14px'}}>S{alloc.source} → D{alloc.dest}</span>
                <span style={{fontWeight: '600', color: '#4a6bff'}}>{alloc.amount.toFixed(2)} units</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ORSolverSystem;