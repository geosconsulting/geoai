import sympy
import numpy as np # Often used with sympy, though not strictly needed for these examples
import matplotlib.pyplot as plt # For optional plotting to visualize

# --- Setup ---
print("--- Setup ---")
# Define the symbolic variable 'x'
x = sympy.symbols('x')

# Define our example function: f(x) = x^2
f = x**2
print(f"Our function: f(x) = {f}")
print("-" * 20)

# --- 1. Limits: Approaching a value ---
print("\n--- 1. Limits ---")
# What value does f(x) approach as x approaches, say, 3?
point_to_approach = 3
limit_expr = sympy.limit(f, x, point_to_approach)

print(f"The limit of f(x) = {f} as x approaches {point_to_approach} is: {limit_expr}")

# Another example: A function undefined AT a point, but with a limit
g = (x**2 - 1) / (x - 1) # This simplifies to x+1, but is undefined at x=1
point_g = 1
limit_g = sympy.limit(g, x, point_g)
print(f"\nThe limit of g(x) = {g} as x approaches {point_g} is: {limit_g}")
# Explanation: Even though plugging x=1 into g gives 0/0, as x gets
# closer and closer to 1, the value of g gets closer and closer to 2.
# The limit tells us this target value.
print("-" * 20)


# --- 2. Derivatives: Instantaneous rate of change (slope) ---
print("\n--- 2. Derivatives ---")
# Let's find the derivative of our original function f(x) = x^2
# The derivative tells us the slope of the tangent line at any point x.
f_derivative = sympy.diff(f, x)

print(f"The derivative of f(x) = {f} with respect to x is: f'(x) = {f_derivative}")

# Now, let's use the derivative to find the slope AT a specific point,
# connecting back to the limit idea. Let's find the slope at x = 3.
slope_at_3 = f_derivative.subs(x, 3) # Substitute x=3 into the derivative expression
print(f"The slope of f(x) at x = 3 is: {slope_at_3}")

# Let's find the slope at x = -1
slope_at_neg_1 = f_derivative.subs(x, -1)
print(f"The slope of f(x) at x = -1 is: {slope_at_neg_1}")
# Explanation: The derivative f'(x) = 2x gives us a formula for the slope
# at *any* point x on the curve f(x) = x^2.
print("-" * 20)


# --- 3. Integration: Adding up small pieces (Area / Antiderivative) ---
print("\n--- 3. Integration ---")

# First, let's find the indefinite integral (antiderivative) of the derivative we found.
# This should give us back our original function (plus a constant 'C', which SymPy omits).
# We integrate f'(x) = 2x
antiderivative = sympy.integrate(f_derivative, x)

print(f"The indefinite integral (antiderivative) of f'(x) = {f_derivative} is: {antiderivative} (+ C)")
print(f"(Notice this is our original function {f}, ignoring the constant of integration)")

# Now, let's calculate a definite integral. This represents the area
# under the curve of the *original* function f(x) = x^2 between two points.
# Let's find the area under f(x) = x^2 from x = 0 to x = 3.
lower_bound = 0
upper_bound = 3
area_under_curve = sympy.integrate(f, (x, lower_bound, upper_bound)) # Note the tuple (x, lower, upper)

print(f"\nThe definite integral (area under the curve) of f(x) = {f} from x={lower_bound} to x={upper_bound} is: {area_under_curve}")

# Explanation:
# - The indefinite integral reverses the derivative. Integrating the rate of change (2x)
#   gives us back the original quantity function (x^2).
# - The definite integral sums up the values of the function over an interval.
#   Here, it calculates the exact area bounded by f(x)=x^2, the x-axis,
#   and the vertical lines x=0 and x=3.
print("-" * 20)

# --- Optional: Visualization ---
# Requires matplotlib installed: pip install matplotlib
try:
    # Convert sympy expressions to functions numpy can use for plotting
    f_lambdified = sympy.lambdify(x, f, 'numpy')
    f_deriv_lambdified = sympy.lambdify(x, f_derivative, 'numpy')

    # Generate x values
    x_vals = np.linspace(-2, 4, 400)
    y_vals = f_lambdified(x_vals)
    y_deriv_vals = f_deriv_lambdified(x_vals) # Slopes at each x

    plt.figure(figsize=(10, 6))

    # Plot the original function
    plt.plot(x_vals, y_vals, label=f'$f(x) = {sympy.latex(f)}$', color='blue')

    # Plot the derivative (slope function)
    plt.plot(x_vals, y_deriv_vals, label=f"$f'(x) = {sympy.latex(f_derivative)}$", color='red', linestyle='--')

    # Show the point x=3 and its tangent slope
    x_point = 3
    y_point = f_lambdified(x_point)
    slope_point = f_deriv_lambdified(x_point)
    plt.scatter(x_point, y_point, color='green', s=100, zorder=5, label=f'Point ({x_point}, {y_point})')
    # Draw tangent line segment at x=3
    tangent_x = np.linspace(x_point - 0.5, x_point + 0.5, 10)
    tangent_y = slope_point * (tangent_x - x_point) + y_point
    plt.plot(tangent_x, tangent_y, color='green', linestyle='-', linewidth=2, label=f'Tangent slope = {slope_point}')

    # Shade the area for the definite integral (0 to 3)
    x_fill = np.linspace(lower_bound, upper_bound, 100)
    y_fill = f_lambdified(x_fill)
    plt.fill_between(x_fill, y_fill, color='skyblue', alpha=0.4, label=f'Area = {area_under_curve}')

    plt.title("Visualizing f(x), f'(x), Tangent Slope, and Area")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    plt.grid(True, which='both', linestyle=':', linewidth=0.5)
    plt.legend()
    plt.ylim(-5, 20) # Adjust plot limits as needed
    plt.show()

except ImportError:
    print("\nMatplotlib not installed. Skipping visualization.")
except Exception as e:
    print(f"\nAn error occurred during plotting: {e}")