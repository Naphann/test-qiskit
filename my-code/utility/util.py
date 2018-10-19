import collections
import matplotlib.pyplot as plt

def groupby_unsorted(seq, key=lambda x: x):
    indexes = collections.defaultdict(list)
    for i, elem in enumerate(seq):
        indexes[key(elem)].append(i)
    for k, idxs in indexes.items():
        yield k, (seq[i] for i in idxs)

def plot_prob(probs, pos):
    x, y = zip(*probs)
    plt.subplot(pos)
    plt.bar(x, y)