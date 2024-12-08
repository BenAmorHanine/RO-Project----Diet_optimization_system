import streamlit as st
# Global Variables

# Title
st.title("Magic Gurobi Optimizer")
# Number of Variables
st.header("Number of Variables:")
num_vars = st.number_input("Enter the number of variables:", value=3, step=1)
# Objective Function
st.header("Objective Function:")
cols = st.columns(num_vars+1)

# Select objective (Max or Min) selectbox
objective = cols[0].selectbox("Objective:", ["Max", "Min"])

objective_function_text = ""
for i in range(num_vars):
   value = cols[i+1].text_input(f"x {i+1}", value=1)
   if value == "1":
      objective_function_text += f" + x_{i+1}"
   elif value == "-1":
      objective_function_text += f" -x_{i+1}"
   elif value == "0":
      continue
   elif float(value) < 0:
      objective_function_text += f" {value}x_{i+1}"
   else:
      objective_function_text += f" + {value}x_{i+1}"



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
   for j in range(num_vars):
      value = cols[j].text_input(f"x {j+1}", value=1, key=f"constraint_{i}{j+1}")
      if value == "1":
         constraint_text += f" + x_{j+1}"
      elif value == "-1":
         constraint_text += f" -x_{j+1}"
      elif value == "0":
         continue
      elif float(value) < 0:
         constraint_text += f" {value}x_{j+1}"
      else:
         constraint_text += f" + {value}x_{j+1}"
   
   # <= or >=
   value = cols[num_vars].selectbox("", ["≤", "≥"], key=f"constraint_{i}sign")
   constraint_text += "\\le " if value == "≤" else "\\ge "
   # RHS
   constraint_text += cols[num_vars+1].text_input("", value=1, key=f"constraint_{i}rhs")
   if constraint_text[1] == "+":
      constraint_text = constraint_text[2:]
   constraints.append(constraint_text)


# Print the problem
objective_function_text = objective.lower() + "imize \\\\" + objective_function_text
st.latex(f"{objective_function_text}")

st.latex("\\text{subject to} \\\\")
for i in range(num_constraints):
   st.latex(f"{constraints[i]}")