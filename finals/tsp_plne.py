import streamlit as st
import gurobipy as gp
from gurobipy import Model, GRB
import math
import matplotlib.pyplot as plt

# Title
st.title("TSP Optimization Problem Solver")

# Number of variables
st.header("Traveling Salesman Problem (TSP)")
num_vars = st.number_input("Enter the number of variables:", value=3, step=1, min_value=2, max_value=10)

# Get variable names and positions
st.subheader("variable Positions")
variable_names = []
variable_positions = []

for i in range(num_vars):
    col1, col2 = st.columns(2)
    with col1:
        variable_name = st.text_input(f"variable {i+1} Name:", value=f"variable {i+1}")
        variable_names.append(variable_name)
    with col2:
        x = st.number_input(f"{variable_name} X-coordinate:", value=float(i), step=0.5, key=f"x_{i}")
        y = st.number_input(f"{variable_name} Y-coordinate:", value=float(i), step=0.5,  key=f"y_{i}")
        variable_positions.append((x, y))

# Calculate Distance Matrix
st.subheader("Calculated Distance Matrix")
distances = {}
for i in range(num_vars):
    for j in range(num_vars):
        if i != j:
            dist = math.sqrt(
                (variable_positions[i][0] - variable_positions[j][0]) ** 2 +
                (variable_positions[i][1] - variable_positions[j][1]) ** 2
            )
            distances[(i, j)] = dist
            st.write(f"Distance from {variable_names[i]} to {variable_names[j]}: {dist:.2f}")

# Display the problem dynamically
st.header("Mathematical Formulation ")

# Objective Function
objective_function = "Minimize: \\sum_{i \\neq j} d_{ij} x_{ij}"
st.latex(objective_function)

# Constraints
st.write("Subject to:")
constraints_text = []
for i in range(num_vars):
    # Constraint for visiting each variable exactly once
    constraints_text.append(f"\\sum_{{j \\neq {i}}} x_{{i,j}} = 1")
    constraints_text.append(f"\\sum_{{j \\neq {i}}} x_{{j,i}} = 1")

# Display constraints dynamically
for constraint in constraints_text:
    st.latex(constraint)

st.latex("x_{ij} \\in \\{0, 1\\} \\quad \\forall i, j")

col1, col2, col3 = st.columns([1, 3, 1])  # Adjust widths to center the Solve button

# Function to plot positions and itinerary
def plot_itinerary(variable_positions, variable_names, itinerary):
    plt.figure(figsize=(8, 6))
    x_coords = [pos[0] for pos in variable_positions]
    y_coords = [pos[1] for pos in variable_positions]
    
    # Plot variables
    for i, (x, y) in enumerate(variable_positions):
        plt.scatter(x, y, color="blue", s=100, zorder=5)
        plt.text(x, y, f" {variable_names[i]}", fontsize=12, zorder=6)
    
    # Plot edges
    for i, j in itinerary:
        x_start, y_start = variable_positions[i]
        x_end, y_end = variable_positions[j]
        plt.plot([x_start, x_end], [y_start, y_end], "r-", lw=2, zorder=4)
    
    plt.title("TSP Itinerary", fontsize=16)
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.grid(True)
    st.pyplot(plt)

# Add the "Solve TSP" button in the middle column
with col2:
    if st.button("Solve TSP"):
        # Initialize the model
        m = Model("TSP")

        # Variables: x[i, j] = 1 if the salesman travels from variable i to variable j
        x = m.addVars(
            distances.keys(),
            vtype=GRB.BINARY,
            name="x"
        )

        # Set objective function
        m.setObjective(
            gp.quicksum(distances[(i, j)] * x[(i, j)] for i in range(num_vars) for j in range(num_vars) if i != j),
            GRB.MINIMIZE,
        )

        # Add constraints
        for i in range(num_vars):
            # Ensure each variable is left once
            m.addConstr(gp.quicksum(x[(i, j)] for j in range(num_vars) if i != j) == 1, name=f"leave_{i}")
            # Ensure each variable is entered once
            m.addConstr(gp.quicksum(x[(j, i)] for j in range(num_vars) if i != j) == 1, name=f"enter_{i}")
        
        # Add u variables for subtour elimination
        u = m.addVars(num_vars, vtype=GRB.CONTINUOUS, name="u")

        # Subtour elimination constraints
        for i in range(1, num_vars):  # Start from 1 since city 0 is the starting point
            for j in range(1, num_vars):
                if i != j:
                    m.addConstr(u[i] - u[j] + num_vars * x[(i, j)] <= num_vars - 1, name=f"subtour_{i}_{j}")


        # Solve the problem
        m.optimize()

        # Display results
        if m.status == GRB.OPTIMAL:
            st.success("Optimal Solution Found!")
            st.latex(f"\\text{{Objective Value: {m.objVal:.2f}}}")
            itinerary = []
            for i in range(num_vars):
                for j in range(num_vars):
                    if i != j and x[(i, j)].x > 0.5:
                        st.write(f"Travel from {variable_names[i]} to {variable_names[j]}")
                        itinerary.append((i, j))
            
            # Plot the solution
            plot_itinerary(variable_positions, variable_names, itinerary)
        else:
            st.error("No optimal solution found.")