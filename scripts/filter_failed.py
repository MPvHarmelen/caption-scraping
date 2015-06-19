from filter_images import filter_data

if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser(description='Filter usable json data')
    parser.add_argument('input_filename', metavar='input file', nargs=1, help='File to read json from')
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
        json.dump(clean_data, filedescriptor)

    print('Found {} of {} rows with images.'.format(*info))
