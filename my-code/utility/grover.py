from utility.util import n_control_not

class Grover:
    def __init__(self):
        pass

    @staticmethod
    def inv_around_mean(circuit, qs, anc):
        n = len(qs)
        for i in range(n):
            circuit.h(qs[i])
        for i in range(n):
            circuit.x(qs[i])
        circuit.h(qs[0])
        n_control_not(circuit, [qs[i] for i in range(1, n)], qs[0], anc)
        circuit.h(qs[0])
        for i in range(n):
            circuit.x(qs[i])
        for i in range(n):
            circuit.h(qs[i])

    @staticmethod
    def init_grover(circuit, f_input, f_output):
        for j in range(len(f_input)):
            circuit.h(f_input[j])
        circuit.x(f_output)
        circuit.h(f_output)