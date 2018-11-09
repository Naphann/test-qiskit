import collections
import datetime
import os
import matplotlib.pyplot as plt
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt

def groupby_unsorted(seq, key=lambda x: x):
    indexes = collections.defaultdict(list)
    for i, elem in enumerate(seq):
        indexes[key(elem)].append(i)
    for k, idxs in indexes.items():
        yield k, (seq[i] for i in idxs)

def plot_prob(probs, title='', pos=None, ax=None, dec=False, n=4):
    x, y = zip(*probs)
    x = list(map(lambda x: ''.join(map(str, x)), x))
    if dec:
        x = list(map(lambda y: '/'.join(y), map(lambda y: [str(int(y[i:i+n], 2)) for i in range(0, len(y), n)], x)))
    if ax is None and pos is not None:
        plt.subplot(pos)
        plt.bar(x, y)
    else:
        ax.set_ylim(-1, 1)
        ax.bar(x, y)
        ax.set_title(title)

def create_pic_folder():
    dir_name = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_name = 'pics/' + dir_name
    dir_list = sorted(list(filter(lambda x: x[0:len(dir_name)] == dir_name, [x[0] for x in os.walk('pics')])))
    if len(dir_list) == 0:
        dir_name += '-001'
    else:
        no = str(int(dir_list[-1].split('-')[-1]) + 1).zfill(3)
        dir_name += '-{}'.format(no)
        print(dir_name)
    os.mkdir(dir_name)
    return dir_name

def save_histogram(data, dirname, title, number_to_keep=False):
    """Plot a histogram of data.

    data is a dictionary of  {'000': 5, '010': 113, ...}
    number_to_keep is the number of terms to plot and rest is made into a
    single bar called other values
    """
    if number_to_keep is not False:
        data_temp = dict(Counter(data).most_common(number_to_keep))
        data_temp["rest"] = sum(data.values()) - sum(data_temp.values())
        data = data_temp

    labels = sorted(data)
    values = np.array([data[key] for key in labels], dtype=float)
    pvalues = values / sum(values)
    numelem = len(values)
    ind = np.arange(numelem)  # the x locations for the groups
    width = 0.35  # the width of the bars
    _, ax = plt.subplots()
    rects = ax.bar(ind, pvalues, width, color='seagreen')
    # add some text for labels, title, and axes ticks
    ax.set_ylabel('Probabilities', fontsize=12)
    ax.set_xticks(ind)
    ax.set_xticklabels(labels, fontsize=12, rotation=70)
    ax.set_ylim([0., min([1.2, max([1.2 * val for val in pvalues])])])
    ax.set_title(title)
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                '%f' % float(height),
                ha='center', va='bottom')
    
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    plt.savefig('{}/{}.png'.format(dirname, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
    plt.close()
