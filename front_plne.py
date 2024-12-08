import streamlit as st
import gurobipy as gp
# print program started
print("#"*10, "Program Started", "#"*10)
# Global Variables
m = gp.Model()
# Title
st.title("Magic PLNE Gurobi Optimizer")

# Number of Variables
st.header("Number of Variables:")
num_vars = st.number_input("Enter the number of variables:", value=3, step=1)
## Setting Gurobi Variables
variables = []
for i in range(num_vars):
   variables.append(m.addVar(vtype='I', name=f"x{i+1}"))

# Objective Function
st.header("Objective Function:")
cols = st.columns(num_vars+1)

# Select objective (Max or Min) selectbox
objective = cols[0].selectbox("Objective:", ["Max", "Min"])

objective_function_text = ""
objective_coefficients = []
for i in range(num_vars):
   value = cols[i+1].number_input(f"x {i+1}", value=1, )
   if value == "1":
      objective_function_text += f" + x_{i+1}"
   elif value == "-1":
      objective_function_text += f" -x_{i+1}"
   elif value == "0":
      continue
   elif int(value) < 0:
      objective_function_text += f" {value}x_{i+1}"
   else:
      objective_function_text += f" + {value}x_{i+1}"
   objective_coefficients.append(int(value))

# Set objective function in Gurobi
if objective == "Max":
   m.setObjective(sum([variables[i] * objective_coefficients[i] for i in range(num_vars)]), gp.GRB.MAXIMIZE)
else:
   m.setObjective(sum([variables[i] * objective_coefficients[i] for i in range(num_vars)]), gp.GRB.MINIMIZE)


#objective_function_text = objective_function_text[:-2]

if objective_function_text[1] == "+":
   objective_function_text = objective_function_text[2:]

# Constraints
st.header("Constraints:")
num_constraints = st.number_input("Enter the number of constraints:", value=2, step=1)
constraints = []
for i in range(num_constraints):
   cols = st.columns(num_vars+2)
   constraint_text = ""
   constraint_coefficients = []
   for j in range(num_vars):
      print("#"*100)
      value = cols[j].number_input(f"x {j+1}", value=0, key=f"constraint_{i}{j+1}")
      print("Value is", value)
      if value == "1":
         constraint_text += f" + x_{j+1}"
      elif value == "-1":
         constraint_text += f" -x_{j+1}"
      elif value == "0":
         pass
      elif int(value) < 0:
         constraint_text += f" {value}x_{j+1}"
      else:
         constraint_text += f" + {value}x_{j+1}"
      constraint_coefficients.append(int(value))
      print("##################################", len(constraint_coefficients), num_vars, value)
   
   
   # <= or >=
   value = cols[num_vars].selectbox("", ["≤", "≥"], key=f"constraint_{i}sign")
   constraint_text += "\\le " if value == "≤" else "\\ge "
   # RHS
   rhs = cols[num_vars+1].number_input("", value=1, key=f"constraint_{i}rhs")
   constraint_text += str(rhs)
   if constraint_text[1] == "+":
      constraint_text = constraint_text[2:]
   constraints.append(constraint_text)
   # Add constraint to Gurobi
   if value == "≤":
      m.addConstr(sum([variables[j] * constraint_coefficients[j] for j in range(num_vars)]) <= int(rhs))
   else:
      m.addConstr(sum([variables[j] * constraint_coefficients[j] for j in range(num_vars)]) >= int(rhs))


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
