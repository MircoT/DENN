from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.ticker import FuncFormatter
import numpy as np
from math import cos, pi
import json


def NN_DE_mnist_loader(filename):
    with open(filename, "r") as input_file:
        res = json.load(input_file)
    return [np.array(res['W']), np.array(res['b'])]


def NN_DE_result_loader(filename,method = 'rand/1/bin'):
    with open(filename, "r") as input_file:
        res = json.load(input_file)
    return res['results'][method]['best_of']['individual']


def NN_to_image(test_result_file, shape, level=0, loader="DE",method = 'rand/1/bin'):
    if loader == "DE":
        individual = NN_DE_result_loader(test_result_file,method)
        W = np.array(individual[0 + (level * 2)])
        b = np.array(individual[1 + (level * 2)])
    elif loader == "gradient":
        W, b = NN_DE_mnist_loader(test_result_file)
    else:
        raise Exception("Error: Unknown loader...")

    W = W + b

    columns = np.hsplit(W, W.shape[-1])

    ##
    # Reshape
    images = []
    for image in columns:
        # print(image.shape)
        images.append(image.reshape(shape))

    ##
    # Normalization
    for image in images:
        max_ = np.max(image)
        min_ = np.min(image)
        image = image - min_
        image = image / (max_ - min_)
        # print(image)

    images = np.array(images)
    # print(images.shape)

    fig = plt.figure()

    for num, image in enumerate(images):
        sub_plt = plt.subplot(2, 5, num + 1)
        sub_plt.set_title(str(num))
        plt.imshow(image, cmap=plt.cm.Greys,
                   interpolation='nearest')

    plt.tight_layout()
    plt.show()
    plt.close()


def my_confusion_matrix(fig, matrix):
    # print(matrix)
    plt.clf()
    norm_conf = []
    for i in matrix:
        a = 0
        tmp_arr = []
        a = sum(i, 0)
        for j in i:
            tmp_arr.append(float(j) / float(a))
        norm_conf.append(tmp_arr)

    res = plt.imshow(norm_conf, cmap=plt.cm.jet,
                     interpolation='nearest')

    width, height = matrix.shape

    for x in range(width):
        for y in range(height):
            plt.annotate(str(matrix[x][y]), xy=(y, x),
                         horizontalalignment='center',
                         verticalalignment='center')

    cb = fig.colorbar(res)

    plt.xticks(range(width), [str(num) for num in range(width)])
    plt.yticks(range(height), [str(num) for num in range(height)])


def my_filter(string, rules):
    tmp = string.split("\t")

    try:
        tmp = [float(val) for val in tmp]
    except ValueError:
        return False

    return [type_(tmp[index]) for index, type_ in rules]


def extract(filename, data_filter, rules):
    values = [[] for _ in range(len(rules))]

    with open(filename, 'r') as data:
        for line in data.readlines():
            tmp = data_filter(line, rules)
            if tmp:
                for pos, value in enumerate(tmp):
                    values[pos].append(value)

    return values


def dispersion(origin, target):
    tmp = []
    for index, value in enumerate(target[0]):
        diff = value - origin[0][index]
        try:
            tmp.append((diff * 100.) / abs(origin[0][index]))
        except ZeroDivisionError:
            tmp.append(0)

    return tmp


def my_plot(fig, data):

    for points in data:
        x, y = points['values']
        plt.plot(x, y,
                 color=points['color'],
                 label=points['label'],
                 alpha=points.get('alpha', 1.0))

    plt.legend()


def to_percent(y, position):
    return "{:.02f}%".format(y * 100.)


def my_hist(fig, data, bins_, range_, colors, labels, normalized=False, max_y=None):
    plt.hist(data,
             bins=bins_, range=range_,
             color=colors, label=labels,
             alpha=0.81, normed=normalized,
             )

    plt.legend(prop={'size': 10})
    x1, x2, y1, y2 = plt.axis()

    if max_y:
        plt.axis((x1, x2, 0, max_y))

    if normalized:
        formatter = FuncFormatter(to_percent)
        plt.gca().yaxis.set_major_formatter(formatter)


def plot_results(results, save=False):
    """Plot a result graph.

    Params:
        results (dict or string): the result dictionary or the json file to
                                  parse

    Note:
        results: {
            "title": ...,
            "x_label": ...,
            "y_label": ...
        }
    """
    MARKERS = ['o', '^', '*', 's', '+', 'v']
    COLORS = [
        "#000000",
        "#999999",
        "#222222",
        "#555555",
        "#AAAAAA",
        "#CCCCCC"
    ]
    ALPHA = [
        0.9,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
    ]
    LINESTYLE = [":", "--", "-", "-.", "steps", ":"]

    if type(results) != dict:
        with open(results) as result_file:
            from json import load as js_load
            results = js_load(result_file)

    fig = plt.figure()
    fig.suptitle(results.get('title', ''), fontsize=14, fontweight='bold')

    data = results.get('results')
    labels = []

    if results.get("sorted", False):
        all_data = enumerate(sorted(data.items(), key=lambda elm: int(elm[0])))
    else:
        all_data = enumerate(data.items())

    for idx, (type_, obj) in all_data:
        if results.get("max_step", False):
            _y_ = obj.get('values')[:results.get("max_step")]
        else:
            _y_ = obj.get('values')
        _x_ = range(len(_y_))
        gen_step = results.get("gen_step", 1)
        tot_gen = (len(_y_) - 1) * gen_step

        x_real = range(tot_gen)
        y_real = []

        for _n_, val in enumerate(_y_[:-1]):
            next_ = _y_[_n_ + 1]
            y_real.append(val)
            for cur_step in range(gen_step - 1):
                ##
                # Cos interpolation
                alpha = float((cur_step + 1.) / gen_step)
                alpha2 = (1 - cos(alpha * pi)) / 2
                new_point = (val * (1 - alpha2) + next_ * alpha2)
                y_real.append(
                    new_point
                )

        ##
        # Do lines and point
        cur_plot = plt.plot(
            x_real, y_real,
            marker=obj.get('marker', MARKERS[idx]),
            markersize=obj.get('markersize', None),
            color=obj.get('color', COLORS[idx]),
            linewidth=obj.get('linewidth', 1),
            #  ls=LINESTYLE[idx],
            alpha=obj.get('alpha', ALPHA[idx]),
            label=obj.get('label'),
            markevery=results.get(
                "markevery", [int(elm * gen_step) for elm in _x_[:-1]])
        )
        labels.append(cur_plot[0])

    plt.legend(
        handler_map=dict(
            [
                (label, HandlerLine2D(numpoints=1))for label in labels
            ]
        ),
        bbox_to_anchor=results.get("legend_ancor", (1.0, 1.0)),
        fontsize=18
    )

    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.tick_params(axis='both', which='minor', labelsize=14)

    plt.axis((0, tot_gen, 0, 1))
    plt.xlabel(results.get('x_label', 'Generations'), fontsize=14)
    plt.ylabel(results.get('y_label', 'Accuracy'), fontsize=14)
    plt.grid(True)

    if save:
        plt.savefig("{}.png".format(save), dpi=600, bbox_inches='tight')
        print("+ out file -> {}.png".format(save))
    plt.show()
    plt.close()
