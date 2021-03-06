'''Example of PyMC - The Challenger Disaster
'''

# author: Thomas Haslwanter, date: Sept-2013

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import seaborn as sns
import os
import pymc as pm

def logistic(x, beta, alpha=0):
    return 1.0 / (1.0 + np.exp(np.dot(beta, x) + alpha))

sns.set_context('poster')

# --- Get and show the O-ring data ---
dataDir = r'C:\Users\p20529\Documents\Teaching\Master_FH\Stats\dist\Data\data_bayes'
inFile = os.path.join(dataDir, 'challenger_data.csv')

challenger_data = np.genfromtxt(inFile, skip_header=1, usecols=[1, 2],
                                missing_values='NA', delimiter=',')

# drop the NA values
challenger_data = challenger_data[~np.isnan(challenger_data[:, 1])]

# plot it, as a function of tempature (the first column)
print("Temp (F), O-Ring failure?")
print(challenger_data)

# First plot
plt.figure()
np.set_printoptions(precision=3, suppress=True)

plt.scatter(challenger_data[:, 0], challenger_data[:, 1], s=75, color="k",
            alpha=0.5)
plt.yticks([0, 1])
plt.ylabel("Damage Incident?")
plt.xlabel("Outside temperature (Fahrenheit)")
plt.title("Defects of the Space Shuttle O-Rings vs temperature")

curDir = os.path.abspath(os.path.curdir)
outFile = 'Challenger_ORings.png'
plt.tight_layout
plt.savefig(outFile, dpi=200)
print('Data written to {0}'.format(os.path.join(curDir, outFile)))
    
plt.show()

# --- Perform the MCMC-simulations ---
temperature = challenger_data[:, 0]
D = challenger_data[:, 1]  # defect or not?

# Define the prior distributions for alpha and beta
# 'value' sets the start parameter for the simulation
# The second parameter for the normal distributions is the "precision",
# i.e. the inverse of the standard deviation
beta = pm.Normal("beta", 0, 0.001, value=0)
alpha = pm.Normal("alpha", 0, 0.001, value=0)

# Define the model-function for the temperature
@pm.deterministic
def p(t=temperature, alpha=alpha, beta=beta):
    return 1.0 / (1. + np.exp(beta * t + alpha))

# connect the probabilities in `p` with our observations through a
# Bernoulli random variable.
observed = pm.Bernoulli("bernoulli_obs", p, value=D, observed=True)

# Combine the values to a model
model = pm.Model([observed, beta, alpha])

# Perform the simulations
map_ = pm.MAP(model)
map_.fit()
mcmc = pm.MCMC(model)
mcmc.sample(120000, 100000, 2)

# --- Show the resulting posterior distributions ---
alpha_samples = mcmc.trace('alpha')[:, None]  # best to make them 1d
beta_samples = mcmc.trace('beta')[:, None]

plt.figure(figsize=(12.5, 6))

# histogram of the samples:
plt.subplot(211)
plt.title(r"Posterior distributions of the variables $\alpha, \beta$")
plt.hist(beta_samples, histtype='stepfilled', bins=35, alpha=0.85,
         label=r"posterior of $\beta$", color="#7A68A6", normed=True)
plt.legend()

plt.subplot(212)
plt.hist(alpha_samples, histtype='stepfilled', bins=35, alpha=0.85,
         label=r"posterior of $\alpha$", color="#A60628", normed=True)
plt.legend()

curDir = os.path.abspath(os.path.curdir)
outFile = 'Challenger_Parameters.png'
plt.savefig(outFile, dpi=200)
print('Data written to {0}'.format(os.path.join(curDir, outFile)))

plt.show()

# --- Show the probability curve ----
# Draw the probability as a function of time
t = np.linspace(temperature.min() - 5, temperature.max() + 5, 50)[:, None]
p_t = logistic(t.T, beta_samples, alpha_samples)

mean_prob_t = p_t.mean(axis=0)

plt.figure(figsize=(12.5, 4))

plt.plot(t, mean_prob_t, lw=3, label="average posterior \nprobability \
of defect")
plt.plot(t, p_t[0, :], ls="--", label="realization from posterior")
plt.plot(t, p_t[-2, :], ls="--", label="realization from posterior")
plt.scatter(temperature, D, color="k", s=50, alpha=0.5)
plt.title("Posterior expected value of probability of defect; \
plus realizations")
plt.legend(loc="lower left")
plt.ylim(-0.1, 1.1)
plt.xlim(t.min(), t.max())
plt.ylabel("probability")
plt.xlabel("temperature")

curDir = os.path.abspath(os.path.curdir)
outFile = 'Challenger_Probability.png'
plt.savefig(outFile, dpi=200)
print('Data written to {0}'.format(os.path.join(curDir, outFile)))

plt.show()

# --- Draw CIs ---
from scipy.stats.mstats import mquantiles

# vectorized bottom and top 2.5% quantiles for "confidence interval"
qs = mquantiles(p_t, [0.025, 0.975], axis=0)
plt.fill_between(t[:, 0], *qs, alpha=0.7,
                 color="#7A68A6")

plt.plot(t[:, 0], qs[0], label="95% CI", color="#7A68A6", alpha=0.7)

plt.plot(t, mean_prob_t, lw=1, ls="--", color="k",
         label="average posterior \nprobability of defect")

plt.xlim(t.min(), t.max())
plt.ylim(-0.02, 1.02)
plt.legend(loc="lower left")
plt.scatter(temperature, D, color="k", s=50, alpha=0.5)
plt.xlabel("temp, $t$")

plt.ylabel("probability estimate")
plt.title("Posterior probability estimates given temp. $t$")

curDir = os.path.abspath(os.path.curdir)
outFile = 'Challenger_CIs.png'
plt.savefig(outFile, dpi=200)
print('Data written to {0}'.format(os.path.join(curDir, outFile)))

plt.show()