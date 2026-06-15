"""A sample file to demonstrate the document viewer's code highlighting.

Replace this folder with your real course material.
"""


def fib(n: int) -> int:
    """Return the n-th Fibonacci number."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


if __name__ == "__main__":
    for i in range(10):
        print(i, fib(i))
