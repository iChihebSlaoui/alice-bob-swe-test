# TODO: modify this file as necessary, to implement the moving average
#  and process incoming data to the appropriate destination

import struct
import sys
from collections import deque
from time import sleep
from concurrent.futures import ProcessPoolExecutor

DOUBLE_SIZE = 8  # 8 bytes for double


class MovingAverage:
    def __init__(self, size: int):
        self.size = size
        self.queue = deque()
        self.sum = 0.0

    def next(self, val: int) -> float:
        self.queue.append(val)
        self.sum += val
        if len(self.queue) > self.size:
            self.sum -= self.queue.popleft()
        elif len(self.queue) < self.size:
            return 0.0
        return self.sum / len(self.queue)


# streams is a list of tuples (window_length, input_file, output_file)
def process_single_stream(args):
    win_len, infilename, outfilename = args
    print(f"Processing stream with window length {win_len}, input {infilename}, output {outfilename}")
    if infilename == "-":
        infile = sys.stdin.buffer
    else:
        infile = open(infilename, "rb")
    if outfilename == "-":
        outfile = sys.stdout.buffer
    else:
        outfile = open(outfilename, "wb")
    
    ma = MovingAverage(win_len)  # Initialize moving average
    while True:
        chunk = infile.read(DOUBLE_SIZE)
        if len(chunk) < DOUBLE_SIZE:
            break
        value = struct.unpack("<d", chunk)[0]  # little-endian double
        avg_value = ma.next(value)
        outfile.write(struct.pack("<d", avg_value))
    infile.close()
    outfile.close()


if __name__ == "__main__":
    stream_params = []
    sleep(0.01)  # TODO: a bit hacky, wait a bit for the first stream to be available
    for arg in sys.argv[1:]:
        win_len, infilename, outfilename = arg.split(",")
        stream_params.append((int(win_len), infilename, outfilename))
    with ProcessPoolExecutor() as pool:
        pool.map(process_single_stream, stream_params)
        pool.shutdown()
