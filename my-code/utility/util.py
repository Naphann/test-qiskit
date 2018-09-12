import math

class Util:

    def __init__(self):
        pass

    @staticmethod
    def n_control_not(circuit, q_array, target, ancillary_array, flip_array=None):
        # error checking
        if flip_array is not None and len(q_array) != len(flip_array):
            raise ValueError("q_array(len:{}) and flip_array(len:{}) must have the same length".format(len(q_array), len(flip_array)))
        if len(ancillary_array) < len(q_array) - 2:
            raise ValueError("ancillary array length is not enough ({}) for q_array ({})".format(len(ancillary_array), len(q_array)))
        if flip_array is None:
            flip_array = [1 for _ in range(len(q_array))]
        # todo handle wrong flip_array
        
        n = len(q_array)
        
        # put X-gate if flip
        for i in range(n):
            if flip_array[i] == -1:
                circuit.x(q_array[i])
            
        # special case for only 2 bits
        if n == 2:
            circuit.ccx(q_array[0], q_array[1], target)
        else:
            circuit.ccx(q_array[0], q_array[1], ancillary_array[0])
            for i in range(2, n-1):
                circuit.ccx(q_array[i], ancillary_array[i-2], ancillary_array[i-1])
            circuit.ccx(q_array[n-1], ancillary_array[n-3], target)
            for i in reversed(range(2, n-1)):
                circuit.ccx(q_array[i], ancillary_array[i-2], ancillary_array[i-1])
            circuit.ccx(q_array[0], q_array[1], ancillary_array[0])
        
        # clean up X-gate
        for i in range(n):
            if flip_array[i] == -1:
                circuit.x(q_array[i]) 

    @staticmethod
    def greater_comp(qc, a, b, anc, target):
        # check whether two register is the same length
        if len(a) != len(b):
            raise ValueError('two register to compare must have the same length: a is {}, b is {}'.format(len(a), len(b)))
        
        anc_len = len(anc)
        n = len(a)
        if anc_len < 2 * n - 2:
            raise ValueError('ancillary bit is not enough: anc_len is {}, need at least {} qbit'.format(anc_len, len(a) - 1))
        
        # compare the MSB
        n_control_not(qc, [a[0], b[0]], target, anc, [1, -1])
        
        for i in range(1, n):
            # all more significant bits must be equalg
            j = i-1
            qc.ccx(a[j], b[j], anc[j])
            qc.x(a[j])
            qc.x(b[j])
            qc.ccx(a[j], b[j], anc[j])
            
            n_control_not(qc, [anc[j] for j in range(i)] + [a[i], b[i]], target, [anc[k] for k in range(i, anc_len)],
                        [1] * (i+1) + [-1])
            
        for j in reversed(range(i)):
            qc.ccx(a[j], b[j], anc[j])
            qc.x(a[j])
            qc.x(b[j])
            qc.ccx(a[j], b[j], anc[j])

    @staticmethod
    def greater_equal_comp(qc, b, a, anc, target):
        # check whether two register is the same length
        if len(a) != len(b):
            raise ValueError('two register to compare must have the same length: a is {}, b is {}'.format(len(a), len(b)))
        
        anc_len = len(anc)
        n = len(a)
        if anc_len < 2 * n - 2:
            raise ValueError('ancillary bit is not enough: anc_len is {}, need at least {} qbit'.format(anc_len, len(a) - 1))
        
        # compare the MSB
        n_control_not(qc, [a[0], b[0]], target, anc, [1, -1])
        
        for i in range(1, n):
            # all more significant bits must be equal
            j = i-1
            qc.ccx(a[j], b[j], anc[j])
            qc.x(a[j])
            qc.x(b[j])
            qc.ccx(a[j], b[j], anc[j])
            
            n_control_not(qc, [anc[j] for j in range(i)] + [a[i], b[i]], target, [anc[k] for k in range(i, anc_len)],
                        [1] * (i+1) + [-1])
            
        for j in reversed(range(i)):
            qc.ccx(a[j], b[j], anc[j])
            qc.x(a[j])
            qc.x(b[j])
            qc.ccx(a[j], b[j], anc[j])

        qc.x(target)

    @staticmethod
    def int_to_qubit(n, circuit, qs):
        bits_required = int(math.log(max(n,1), 2) + 1)
        qs_len = len(qs)
        if qs_len < bits_required:
            raise ValueError('input n = {} requires {} bits but qs is only {} bits'.format(n, bits_required, qs_len))

        bstr = '{0:b}'.format(n)
        bstr = bstr.zfill(qs_len)
        for i in range(qs_len):
            if bstr[i] == '1':
                circuit.x(qs[i])

    