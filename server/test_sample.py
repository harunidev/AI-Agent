def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    if a < 0 or b < 0:
        raise ValueError("Negative numbers not allowed")
    return a + b

def factorial(n):
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("Negative number")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
