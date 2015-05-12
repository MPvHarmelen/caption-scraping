#!env/bin/python3

# This script takes a file with urls as an argument and prints an ordered list
# of netloc counts.

from urllib.parse import urlparse

def count(iterable, key=lambda a: urlparse(a).netloc):
    """Count the duplicate results given by key()"""
    counts = {}
    for item in iterable:
        k = key(item)
        if k in counts:
            counts[k] += 1
        else:
            counts[k] = 1
    return counts

if __name__ == '__main__':
    # Input
    import argparse
    parser = argparse.ArgumentParser(description='Count netlocs of urls in a file')
    parser.add_argument('filename', nargs=1, help='Filename to read urls from')
    filename = parser.parse_args().filename[0]

    # Calculate
    file_descriptor = open(filename)
    counts = count(file_descriptor)

    # Output
    sorted_counts = sorted(counts.items(), key=lambda a: a[1])
    for k, v in sorted_counts:
        print(k, '\t', v)

    END_SLICE = 20
    numbers_only = sorted(counts.values())
    total = sum(numbers_only)
    last_items = sum(numbers_only[-END_SLICE:])
    percentage = round(float(last_items) / total * 100, 2)
    print('The last {} urls account for {} of {} urls ({} %)'.format(
        END_SLICE,
        last_items,
        total,
        percentage
    ))
