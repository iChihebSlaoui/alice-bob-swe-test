# TODO: modify this file as necessary, to implement the moving average
#  and process incoming data to the appropriate destination

import sys
from time import sleep
import struct
from collections import deque


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
        return self.sum / len(self.queue)


# streams is a list of tuples (window_length, input_file, output_file)
def process_streams(streams):
    pass


if __name__ == "__main__":
    stream_params = []
    sleep(0.01)  # TODO: a bit hacky, wait a bit for the first stream to be available
    for arg in sys.argv[1:]:
        win_len, infilename, outfilename = arg.split(",")
        if infilename == "-":
            infile = sys.stdin.buffer
        else:
            infile = open(infilename, "rb")
        if outfilename == "-":
            outfile = sys.stdout.buffer
        else:
            outfile = open(outfilename, "wb")
        stream_params.append((int(win_len), infile, outfile))
    process_streams(stream_params)
