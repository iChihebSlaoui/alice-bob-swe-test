import struct
import sys

DOUBLE_SIZE = 8  # 8 bytes for double


def decode_stream(stream):
    while True:
        chunk = stream.read(DOUBLE_SIZE)
        if len(chunk) < DOUBLE_SIZE:
            break
        value = struct.unpack("<d", chunk)[0]  # little-endian double
        print(value)
        # i want to send each value to stdout as text
        # but also flush stdout so that the value is immediately available
        sys.stdout.flush()


if __name__ == "__main__":
    decode_stream(sys.stdin.buffer)
