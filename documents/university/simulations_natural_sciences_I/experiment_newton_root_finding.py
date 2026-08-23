
def func(x):
    return x ** 5 + x **2

def func_der(x):
    return 5 * x ** 4 + 2 * x

def lameroot(f, a, b, e):
    if f(a) > f(b): a,b = b,a 

    c, i = 0.5*(a + b), 0
    while abs(f(c)) > e and i < 1000:
        c = 0.5*(a + b)
        if f(c) > 0: b = c 
        else: a = c
        i+=1
    print(f"lameroot iterations: {i}")
    return c

def newtonroot(f, fder, x, e):
    i = 0
    while abs(f(x)) > e and i < 1000:
        assert abs(fder(x)) < 1e-12, f"derivative is to close to zero {fder(x)}"
        x = x - (f(x)/fder(x))
        i += 1
    print(f"newtons root iterations: {i}")
    return x

def main():
    res = lameroot(func, -5, 7, 1e-10)
    print(f"lame result: {res}\n")    
    
    res = newtonroot(func, func_der, 1, 1e-10)
    print(f"newton result: {res}")

if __name__ == "__main__":
    main()