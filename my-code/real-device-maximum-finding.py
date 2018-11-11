from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, QISKitError, IBMQ
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

def do_experiment(n, st_val, iter, shots=1000, useRealDevice=False):
    # setup
    qs = QuantumRegister(n, 'qs')
    st = QuantumRegister(n, 'st')
    anc = QuantumRegister(2*n - 2, 'anc')
    out = QuantumRegister(1, 'out')
    cs = ClassicalRegister(n, 'cs')
    qc = QuantumCircuit(qs, st, anc, out, cs)

    Util.int_to_qubit(st_val, qc, st)
    qc.barrier()

    # prepare grover
    qc.h(qs)
    qc.x(out)
    qc.h(out)

    # do grover iteration
    for _ in range(iter):
        Util.greater_comp(qc, qs, st, anc, out[0])
        Grover.inv_around_mean(qc, qs, anc)

    qc.barrier()
    qc.measure(qs, cs)


    # visualization.plot_circuit(qc)
    device_name = 'ibmq_qasm_simulator'
    if useRealDevice:
        # device_name = 'ibmqx5'
        device_name = 'ibmq_16_melbourne'
    backend = IBMQ.get_backend(device_name)
    qobj = compile([qc], backend=backend, shots=shots)
    job = backend.run(qobj)
    jid = str(job.job_id())
    lapse = 0
    interval = 60
    while job.status().name != 'DONE':
        print('{} Status @ {} minutes'.format(jid, lapse))
        print(job.status())
        print('quere pos: {}'.format(job.queue_position()))
        time.sleep(interval)
        lapse += 1
    print(job.status())
    result = job.result()
    if useRealDevice:
        print(jid)
    print('total time: {} minutes'.format(lapse))
    print('================================================')

    result = job.result()
    counts = result.get_counts(qc)
    counts = {int(k[::-1],2) : v for k,v in counts.items()}
    if useRealDevice:
        Util.save_histogram(counts, 'pics/real-{}-bits'.format(n), '{}-{}-{}'.format(n, st_val, iter), fname='{}-{}-{}'.format(n, st_val, iter))
    else:
        Util.save_histogram(counts, 'pics/sim-{}-bits'.format(n), '{}-{}-{}'.format(n, st_val, iter), fname='{}-{}-{}'.format(n, st_val, iter))

# try_connect()
IBMQ.load_accounts()
n = 4
N = 2 ** n

max_iter = int(math.pi / 4 * math.sqrt(N) + 1)
total = N * (max_iter - 1)
current_exp = 0
for i in range(N):
    for iter in range(1, max_iter):
        current_exp += 1
        print('doing experiment {}/{}: {}-{}-{}'.format(current_exp, total, n, i, iter))
        # do_experiment(n, i, iter, shots=1000, useRealDevice=True)
        do_experiment(n, i, iter, shots=1000)

