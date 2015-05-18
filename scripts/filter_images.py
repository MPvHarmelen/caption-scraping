#!env/bin/python3

# Filter the rows with images from the data

from copy import deepcopy

def filter_data(data, key=lambda row: 'Image' in row):
    """
    Take data formatted as dumped by kimonolabs and remove rows without an image.

    Assume there is only one collection
    Update count
    """
    # Make sure we don't muck up the data that was given
    data = deepcopy(data)
    collections = data['results']

    # There is only one collection
    collection_name = next(collections.__iter__())

    # Filter
    rows = collections[collection_name]
    collections[collection_name] = [row for row in rows if key(row)]
    data['count'] = len(collections[collection_name])
    return data, (data['count'], len(rows))


if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser(description='Filter usable json data')
    parser.add_argument('input_filename', metavar='input file', nargs=1,
                        help='File to read json from')
    parser.add_argument('output_filename', metavar='output file', nargs='?',
                        help='File to output filtered json to')
    args = parser.parse_args()
    input_filename = args.input_filename[0]
    output_filename = args.output_filename or '.'.join(
        input_filename.split('.')[:-1] + [
            'clean',
            input_filename.split('.')[-1]
        ]
    )

    # Read
    with open(input_filename) as filedescriptor:
        data = json.load(filedescriptor)

    # Filter
    clean_data, info = filter_data(data)

    # Write
    with open(output_filename, 'w') as filedescriptor:
        # Indent with 4 spaces
        json.dump(clean_data, filedescriptor, indent=4)

    print('Found {} of {} rows with images.'.format(*info))
