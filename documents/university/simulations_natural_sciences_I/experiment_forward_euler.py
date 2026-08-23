def function(x):
    return x ** 3 + 4

def derfunction(x):
    return 3 * x ** 2 

def forwardeuler(f, derf, eps, x):
    i = 0
    while abs(f(x)) > eps and i < 1000:
        x = x - f(x)/derf(x)
        i += 1
    print(f"iterations: {i}")
    return x

def main():
    print(forwardeuler(function, derfunction, 1e-5, 3))

if __name__ == "__main__":
    main()