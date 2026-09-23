# use the numpy package to do basic array stuff
import numpy as np

# take array, return mean
def array_mean(values):
    return float(np.mean(values))

# return min, max, sum of array vals
def array_stats(values):
    array = np.array(values)
    return {
        "min": float(array.min()),
        "max": float(array.max()),
        "sum": float(array.sum()),
    }

# mult array vals and return list
def scale(values, factor):
    return (np.array(values) * factor).tolist()


if __name__ == "__main__":
    print(array_mean([1, 2, 3, 4]))
    print(array_stats([5, 1, 9]))
    print(scale([1, 2, 3], 3))