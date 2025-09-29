import struct
import sys
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from time import sleep
from typing import BinaryIO, Optional

DOUBLE_SIZE = 8  # 8 bytes for double


class MovingAverage:
    """
    Computes the moving average of a stream of float values using a fixed window size.
    """

    def __init__(self, size: int):
        """
        Args:
            size (int): The window size for the moving average.
        """
        self.size = size
        self.queue = deque()
        self.sum = 0.0

    def next(self, val: float) -> Optional[float]:
        """
        Add a new value to the stream and compute the moving average if enough values are present.

        Args:
            val (float): The new value to add.

        Returns:
            Optional[float]: The moving average, or None if not enough values are present.
        """
        self.queue.append(val)
        self.sum += val
        if len(self.queue) > self.size:
            self.sum -= self.queue.popleft()
        elif len(self.queue) < self.size:
            return None
        return self.sum / self.size


def process_stream(win_len: int, instream: BinaryIO, outfilename: str) -> None:
    """
    Process a binary stream of doubles, compute moving averages, and write results as binary doubles.

    Args:
        win_len (int): Window length for moving average.
        instream (BinaryIO): Input binary stream.
        outfilename (str): Output filename or "-" for stdout.
    """
    if outfilename == "-":
        outfile = sys.stdout.buffer
        close_outfile = False
    else:
        outfile = open(outfilename, "wb")
        close_outfile = True
    try:
        ma = MovingAverage(win_len)
        while True:
            chunk = instream.read(DOUBLE_SIZE)
            if len(chunk) < DOUBLE_SIZE:
                break
            value = struct.unpack("<d", chunk)[0]
            avg_value = ma.next(value)
            if avg_value is not None:
                outfile.write(struct.pack("<d", avg_value))
    finally:
        if close_outfile:
            outfile.close()


def process_single_stream(args: tuple[int, str, str]) -> None:
    """
    Process a single input file and write moving averages to output file.

    Args:
        args (Tuple[int, str, str]): (window length, input filename, output filename)
    """
    win_len, infilename, outfilename = args
    with open(infilename, "rb") as infile:
        process_stream(win_len, infile, outfilename)


def process_stdin_stream(win_len: int, stream: BinaryIO, outfilename: str) -> None:
    """
    Process a stream from stdin and write moving averages to output file.

    Args:
        win_len (int): Window length for moving average.
        stream (BinaryIO): Input binary stream (stdin).
        outfilename (str): Output filename or "-" for stdout.
    """
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
