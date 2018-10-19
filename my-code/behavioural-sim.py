#%%
import matplotlib.pyplot as plt
import random
import math

import itertools
import bisect
import pprint

import utility as Util

# %matplotlib inline

#%%
class State:
    
    def __init__(self, n):
        """
        n: number of qubits
        """
        self.len = n
        self.state = [([0] * n, 1)]
        
    def measure(self, a, b):
        n = self.len
        if a > b or a < 0 or b > n:
            return False
        cum_prob = [amp * amp for st, amp in self.state]

        for i in range(1, len(self.state)):
            cum_prob[i] += cum_prob[i - 1]
        r = random.uniform(0, 1)
        idx = bisect.bisect_left(cum_prob, r)
        result = self.state[idx][0][a:b]
        self.state = list(filter(lambda st: st[0][a:b] == result, self.state))
        self.__normalize__()
        return result
    
    def set_value(self, a, b, val):
        # check whether val can fit into (a,b) range
        bstr = '{0:b}'.format(val).zfill(b - a)
        if len(bstr) > b - a:
            raise ValueError('value is too large')
        bstr_l = [int(x) for x in bstr]
        self.measure(a, b)
        for i in range(len(self.state)):
            self.state[i][0][a:b] = bstr_l
        self.__cleanup__()
    
    def hadamard(self, a, b):
        n = self.len
        if a > b or a < 0 or b > n:
            raise ValueError("can't hadamard this right now: reason 1")
        if list(filter(lambda st: st[0][a:b] != ([0]*(b-a)), self.state)):
            raise ValueError("can't hadamard this right now: reason 2")
        temp = []
        for st, amp in self.state:
            for i in range(2**(b-a)):
                nst = st[:]
                nst[a:b] = [int(x) for x in '{0:b}'.format(i).zfill(b-a)]
                temp.append((nst, amp * 1 / math.sqrt(2**(b-a))))
        self.state = temp
        
    def get_probability(self, a, b, name=None, save=False):
        """
        get snapshot of probability of the range [a, b)
        """
        # todo: make it general for complex amplitude
        prob_vec = [(st, amp * amp) for st, amp in self.state]
        prob_vec = sorted([(list(st), sum(j for i, j in prob_group)) 
                   for st, prob_group in Util.groupby_unsorted(prob_vec, key=lambda x: tuple(x[0][a:b]))])
        return prob_vec

    def __expand_state__(self, a, b):
        n = b - a
        st_dict = {}
        distinct_gen = Util.groupby_unsorted(map(lambda x: x[0], self.state), key=lambda x: tuple(x[:a] + x[b:]))
        for st, _ in distinct_gen:
            for i in range(2**n):
                nst = list(st)
                nst[a:a] = [int(x) for x in '{0:b}'.format(i).zfill(n)]
                st_dict[tuple(nst)] = 0.00
        for st, amp in self.state:
            st_dict[tuple(st)] = amp
        self.state = list(st_dict.items())
        
    def __normalize__(self):
        renorm_factor = math.sqrt(sum([amp*amp for st, amp in self.state]))
        self.state = [(st, amp/renorm_factor) for st, amp in self.state]

    def __cleanup__(self):
        self.state = list(filter(lambda x: x[1] != 0.00, self.state))
        self.state = sorted([(list(st), sum(j for i, j in amp_group)) 
                     for st, amp_group in Util.groupby_unsorted(self.state, key=lambda x: tuple(x[0]))])

#%%
def qu_comparator(state_vector, bound_a, bound_b):
    """
    state_vector
    bound is [start, end)
    """
    n = len(state_vector)
    
    if type(bound_a) is not tuple or type(bound_b) is not tuple:
        raise ValueError('invalid input: not tuples')
        
    a, b = bound_a
    c, d = bound_b
    
    if b - a != d - c:
        raise ValueError("input qreg doesn't have the same size = {}, {}".format(b-a, d-c))
        
    if a < 0 or b > n or c < 0 or d > n:
        raise ValueError('index out of bound')

    return state_vector[a:b] > state_vector[c:d]
    
def fixed_comparator(state_vector, bound, value):
    # n = len(state_vector)
    if type(bound) is not tuple:
        raise ValueError('invalid input: not tuples')
    
    a, b = bound
    bstr = '{0:b}'.format(value).zfill(b - a)
    bstr_l = [int(x) for x in bstr]
    return state_vector[a:b] > bstr_l
    
def grover(qureg, Uf, input_bound, bounds):
    """
    qureg: [(state, amplitude)]
    input_bound: (a, b) 
    bounds: [(start, end)] 
    Uf: function that outputs 0, 1
    """
    bds = [input_bound] + bounds
    # flip state that has Uf(x) = 1
    # Todo: make it more general
    qureg.state = [(st, -amp) if Uf(st, bds[0], bds[1]) else (st, amp) for (st, amp) in qureg.state]
    pp.pprint(qureg.state)
    # inverse around the mean
    qureg.__expand_state__(input_bound[0], input_bound[1])
    n = len(qureg.state)
    mean = sum(map(lambda x: x[1], qureg.state)) / n
    # print('mean = {}'.format(mean))
    qureg.state = [(st, 2*mean-amp) for (st, amp) in qureg.state]
    qureg.__cleanup__()

plt.figure(figsize=(16,10))
pp = pprint.PrettyPrinter(indent=4)
