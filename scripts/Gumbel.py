import pyvinecopulib as pv
import numpy as np
import matplotlib.pyplot as plt

for theta in [1.5, 8.0, 20.0, 50.0]:
    cop = pv.Bicop(
        family=pv.BicopFamily.gumbel,
        parameters=np.array([[theta]])   # ← explicit np.array, shape (1,1)
    )
    samples = cop.simulate(n=500, seeds=[42])
    plt.scatter(samples[:, 0], samples[:, 1], s=5, alpha=0.5, label=f'θ={theta}')

plt.legend()
plt.xlabel('U')
plt.ylabel('V')
plt.title('Gumbel Copula Samples')
plt.show()