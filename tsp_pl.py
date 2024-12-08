import streamlit as st
import gurobipy as gp
from gurobipy import Model, GRB
import math
import matplotlib.pyplot as plt

# Title
st.title("TSP Optimization Problem Solver")

# Number of cities
st.header("Traveling Salesman Problem (TSP)")
num_vars = st.number_input("Enter the number of cities:", value=3, step=1, min_value=2, max_value=10)

# Get city names and positions
st.subheader("City Positions")
city_names = []
city_positions = []

for i in range(num_vars):
    col1, col2 = st.columns(2)
    with col1:
        city_name = st.text_input(f"City {i+1} Name:", value=f"City {i+1}")
        city_names.append(city_name)
    with col2:
        x = st.number_input(f"{city_name} X-coordinate:", value=float(i), key=f"x_{i}")
        y = st.number_input(f"{city_name} Y-coordinate:", value=float(i), key=f"y_{i}")
        city_positions.append((x, y))

# Calculate Distance Matrix
st.subheader("Calculated Distance Matrix")
distances = {}
for i in range(num_vars):
    for j in range(num_vars):
        if i != j:
            dist = math.sqrt(
                (city_positions[i][0] - city_positions[j][0]) ** 2 +
                (city_positions[i][1] - city_positions[j][1]) ** 2
            )
            distances[(i, j)] = dist
            st.write(f"Distance from {city_names[i]} to {city_names[j]}: {dist:.2f}")

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

col1, col2, col3 = st.columns([1, 3, 1])  # Adjust widths to center the Solve button

# Function to plot positions and itinerary
def plot_itinerary(city_positions, city_names, itinerary):
    plt.figure(figsize=(8, 6))
    x_coords = [pos[0] for pos in city_positions]
    y_coords = [pos[1] for pos in city_positions]
    
    # Plot cities
    for i, (x, y) in enumerate(city_positions):
        plt.scatter(x, y, color="blue", s=100, zorder=5)
        plt.text(x, y, f" {city_names[i]}", fontsize=12, zorder=6)
    
    # Plot edges
    for i, j in itinerary:
        x_start, y_start = city_positions[i]
        x_end, y_end = city_positions[j]
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
            st.latex(f"\\text{{Objective Value: {m.objVal:.2f}}}")
            itinerary = []
            for i in range(num_vars):
                for j in range(num_vars):
                    if i != j and x[(i, j)].x > 0.5:
                        st.write(f"Travel from {city_names[i]} to {city_names[j]}")
                        itinerary.append((i, j))
            
            # Plot the solution
            plot_itinerary(city_positions, city_names, itinerary)
        else:
            st.error("No optimal solution found.")
