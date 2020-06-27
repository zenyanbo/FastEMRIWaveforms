import numpy as np
from ylm import get_ylms

try:
    from FEW import FastEMRIWaveforms
except ImportError:
    pass

import argparse
import time

from nn import NN

import argparse

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("--time", "-t", default=0, type=int)
args = parser.parse_args()

check = NN(input_str="SE_n30_")

bias = []
weight = []
dim1 = []
dim2 = []
for i in range(check.num_layers):
    try:
        weight.append(check.layers[i].w.T.get().flatten())
        bias.append(check.layers[i].b.get())

    except AttributeError:
        weight.append(check.layers[i].w.T.flatten())
        bias.append(check.layers[i].b)
    dim1.append(check.layers[i].w.shape[0])
    dim2.append(check.layers[i].w.shape[1])


weight = np.concatenate(weight)
bias = np.concatenate(bias)
dim1 = np.asarray(dim1).astype(np.int32)
dim2 = np.asarray(dim2).astype(np.int32)

transform_matrix = np.asarray(
    np.genfromtxt("few/files/reduced_basis_n30.dat", dtype=np.complex128)
)
trans_dim1, trans_dim2 = transform_matrix.shape
transform_matrix = transform_matrix.T.flatten()
transform_factor = 1000.0

traj = np.genfromtxt("insp_p12.5_e0.7_tspacing_1M.dat")
input_len = len(traj)
print(input_len)

p = np.asarray(traj[:, 0], dtype=np.float64)
e = np.asarray(traj[:, 1], dtype=np.float64)
Phi_phi = np.asarray(traj[:, 2], dtype=np.float64)
Phi_r = np.asarray(traj[:, 3], dtype=np.float64)

l = np.zeros(3843, dtype=np.int32)
m = np.zeros(3843, dtype=np.int32)
n = np.zeros(3843, dtype=np.int32)

ind = 0
l_m_only = []

range_l = range(2, 10 + 1)
range_n = range(-30, 30 + 1)

num_n = 0
for _ in range_n:
    num_n += 1

for l_i in range_l:
    for m_i in range(0, l_i + 1):
        l_m_only.append([l_i, m_i])
        for n_i in range_n:
            l[ind] = l_i
            m[ind] = m_i
            n[ind] = n_i
            ind += 1

num_l_m = len(l_m_only)
ls, ms = np.asarray(l_m_only).T
buffer = np.zeros_like(ls, dtype=np.complex128)

theta = 1.5
phi = 2.5
"""
num = 100



st = time.perf_counter()
for _ in range(num):
    buffer = get_ylms(ls, ms, theta, phi, buffer)
et = time.perf_counter()
print((et - st) / num)

import pdb

pdb.set_trace()
"""
input_mat = np.concatenate([p, e]).astype(np.float64)

break_index = 97

delta_t = 10.0
max_init_len = 1000
input_len = 3155760

time_batch_size = 100
few_class = FastEMRIWaveforms(
    time_batch_size,
    check.num_layers,
    dim1,
    dim2,
    weight,
    bias,
    transform_matrix,
    trans_dim1,
    trans_dim2,
    transform_factor,
    break_index,
    l,
    m,
    n,
    num_l_m,
    num_n,
    input_len,
    max_init_len,
    delta_t,
    tol=1e-20,
)

theta = 1.6194924730440332
phi = 3.946698166040000011e00
M = 1.134944869275921956e06
mu = 2.948999954778721033e01


p0 = 13.0
e0 = 0.4
check = few_class.run_nn(M, mu, p0, e0, theta, phi)

if args.time:
    out_time = []
    for e0 in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        st = time.perf_counter()
        for _ in range(args.time):
            check = few_class.run_nn(M, mu, p0, e0, theta, phi)
        et = time.perf_counter()
        print(e0, len(check), "time per:", (et - st) / args.time, "\n")

        out_time.append([e0, (et - st) / args.time])
    np.save("few_timing_20.npy", np.asarray(out_time))

import pdb

pdb.set_trace()