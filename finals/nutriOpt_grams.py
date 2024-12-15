import streamlit as st
import gurobipy as gp
from gurobipy import Model, GRB

# Gurobi Model
m = gp.Model()

# Title
st.title("NutriOpt: Adaptive Diet Optimization for Personalized Goals")

# Number of Foods
num_foods = st.number_input("Enter the number of foods:", value=3, step=1)

# Food Input Table
st.header("Food Details")
foods = []
for i in range(num_foods):
    cols = st.columns(4)
    with cols[0]:
        food_name = st.text_input(f"Food {i+1} Name:", value=f"Food{i+1}", key=f"food_name_{i}")
    with cols[1]:
        price = st.number_input(f"Price for {food_name}:", value=1.0, key=f"food_price_{i}")
        
    with cols[2]:
        min_qty = st.number_input(f"Minimum Quantity for {food_name}:", value=0.0, key=f"min_qty_{i}")
    with cols[3]:
        max_qty = st.number_input(f"Maximum Quantity for {food_name}:", value=10.0, key=f"max_qty_{i}")
    
    foods.append((food_name, price, min_qty, max_qty))

    #foods.append((food_name, price))

# Add Gurobi Variables for Foods
variables = [m.addVar(vtype='C', name=food[0]) for food in foods]

# Number of Constraints
num_constraints = st.number_input("Enter the number of constraints:", value=2, step=1)

# Constraint Input Table
st.header("Constraint Details")
constraints = []
for i in range(num_constraints):
    cols = st.columns(3)
    with cols[0]:
        constraint_name = st.text_input(f"Constraint {i+1} Name:", value=f"Constraint{i+1}", key=f"constraint_name_{i}")
    with cols[1]:
        constraint_type = st.selectbox(f"Type for {constraint_name}:", ["≤", "≥", "="], key=f"constraint_type_{i}")
    with cols[2]:
        limit = st.number_input(f"Limit for {constraint_name}:", value=100.0, key=f"constraint_limit_{i}")
    constraint_contributions = []
    for j, food in enumerate(foods):
        contrib = st.number_input(f"{food[0]} contribution to {constraint_name}:", value=1.0, key=f"contrib_{i}_{j}")
        constraint_contributions.append(contrib)
    constraints.append((constraint_name, constraint_type, limit, constraint_contributions))

# Set Objective Function
m.setObjective(sum(variables[j] * foods[j][1] for j in range(num_foods)), GRB.MINIMIZE)

# Add Constraints to Gurobi
for name, ctype, limit, contributions in constraints:
    expr = sum(variables[j] * contributions[j] for j in range(num_foods))
    if ctype == "≤":
        m.addConstr(expr <= limit, name=name)
    elif ctype == "≥":
        m.addConstr(expr >= limit, name=name)
    elif ctype == "=":
        m.addConstr(expr == limit, name=name)

# Add Bounds for Foods
for j, food in enumerate(foods):
    m.addConstr(variables[j] >= food[2], name=f"{food[0]}_min")
    m.addConstr(variables[j] <= food[3], name=f"{food[0]}_max")

# Display Model
st.subheader("Mathematical Formulation")
st.write("Objective: Minimize the total cost")
for name, ctype, limit, contributions in constraints:
    st.write(f"{name}: {' + '.join([f'{contrib} * {foods[j][0]}' for j, contrib in enumerate(contributions)])} {ctype} {limit}")

# Solve the Model
if st.button("Solve"):
    m.optimize()

    if m.status == GRB.OPTIMAL:
        st.subheader("Optimal Solution")
        for v in m.getVars():
            st.write(f"{v.varName}: {v.x:.2f}")
        st.write(f"Total Cost: {m.objVal:.2f}")
    else:
        st.write("No optimal solution found.")
