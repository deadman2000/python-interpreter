import argparse
import datetime
import sys
import msgpack
from formats.win32exe import ExeFormat


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.timestamp()
    return obj


def main():
    parser = argparse.ArgumentParser(description='Parsing file to msgpack format')
    parser.add_argument('--in', metavar='IN_FILE', help='input file to parsing', required=True)
    parser.add_argument('--out', metavar='OUT_FILE', help='output destination')
    args = vars(parser.parse_args())

    fmt = ExeFormat()
    try:
        obj = fmt.parse_file(args['in'], to_meta=True, compact_meta=True)
    except Exception:
        obj = {}

    # http://sugendran.github.io/msgpack-visualizer/
    data = msgpack.packb(obj, default=encode_datetime, use_bin_type=True)
    sys.stdout.buffer.write(data)


if __name__ == '__main__':
    main()
