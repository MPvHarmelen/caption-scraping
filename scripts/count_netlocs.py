#!env/bin/python3

# This script takes a file with urls as an argument and prints an ordered list
# of netloc counts.

from urllib.parse import urlparse

def count(iterable, key=lambda a: urlparse(a).netloc):
    """Count the duplicate results given by key() in iterable"""
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
    parser = argparse.ArgumentParser(description='Count netlocs of urls from a file')
    parser.add_argument('input_filename', metavar='input file', nargs=1, help='File to read urls from')
    parser.add_argument('output_filename', metavar='output file', nargs='?',
                        help='File to output counts to')
    args = parser.parse_args()
    input_filename = args.input_filename[0]
    output_filename = args.output_filename

    # Calculate
    with open(input_filename) as file_descriptor:
        counts = count(file_descriptor)

    # Output
    sorted_counts = sorted(counts.items(), key=lambda a: a[1], reverse=True)
    if output_filename:
        # Save output
        with open(output_filename, 'w') as output_file:
            for k, v in sorted_counts:
                output_file.write('{}, {}\n'.format(k, v))
    else:
        # Print output (and some extra info)
        for k, v in sorted_counts:
            print(k, '\t', v)

        END_SLICE = 20
        numbers_only = sorted(counts.values())
        total = sum(numbers_only)
        first_items = sum(numbers_only[:END_SLICE])
        percentage = round(float(first_items) / total * 100, 2)
        print('The first {} urls account for {} of {} urls ({} %)'.format(
            END_SLICE,
            first_items,
            total,
            percentage
        ))
