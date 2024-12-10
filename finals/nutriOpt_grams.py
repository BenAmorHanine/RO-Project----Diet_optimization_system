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
    value = cols[i+1].text_input(f"x {i+1}", value="1")
    try:
        value = float(value)
        if value > 0:
            objective_function_text += f"  {value}x_{i+1}"
            objective_coefficients.append(value)
        else:
            st.error(f"Coefficient for x_{i+1} must be greater than 0.")  # Display error for invalid input
    except ValueError:
        st.error(f"Invalid input for x_{i+1}. Please enter a valid number.")  # Handle non-numeric input


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
    inequality = cols[num_vars].selectbox("Inequality:", ["≤", "≥", "="], key=f"constraint_{i}_ineq")
    constraint_text += f" {inequality} "

    # RHS of the constraint
    rhs = cols[num_vars + 1].text_input("RHS:", value="1", key=f"constraint_{i}_rhs")
    try:
        rhs = float(rhs)
    except ValueError:
        rhs = 0
context = cols[num_vars + 2].selectbox("Constraint Context:", 
                                           ["Calorie Requirement", "Protein Requirement", 
                                            "Fat Requirement", "Vitamin Requirement", 
                                            "Food Availability"], 
                                           key=f"constraint_{i}_context")

 # Update Gurobi model with the constraint
if inequality == "≤":
    m.addConstr(sum(variables[j] * constraint_coefficients[j] for j in range(num_vars)) <= rhs, name=context)
elif inequality == "≥":
    m.addConstr(sum(variables[j] * constraint_coefficients[j] for j in range(num_vars)) >= rhs, name=context)
elif inequality == "=":
    m.addConstr(sum(variables[j] * constraint_coefficients[j] for j in range(num_vars)) == rhs, name=context)

constraints.append((constraint_text, context))

# Display constraints summary
st.header("Constraints Summary")
for constraint_text, context in constraints:
    st.write(f"Context: {context} - {constraint_text}")

# Solve button
if st.button("Solve"):
    m.setObjective(sum(variables), GRB.MINIMIZE)  # Set objective function (can be adjusted)
    m.optimize()

    # Display results
    if m.status == GRB.OPTIMAL:
        st.subheader("Optimal Solution")
        for v in m.getVars():
            st.write(f"{v.varName}: {v.x}")
        st.write(f"Objective Value: {m.objVal}")
    else:
        st.write("No optimal solution found.")




""""





# Solve the problem
m.optimize()


# Print the problem
st.header("The Problem:")
objective_function_text = objective.lower() + "imize \\\\" + objective_function_text
st.latex(f"{objective_function_text}")

st.latex("\\text{subject to} \\\\")
for i in range(num_constraints):
   st.latex(f"{constraints[i]}")

positive_str = ""
for i in range(num_vars):
   positive_str += f",x_{i}"
positive_str = positive_str[1:] + "\\ge 0"
st.latex(positive_str)


# Print the solution
st.header("The Solution:")
print("#"*4,m,"#"*4)
try:
   if(m.ObjVal):
      st.latex(f"\\text{{Optimal objective value: }} {m.ObjVal}")
      solution_text = ""
      for i in range(num_vars):
         solution_text += f"x_{i+1} = {variables[i].X}\\\\  "
      solution_text = solution_text[:-2]
      st.latex(f"\\text{{Solution values: }} \\\\ {solution_text}")
   else:
      st.latex("NO available solution")
except:
   st.latex(f"\\text{{No Solution }}")
"""