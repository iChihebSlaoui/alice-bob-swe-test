# Design notes
I took time to get familirized with the problem, play with it, discover it, almost for the more philosophing and poeting of the engineers: to fall in love with the problem.

My first step has been to fill the some vacuum knowledge, by implementing fast utils to play with, and get a hands on feel of the subject.

Within my first step, I gain "eyes" to see in side the box:

```bash
python3 encode_binary.py input.txt input1
cat data/sample-data-out | python3 decode_binary.py
```

I implemented encode_binary.py as well as decode_binary.py so I can input the data that I want

```bash
cat input.txt | python3 encode_binary.py input1
cat input1 | python3 decode_binary.py
```

Second step, figure out the mechanics of the data pipeline:
```bash
# terminal 1
./datastream.sh input1,output
# terminal 2
python3 processing/run.py 3,output,- | python3 decode_binary.py
```
Third step, the moving average for a data stream.
The moving average for a data stream needs to compute each new element with the previous in a secuential mode.

```python
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
```
This moving average algorithm uses a queue data structure, organizing information by FIFO method.

As I figured out the mechanics of the data streaming pipeline, I now dive in to the core of the problem:
how to handle multiple moving average data streams ? some theorethical options:
- one stream after the other
- parallel streams
- a "buck" from a stream, a "buck" from another stream
- multiple python runners

The last two options prove to be not optimized, as the buck-per-buck would be subperformant in front of the parallel streams, and the multiple python runners would be a considered option for a large scale and distributed solution to a large scale problem, which is currently not our case scenario.

The final step, has been the code review, including the verification of the imports, the code style best practices (naming, docstrings, comments and type hints), and assessing the functional behaviour, the robustness of code, insuring its readability and maintainability.

# Expected behaviour
The expected behaviour for the code is derived from the tests, following the Test Driven Development approach, funeling the clients or our stakeholders expectations.

- Named pipes
    ```bash
    # terminal 1
    ./datastream.sh input1,in
    # terminal 2
    python3 processing/run.py 3,in,output
    ```
- stdin stdout
    ```bash
    python3 processing/run.py 3,-,- < data/sample-data-in | python3 decode_binary.py
    ```
- Multiple secuential streams in order
    ```bash
    # terminal 1
    ./datastream.sh input1,in1 input2,in2
    # terminal 2
    python3 processing/run.py 3,in1,output2 5,in2,output2
    ```
- Multiple secuential streams in inverted order
    ```bash
    # terminal 1
    ./datastream.sh input1,in1 input2,in2
    # terminal 2
    python3 processing/run.py 3,in1,output2 5,in2,output2
    ```
- Multiple parallel streams
    ```bash
    # terminal 1
    ./datastream.sh input1,in1 input2,in2
    # terminal 2
    python3 processing/run.py 3,in1,output2 5,in2,output2
    ```

After running the tests:
```bash
python3 tests/test_processing_cli.py
```
I was able to validate the tests:
```bash
test_multiple_invert_order (__main__.AdvancedTests.test_multiple_invert_order) ... ok
test_multiple_parallel (__main__.AdvancedTests.test_multiple_parallel) ... ok
test_multiple_right_order (__main__.AdvancedTests.test_multiple_right_order) ... ok
test_named_pipes (__main__.BasicTests.test_named_pipes) ... ok
test_stdout_stdin (__main__.BasicTests.test_stdout_stdin) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.652s
```

The main difficulty was in understanding the errors and failures with validating the tests:
- Assertion errors: Basically that my output file didn't match the expected output file. While obvious for the named pipes test, it was interesting to see that the `sys.stdin.buffer` does not "travel well" inside multiple functions.
- File Not Found error: While being intrigued by the `sleep(0.01)`, I then understood with this recurring error in my debugging the intricacies of the named pipes or FIFO files; which I resolved with a round robin retry mechanism.

# Personal Feedback
Thank you for this very interesting, and much enjoyed take-home assessment, as it has a wide technical span: named pipes, parallelism, processing of streams of data, functions with CLI arguments.
A great exercice to assess my coding abilities, thought process and even an opportunity to show a little byte of my personality and char ;)

# Interesting Knowledge 
#### Named pipes
```bash
prw-rw-r-- 1 ichiheb ichiheb    0 Sep 28 12:55 output1
# p named pipes or FIFO file. Keeps "running" until "read"
```

#### Binary files: double little endian
```python
import struct
struct.pack('<d', 5707)
# < little endian
# d double 8 bytes
```
