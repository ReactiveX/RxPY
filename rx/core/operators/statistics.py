from rx.core import Observable
import math


def determine_median(sorted_list):
    if len(sorted_list) == 0:
        raise Exception("The input sequence was empty")

    if len(sorted_list) % 2 == 1:
        return sorted_list[int((len(sorted_list) + 1) / 2) - 1]
    else:
        median_1 = sorted_list[int((len(sorted_list) + 1) / 2) - 1]
        median_2 = sorted_list[int((len(sorted_list) + 1) / 2)]
        return float(median_1 + median_2) / 2.0


def median(source: Observable) -> Observable:
    """
    Calculates the statistical median on numerical emissions. The sequence must be finite.
    """
    return source.to_sorted_list().map(lambda l: determine_median(l))


def mode(source: Observable) -> Observable:
    """
    Returns the most frequently emitted value (or "values" if they have the same number of occurrences).
    The sequence must be finite.
    """
    return source.group_by(lambda v: v) \
        .flat_map(lambda grp: grp.count().map(lambda ct: (grp.key, ct))) \
        .to_sorted_list(lambda t: t[1], reverse=True) \
        .flat_map(lambda l: Observable.from_(l).take_while(lambda t: t[1] == l[0][1])) \
        .map(lambda t: t[0])


def variance(source: Observable) -> Observable:
    """
    Returns the statistical variance of the numerical emissions.
    The sequence must be finite.
    """
    squared_values = source.to_list() \
        .flat_map(lambda l: Observable.from_(l).average().flat_map(lambda avg: Observable.from_(l).map(lambda i: i - avg))) \
        .map(lambda i: i * i) \
        .publish() \
        .auto_connect(2)

    return Observable.zip(squared_values.sum(), squared_values.count(), lambda sum, ct: sum / (ct - 1))


def standard_deviation(source: Observable) -> Observable:
    """
    Returns the standard deviation of the numerical emissions:
    The sequence must be finite.
    """
    return source.variance().map(lambda i: math.sqrt(i))


