"""
Experiment 01 — Classical evaluation of Boolean functions

We consider Boolean functions f: {0,1} -> {0,1}.
Classically, to decide whether f is constant or balanced,
we must evaluate the function on more than one input.
"""

def f_constant_zero(x):
    return 0

def f_constant_one(x):
    return 1

def f_identity(x):
    return x

def f_not(x):
    return 1 - x

functions = {
    "constant_zero": f_constant_zero,
    "constant_one": f_constant_one,
    "identity": f_identity,
    "not": f_not,
}

def classify_classically(f):
    """
    Evaluates f(0) and f(1) and classifies the function.
    """
    values = [f(0), f(1)]

    if values[0] == values[1]:
        return "constant"
    else:
        return "balanced"

print("\n=== Classical Boolean Function Evaluation ===")

for name, f in functions.items():
    classification = classify_classically(f)
    print(f"Function '{name}':", classification)
