from rx.core import Observable
from rx.internal import extensionmethod


def determine_median(sorted_list):
    if len(sorted_list) == 0:
        raise Exception("The input sequence was empty")

    if len(sorted_list) % 2 == 1:
        return sorted_list[int((len(sorted_list) + 1) / 2) - 1]
    else:
        median_1 = sorted_list[int((len(sorted_list) + 1) / 2) - 1]
        median_2 = sorted_list[int((len(sorted_list) + 1) / 2)]
        return float(median_1 + median_2) / 2.0


@extensionmethod(Observable)
def median(self):
    """
    Calculates the statistical median on numerical emissions. The sequence must be finite.
    """
    return self.to_sorted_list().map(lambda l: determine_median(l))


@extensionmethod(Observable)
def mode(self):
    """
    returns the most frequently emitted value (or "values" if they have the same number of occurrences)
    """
    return self.group_by(lambda v: v) \
        .flat_map(lambda grp: grp.count().map(lambda ct: (grp.key, ct))) \
        .to_sorted_list(lambda t: t[1], reverse=True) \
        .flat_map(lambda l: Observable.from_(l).take_while(lambda t: t[1] == l[0][1])) \
        .map(lambda t: t[0])



