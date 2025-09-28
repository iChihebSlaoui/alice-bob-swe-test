import struct
import sys

DOUBLE_SIZE = 8  # 8 bytes for double


def encode_file(stream):
    values = [float(x) for x in stream.read().strip().split()]
    if len(sys.argv) <= 1:
        for v in values:
            sys.stdout.buffer.write(struct.pack("<d", v))
    else:
        outfile = sys.argv[1]
        with open(outfile, "wb") as outfile:
            for v in values:
                outfile.write(struct.pack("<d", v))
            outfile.close()


if __name__ == "__main__":
    encode_file(sys.stdin.buffer)
