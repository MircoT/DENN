from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter


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