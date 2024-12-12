import streamlit as st
import gurobipy as gp
from gurobipy import Model, GRB
import matplotlib.pyplot as plt
import math

# -------------------------------
# Title and Description
# -------------------------------
st.title("Resourcify-- Resource Optimization Solver")


# -------------------------------
# Number of Variables
# -------------------------------
num_vars = st.number_input("Enter the number of variables:", value=3, step=1, min_value=2, max_value=10)

# -------------------------------
# Variable Names and Costs
# -------------------------------
st.subheader("define  variables and their costs ")
variable_names = []
variable_costs = []

for i in range(num_vars):
    col1, col2 = st.columns(2)
    with col1:
        variable_name = st.text_input(f" variable Name {i+1}:", value=f"Variable {i+1}")
        variable_names.append(variable_name)
    with col2:
        x = st.number_input(f"cost  for {variable_name}:", value=float(i), step=0.5, key=f"x_{i}")
        variable_costs.append((x))

# -------------------------------
# Number of constraints
# -------------------------------
num_cons = st.number_input("Enter the number of constraints:", value=1, step=1, min_value=1, max_value=5)
# -------------------------------
# Constraints names, coefficients, and limits
# -------------------------------
st.subheader("Define Constraints and Their Limits")  # (rhs)
constraint_names = []
constraints_coefs = []
constraints_limits = []

for i in range(num_cons):
    st.write(f"**Constraint {i + 1}**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        constraint_name = st.text_input(f"Constraint Name {i + 1}:", value=f"Constraint {i + 1}")
        constraint_names.append(constraint_name)
    
    coefs = []
    for j in range(num_vars):
        coef = st.number_input(f"Coefficient for {variable_names[j]} {j + 1} in {constraint_name}:", 
                               value=float(1.0), step=0.5, key=f"coef_{i}_{j}")
        coefs.append(coef)
    constraints_coefs.append(coefs)

    # Get the limit (RHS) for the constraint
    with col3:
        limit = st.number_input(f"Limit for {constraint_name}:", value=float(i + 10), step=0.5, key=f"limit_{i}")
        constraints_limits.append(limit)


# -------------------------------
# Mathematical Formulation
# -------------------------------
st.subheader("Mathematical Formulation ")
st.latex(r"""
\text{Minimiser: } \sum_{i } c_{i} \cdot x_{i}
""")
st.latex(r"\text{with }c_i \text{ represents the cost of each variable } x_i")
st.write("Subject to:")
for i in range(num_cons):
    c = constraint_names[i][0]
    limit = constraints_limits[i]
    st.latex(f"\\sum_{{i}} {c}{{i}} \\cdot x_{{i}} \\geq {limit}")
# Add non-null constraints
st.write("And:")
for j in range(num_vars):
    st.latex(f"x_{{{j+1}}} > 0")


# -------------------------------
# Solve the Model
# -------------------------------
# Initialize the model

model = Model("Resource Optimization")

# Add decision variables
x = model.addVars(num_vars, vtype=GRB.CONTINUOUS, name="x")

# Set the objective function
model.setObjective(
    gp.quicksum(variable_costs[i] * x[i] for i in range(num_vars)),
    GRB.MINIMIZE
)
# Add constraints
for i in range(num_cons):
    model.addConstr(
        gp.quicksum(constraints_coefs[i][j] * x[j] for j in range(num_vars)) >= constraints_limits[i],
        name=f"Constraint_{i+1}"
    )

# Ensure no variable is null
for j in range(num_vars):
    model.addConstr(
        x[j] >= 1e-2,  # No conversion needed
        name=f"NonNullConstraint_var{j+1}"
    )



# Solve the model
model.optimize()
print(model.display())

if st.button("Solve Problem"):
    # Check the status and display results
    if model.status == GRB.OPTIMAL:
        st.success("Optimal Solution Found!")
        st.write(f"Objective Value: {model.objVal:.2f}")
        solution = [x[i].x for i in range(num_vars)]
        st.write("Solution:")
        for i, value in enumerate(solution):
            st.write(f"{variable_names[i]}: {value:.2f}")

        
    else:
        st.error("No Optimal Solution Found!")