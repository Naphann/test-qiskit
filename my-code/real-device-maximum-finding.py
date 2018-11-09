from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, QISKitError
from qiskit import available_backends, execute, register, get_backend, compile

from qiskit.tools import visualization
from qiskit.tools.visualization import circuit_drawer
import qiskit.extensions.simulator
import matplotlib

import utility as Util
from utility import Grover

# import other necessary stuff
import random
import math
import warnings

import sys, time, getpass


def try_connect():
    try:
        sys.path.append("../")
        import Qconfig
        qx_config = {
            "APItoken": Qconfig.APItoken,
            "url": Qconfig.config['url']}
        print('Qconfig loaded from %s.' % Qconfig.__file__)
    except:
        print('Qconfig.py not found in parent directory')

    # Connect to IBMQX system
    register(qx_config['APItoken'], qx_config['url'])
    print(available_backends())

# try_connect()
# setup
qs = QuantumRegister(2, 'qs')
st = QuantumRegister(2, 'st')
anc = QuantumRegister(5, 'anc')
out = QuantumRegister(1, 'out')
cs = ClassicalRegister(2, 'cs')
qc = QuantumCircuit(qs, st, anc, out, cs)

Util.int_to_qubit(0, qc, st)

# prepare grover
qc.h(qs)
qc.x(out)
qc.h(out)

# do grover iteration
Util.greater_comp(qc, qs, st, anc, out[0])
Grover.inv_around_mean(qc, qs, anc)

qc.measure(qs, cs)

# visualization.plot_circuit(qc)
device_name = 'local_qasm_simulator'
# device_name = 'ibmq_qasm_simulator'
my_backend = get_backend(device_name)
qobj = compile([qc], backend=my_backend, shots=1000)
job = my_backend.run(qobj)
lapse = 0
interval = 60
while not job.done:
    print('Status @ {} minutes'.format(lapse))
    print(job.status)
    time.sleep(interval)
    lapse += 1
print(job.status)
# print(job.id)

result = job.result()
counts = result.get_counts(qc)
counts = {int(k[::-1],2) : v for k,v in counts.items()}
Util.save_histogram(counts, 'pics/sim-2-bits', 'title')
