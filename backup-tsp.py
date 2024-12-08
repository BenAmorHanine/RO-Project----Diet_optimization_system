import streamlit as st
import gurobipy as gp
from gurobipy import Model, GRB

# Title
st.title("TSP Optimization Problem Solver")

# Number of cities
st.header("Traveling Salesman Problem (TSP)")
num_vars = st.number_input("Enter the number of variables:", value=3, step=1, min_value=2, max_value=10)

# Get variable names
st.subheader("Variable Names")
city_names = []
for i in range(num_vars):
    city_name = st.text_input(f"Variable {i+1} Name:", value=f"X {i+1}")
    city_names.append(city_name)

# Distance matrix
st.subheader("Distance Matrix")
distances = {}
for i in range(num_vars):
    for j in range(num_vars):
        if i != j:
            distances[(i, j)] = st.number_input(
                f"Distance from {city_names[i]} to {city_names[j]}:",
                min_value=0.0,
                value=1.0,
                key=f"distance_{i}_{j}"
            )

# Display the problem dynamically
st.header("Mathematical Formulation ")

# Objective Function
objective_function = "Minimize: \\sum_{i \\neq j} d_{ij} x_{ij}"
st.latex(objective_function)

# Constraints
st.write("Subject to:")
constraints_text = []
for i in range(num_vars):
    # Constraint for visiting each city exactly once
    constraints_text.append(f"\\sum_{{j \\neq {i}}} x_{{i,j}} = 1")
    constraints_text.append(f"\\sum_{{j \\neq {i}}} x_{{j,i}} = 1")

# Display constraints dynamically
for constraint in constraints_text:
    st.latex(constraint)

st.latex("x_{ij} \\in \\{0, 1\\} \\quad \\forall i, j")

col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 1,1])  # Adjust widths as needed

# Add the "Solve TSP" button in the middle column
with col3:
# Solve Button
    if st.button("Solve TSP"):
    # Initialize the model
        m = Model("TSP")

        # Variables: x[i, j] = 1 if the salesman travels from city i to city j
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
            # Ensure each city is left once
            m.addConstr(gp.quicksum(x[(i, j)] for j in range(num_vars) if i != j) == 1, name=f"leave_{i}")
            # Ensure each city is entered once
            m.addConstr(gp.quicksum(x[(j, i)] for j in range(num_vars) if i != j) == 1, name=f"enter_{i}")

        # Solve the problem
        m.optimize()

        # Display results
        if m.status == GRB.OPTIMAL:
            st.success("Optimal Solution Found!")
            st.latex(f"\\text{{ Solution :}}")
            st.latex(f"Objective Value: {m.objVal}")
            for i in range(num_vars):
                for j in range(num_vars):
                    if i != j and x[(i, j)].x > 0.5:
                        st.latex(f"Travel from {city_names[i]} to {city_names[j]}")
        else:
            st.error("No optimal solution found.")