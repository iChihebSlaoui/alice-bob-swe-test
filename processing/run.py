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
            return None
        return self.sum / len(self.queue)


# streams is a list of tuples (window_length, input_file, output_file)
def process_single_stream(args):
    win_len, infilename, outfilename = args
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
        if avg_value is not None:
            outfile.write(struct.pack("<d", avg_value))
    infile.close()
    outfile.close()


def process_stdin_streams(win_len, stream, outfilename):
    if outfilename == "-":
        outfile = sys.stdout.buffer
    else:
        outfile = open(outfilename, "wb")
    ma = MovingAverage(win_len)  # Initialize moving average
    while True:
        chunk = stream.read(DOUBLE_SIZE)
        if len(chunk) < DOUBLE_SIZE:
            break
        value = struct.unpack("<d", chunk)[0]  # little-endian double
        avg_value = ma.next(value)
        if avg_value is not None:
            outfile.write(struct.pack("<d", avg_value))
    outfile.close()
    


if __name__ == "__main__":
    stream_params = []
    sleep(0.01)  # TODO: a bit hacky, wait a bit for the first stream to be available
    # why need the sleep? To ensure that the input streams are ready before processing
    # is there a better way to do this?

    for arg in sys.argv[1:]:
        win_len, infilename, outfilename = arg.split(",")
        if infilename == "-":
            process_stdin_streams(int(win_len), sys.stdin.buffer, outfilename)
        else:
            stream_params.append((int(win_len), infilename, outfilename))

    # # is there a better way than ProcessPoolExecutor?
    with ProcessPoolExecutor() as pool:
        pool.map(process_single_stream, stream_params)
        pool.shutdown()
