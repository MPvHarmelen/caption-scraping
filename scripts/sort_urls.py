#!env/bin/python3

# Sort a file with many urls into separate files per netloc.

import os
from urllib.parse import urlparse

# Sort
def categorise(iterable, threshold=100, key=lambda a: urlparse(a).netloc):
    """Create a dict with netloc as keys and a list of urls as values."""
    categories = {}
    for item in iterable:
        k = key(item)
        if k in categories:
            categories[k].append(item)
        else:
            categories[k] = [item]

    if threshold:
        categories = dict(
            (cat, value) for cat, value in categories.items()
            if len(value) >= threshold
        )
    return categories

# Output
# Create a folder 'sorted_urls'
# Write a file per url with <netloc>.csv as name

if __name__ == '__main__':
    # Input
    import argparse
    parser = argparse.ArgumentParser(
        description='Sort urls from a file into different files according to netlocs'
    )
    parser.add_argument('filename', metavar='input file', nargs=1,
                        help='File to read urls from')
    parser.add_argument('output_folder', metavar='output folder', nargs=1,
                        default='sorted_urls', help='File to output counts to')
    args = parser.parse_args()
    filename = args.filename[0]
    output_folder = args.output_folder[0]

    # Create folder before categorising to quickly find out if the
    # output folder can be used.
    try:
        os.makedirs(output_folder, exist_ok=True)
    except FileExistsError:
        print('A file with the name {} already exists'.format(output_folder))
        # Fail
        exit(1)

    # Categorise
    with open(filename) as filedescriptor:
        categories = categorise(filedescriptor)

    # For each netloc, create and write file
    for netloc in categories:
        output_file = os.path.join(output_folder, '{}.csv'.format(netloc))
        with open(output_file, 'w') as filedescriptor:
            for url in categories[netloc]:
                # I think there is still a newline in the url because
                # it came from a file, but I'm not sure.
                filedescriptor.write(url)
