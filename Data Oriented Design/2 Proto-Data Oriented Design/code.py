import numpy as np
import time
import matplotlib.pyplot as plt

figure, axis = plt.subplots()

n = np.array([100 * i for i in range(1,20)])

# Flat layout, all "objects"
t1 = np.zeros_like(n, dtype=np.float32)
for j in range(n.size):
    for sample in range(100):
        x = []
        for i in range(n[j]):
            object_code = np.random.randint(0,2)
            x.append(object_code)
            x.append(np.random.random())
            if object_code == 1:
                x.append(np.random.random())

        start = time.time()
        while i < len(x):
            object_code = x[i]
            i += 1
            
            if object_code == 0:
                x[i] = 2 * x[i]
                i += 1
            else:
                x[i] = x[i] + x[i + 1]
                i += 2

        finish = time.time()
        t1[j] += 0.01 * (finish - start)
axis.plot(n,t1)

# Flat layout, all objects for real

class Object0:

    def __init__(self, a):
        self._a = a
    
    def update(self):
        self._a = self._a * 2

class Object1:

    def __init__(self, a, b):
        self._a = a
        self._b = b
    
    def update(self):
        self._a = self._a + self._b

t2 = np.zeros_like(n, dtype=np.float32)
for j in range(n.size):
    for sample in range(100):
        x = []
        for i in range(n[j]):
            object_code = np.random.randint(0,2)
            
            if object_code == 0:
                x.append(Object0(np.random.random()))
            else:
                x.append(Object1(np.random.random(), np.random.random()))

        start = time.time()
        for i in range(len(x)):
            x[i].update()

        finish = time.time()
        t2[j] += 0.01 * (finish - start)
axis.plot(n,t2)

# Flat layout, branchless
def update_0(x, i):
    x[i] = 2 * x[i]
    return i + 1

def update_1(x, i):
    x[i] = x[i] + x[i + 1]
    return i + 2

update = [update_0, update_1]

t3 = np.zeros_like(n, dtype=np.float32)
for j in range(n.size):
    for sample in range(100):
        x = []
        for i in range(n[j]):
            object_code = int(np.random.randint(0,2))
            x.append(object_code)
            x.append(np.random.random())
            if object_code == 1:
                x.append(np.random.random())

        start = time.time()
        i = 0
        while i < len(x):
            object_code = x[i]
            i += 1
            
            i = update[object_code](x, i)

        finish = time.time()
        t3[j] += 0.01 * (finish - start)
axis.plot(n,t3)

# Flat layout, two arrays
t4 = np.zeros_like(n, dtype=np.float32)
for j in range(n.size):
    for sample in range(100):
        x = []
        y = []
        for i in range(n[j]):
            object_code = int(np.random.randint(0,2))
            if object_code == 0:
                x.append(np.random.random())
            if object_code == 1:
                y.append(np.random.random())
                y.append(np.random.random())

        start = time.time()
        for i in range(len(x)):
            x[i] = 2 * x[i]
            
        for i in range(0, len(y), 2):
            y[i] = y[i] + y[i + 1]

        finish = time.time()
        t4[j] += 0.01 * (finish - start)
axis.plot(n,t4)

# Flat layout, three arrays
t5 = np.zeros_like(n, dtype=np.float32)
for j in range(n.size):
    for sample in range(100):
        x = []
        y = []
        dy = []
        for i in range(n[j]):
            object_code = int(np.random.randint(0,2))
            if object_code == 0:
                x.append(np.random.random())
            if object_code == 1:
                y.append(np.random.random())
                dy.append(np.random.random())

        start = time.time()
        for i in range(len(x)):
            x[i] = 2 * x[i]
            
        for i in range(0, len(y)):
            y[i] = y[i] + dy[i]

        finish = time.time()
        t5[j] += 0.01 * (finish - start)
axis.plot(n,t5)

figure.tight_layout()
axis.legend(["Naive", "OOP", "flat, branchless", "flat, two arrays", "flat, three arrays"])
plt.show()