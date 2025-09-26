import sys
import struct

DOUBLE_SIZE = 8  # 8 bytes for double

def encode_file():
    if len(sys.argv) < 2:
        print("Usage: encode_binary.py inputfile outputfile")
        sys.exit(1)

    infile = sys.argv[1]
    outfile = sys.argv[2]
    with open(infile, "r") as f:
        values = [float(x) for x in f.read().strip().split()]
        f.close()

    with open(outfile, "wb") as f:
        for v in values:
            f.write(struct.pack("<d", v))
        f.close()

if __name__ == "__main__":
    encode_file()