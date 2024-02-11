import argparse, re, csv, time
from concurrent.futures import TimeoutError
import multiprocessing as mp
from pebble import ProcessPool

from steckbriefe.calc.steckbrief import calculate_steckbrief
from steckbriefe.fields import all_fields
from config import Config

def get_steckbrief(fn_str, queue, serialize):
    steckbrief = calculate_steckbrief(fn_str, serialize=serialize)
    print(fn_str, steckbrief['computation_seconds'])
    queue.put(steckbrief)
    return steckbrief

def queue_listener(queue, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        while True:
            payload = queue.get()
            writer = csv.DictWriter(file, fieldnames = all_fields)
            writer.writerow(payload)
            file.flush()

def done(future):
    try:
        future.result()
    except TimeoutError as error:
        print('Function timed out')
    except Exception as error:
        print('Function raised %s' % error)
        print(error.traceback)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("steckbrief_generator")
    parser.add_argument('input', help='input file with expressions')
    parser.add_argument('-t', '--timeout', help='timeout per function in seconds', default=10, type=int)
    parser.add_argument('-o', '--output', help='output file for steckbriefe', default='steckbriefe.csv', type=str)
    parser.add_argument('-s', '--serialize', help='method of serialization', default='sympy', type=str, choices=['sympy', 'mathml', 'latex'])
    args = parser.parse_args()
    
    start = time.perf_counter()

    manager = mp.Manager()
    queue = manager.Queue()
    queue_process = mp.Process(target=queue_listener, args=(queue, args.output))
    queue_process.start()

    with open(args.output, 'w', newline='') as writefile:
        writer = csv.DictWriter(writefile, fieldnames = all_fields)
        writer.writeheader()

    with ProcessPool() as pool:
        with open(args.input, 'r') as readfile:
            for index, line in enumerate(readfile):
                line = re.sub('\s+', '', line)
                future = pool.schedule(get_steckbrief, (line, queue, args.serialize), timeout=args.timeout)
                future.add_done_callback(done)
        pool.close()
        pool.join()
        queue_process.kill()

    print(f'Took {time.perf_counter() - start} seconds in total')
