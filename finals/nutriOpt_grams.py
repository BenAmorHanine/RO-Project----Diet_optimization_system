import streamlit as st
import gurobipy as gp
from gurobipy import Model, GRB

# print program started
print("#"*10, "Program Started", "#"*10)
# Global Variables
m = gp.Model()
# Title
st.title("NutriOpt: Adaptive Diet Optimization for Personalized Goals")

# Number of Variables
st.header("Number of Variables:")
num_vars = st.number_input("Enter the number of variables:", value=3, step=1)
## Setting Gurobi Variables
variables = []
for i in range(num_vars):
   variables.append(m.addVar(vtype='C', name=f"x{i+1}"))

# Objective Function
st.header("Objective Function:")

cols = st.columns(num_vars+1)

# Select objective (Max or Min) selectbox
#objective = cols[0].selectbox("Objective:", [ "Min"])
objective= cols[0].text_input("Objective:", "Min")


objective_function_text = ""
objective_coefficients = []
for i in range(num_vars):
    value = cols[i+1].text_input(f"Food {i+1}", value="1")
    try:
        value = float(value)
        if value > 0:
            objective_function_text += f"  {value}x_{i+1}"
            objective_coefficients.append(value)
        else:
            st.error(f"Coefficient for Food_{i+1} must be greater than 0.")  # Display error for invalid input
    except ValueError:
        st.error(f"Invalid input for Food_{i+1}. Please enter a valid number.")  # Handle non-numeric input


# Set objective function in Gurobi
m.setObjective(sum([variables[i] * objective_coefficients[i] for i in range(num_vars)]), gp.GRB.MINIMIZE)


#objective_function_text = objective_function_text[:-2]

if objective_function_text[1] == "+":
   objective_function_text = objective_function_text[2:]

constraints = []
num_constraints = st.number_input("Enter the number of constraint categories:", value=3, step=1)

for i in range(num_constraints):
    st.subheader(f"Constraint {i+1}")
    cols = st.columns(num_vars + 3)

    # Coefficients for the constraint
    constraint_text = ""
    constraint_coefficients = []
    for j in range(num_vars):
        coeff = cols[j].text_input(f"Food {j+1} Coefficient:", value="1", key=f"constraint_{i}_{j}")
        try:
            coeff = float(coeff)
        except ValueError:
            coeff = 0
        constraint_coefficients.append(coeff)
        constraint_text += f" + {coeff}x_{j+1}" if coeff > 0 else f" {coeff}x_{j+1}"

    # Select inequality type
    inequality = cols[num_vars].selectbox("Constraint Inequality:", ["≤", "≥", "="], key=f"constraint_{i}_ineq")
    constraint_text += f" {inequality} "

    # RHS of the constraint
    rhs = cols[num_vars + 1].text_input("Minimuun/Maximum required", value="1", key=f"constraint_{i}_rhs")
    try:
        rhs = float(rhs)
        constraint_text+= f"{rhs}"
    except ValueError:
        rhs = 0


    # Update Gurobi model with the constraint
    if inequality == "≤":
        m.addConstr(sum(variables[j] * constraint_coefficients[j] for j in range(num_vars)) <= rhs)
    elif inequality == "≥":
        m.addConstr(sum(variables[j] * constraint_coefficients[j] for j in range(num_vars)) >= rhs)
    elif inequality == "=":
        m.addConstr(sum(variables[j] * constraint_coefficients[j] for j in range(num_vars)) == rhs)

    constraints.append((constraint_text))

for j in range(num_vars):
    m.addConstr(
        variables[j] >= 1,  # No conversion needed
        name=f"NonNullConstraint_var{j+1}"
    )


st.subheader("Mathematical Formulation ")
st.latex(r"""
\text{Minimiser: } \sum_{i } c_{i} \cdot x_{i}
""")
st.latex(r"\text{with }c_i \text{ represents the cost of each food } x_i")
st.write("Subject to:")

for constraint_text in constraints:
    st.write(f"{constraint_text}")


# Solve button
if st.button("Solve"):
    m.setObjective(sum(variables), GRB.MINIMIZE)
    m.optimize()
    print(m.display())

    # Display results
    if m.status == GRB.OPTIMAL:
        st.subheader("Optimal Solution")
        for v in m.getVars():
            st.write(f"{v.varName}: {v.x}")
        st.write(f"Objective Value: {m.objVal}")
    else:
        st.write("No optimal solution found.")
