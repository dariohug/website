---
title: "Neural Networks in Four Tiers"
---

I wanted to know how a neural network is *actually* written, so I wrote the same
one four times: from "the framework does it for me" down to "I do it myself".
The task never changes. Every notebook reads a 28x28 MNIST image and predicts
which digit it shows, always with the same 784 → 128 → 64 → 10 perceptron,
109,386 parameters, dropout between the hidden layers. Only the way of writing
it changes, which is what makes the comparison fair.

Code on GitHub: [dariohug/neural_net](https://github.com/dariohug/neural_net).

## The four levels

**1 · TensorFlow / Keras.** Turned out to be really easy. List the layers, call
`compile()`, call `fit()`, and Keras writes the training loop for you.

**2 · PyTorch.** Same network, but the training loop is mine: forward pass,
loss, backpropagate, update. I also handle the device and switch the model
between train and eval mode.

**3 · numpy.** No framework. The forward pass is matrix multiplications written
out, and every gradient is derived by hand. Adam turns out to be fifteen lines
of my own code.

**4 · My own autograd.** I build the tape PyTorch calls autograd, then run the
same network on top of it. Level 3's hand-derived backward pass disappears
completely.

All four land at roughly 97.5 % test accuracy after 5 epochs. The number does
not move, because the architecture never moved. Next up: convolutions, which is
where it finally should.

## Best of

**The whole backward pass, by hand (level 3).** Three lines per layer, repeated.
For `y = h @ W + b` the rules are `dW = h.T @ dy`, `db = sum(dy)` and
`dh = dy @ W.T`; everything else is walking those backwards through ReLU and
dropout.

```python
def backward(self, dlogits):
    x, z1, mask, d1, z2, a2 = self.cache
    W2, W3 = self.params["W2"], self.params["W3"]
    g = {}

    g["W3"] = a2.T @ dlogits          # layer 3
    g["b3"] = dlogits.sum(axis=0)
    da2 = dlogits @ W3.T

    dz2 = da2 * (z2 > 0)              # back through ReLU
    g["W2"] = d1.T @ dz2              # layer 2
    g["b2"] = dz2.sum(axis=0)
    dd1 = dz2 @ W2.T

    da1 = dd1 * mask if mask is not None else dd1   # back through dropout
    dz1 = da1 * (z1 > 0)
    g["W1"] = x.T @ dz1               # layer 1
    g["b1"] = dz1.sum(axis=0)
    return g
```

**A wrong derivative never crashes.** It just trains a little worse and stays
hidden, so the only honest check is a numeric one: nudge a single weight by
*h*, measure how the loss actually moves, and compare that to what the analytic
gradient claims. Picking a weight whose gradient is zero would pass trivially,
so the check only ever samples a live one.

```python
numeric  = (loss_plus - loss_minus) / (2 * h)   # central difference
analytic = grads[name][i]
rel = abs(numeric - analytic) / max(1e-12, abs(numeric) + abs(analytic))
```

Relative errors come out around 1e-8. That is the moment level 3 becomes
trustworthy.

**Autograd is smaller than it sounds (level 4).** A tensor remembers which
operation produced it and how to push a gradient back, so the forward pass
records a graph as a side effect. Five operations are enough for the whole
network:

```python
def matmul(a, b):
    out = Tensor(a.data @ b.data, _prev=(a, b))
    def _backward():
        # the two rules I wrote out by hand three times in level 3
        a.grad += out.grad @ b.data.T
        b.grad += a.data.T @ out.grad
    out._backward = _backward
    return out

def relu(a):
    out = Tensor(np.maximum(a.data, 0.0), _prev=(a,))
    def _backward():
        a.grad += out.grad * (a.data > 0)   # blocked where the input was negative
    out._backward = _backward
    return out
```

`backward()` then topologically sorts the recorded graph and walks it in
reverse, calling each of those closures once. Gradients *accumulate* with `+=`,
because a tensor used twice receives a contribution from each use, and that is
also why `zero_grad()` exists. Four levels in, that quirk finally made sense.

**Dropout for free.** Once multiplication carries its own gradient, dropout is
just a multiplication by a scaled mask. No backward code at all:

```python
mask = (rng.random(x.data.shape) < keep) / keep
x = x * Tensor(mask)
```
