import struct
import sys
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from time import sleep

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


def process_stream(win_len, instream, outfilename):
    if outfilename == "-":
        outfile = sys.stdout.buffer
        close_outfile = False
    else:
        outfile = open(outfilename, "wb")
        close_outfile = True
    ma = MovingAverage(win_len)
    while True:
        chunk = instream.read(DOUBLE_SIZE)
        if len(chunk) < DOUBLE_SIZE:
            break
        value = struct.unpack("<d", chunk)[0]
        avg_value = ma.next(value)
        if avg_value is not None:
            outfile.write(struct.pack("<d", avg_value))
    if close_outfile:
        outfile.close()


def process_single_stream(args):
    win_len, infilename, outfilename = args
    with open(infilename, "rb") as infile:
        process_stream(win_len, infile, outfilename)


def process_stdin_stream(win_len, stream, outfilename):
    process_stream(win_len, stream, outfilename)


if __name__ == "__main__":
    stream_params = []
    sleep(0.01)  # TODO: a bit hacky, wait a bit for the first stream to be available
    # why need the sleep? To ensure that the input streams are ready before processing
    # is there a better way to do this?
    args = sys.argv[1:]
    parallel = False
    if "--parallel" in args:
        parallel = True
        args.remove("--parallel")

    for arg in args:
        win_len, infilename, outfilename = arg.split(",")
        if infilename == "-":
            process_stdin_stream(int(win_len), sys.stdin.buffer, outfilename)
        else:
            stream_params.append((int(win_len), infilename, outfilename))

    if parallel:
        with ProcessPoolExecutor() as pool:
            pool.map(process_single_stream, stream_params)
            pool.shutdown()
    else:
        retries = 5
        while retries > 0 and stream_params:
            next_round = []
            for stream in stream_params:
                try:
                    process_single_stream(stream)
                except FileNotFoundError:
                    next_round.append(stream)
            if not next_round:
                break
            stream_params = next_round
            retries -= 1
            sleep(0.01)
