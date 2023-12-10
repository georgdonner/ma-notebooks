import re, csv, time
from concurrent.futures import TimeoutError
import multiprocessing as mp
from pebble import ProcessPool

from steckbriefe.calc.steckbrief import calculate_steckbrief
from steckbriefe.fields import all_fields

def get_steckbrief(fn_str, queue):
    steckbrief = calculate_steckbrief(fn_str)
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
    timeout = 30
    depth = 2
    write_filename = f'steckbriefe{depth}_ext.csv'
    start = time.perf_counter()

    manager = mp.Manager()
    queue = manager.Queue()
    queue_process = mp.Process(target=queue_listener, args=(queue, write_filename))
    queue_process.start()

    with open(write_filename, 'w', newline='') as writefile:
        writer = csv.DictWriter(writefile, fieldnames = all_fields)
        writer.writeheader()

    with ProcessPool() as pool:
        with open(f'uniques_ext_depth{depth}.csv', 'r') as readfile:
            for line in readfile:
                if line != 'k':
                    line = re.sub('\s+', '', line)
                    future = pool.schedule(get_steckbrief, (line, queue), timeout=timeout)
                    future.add_done_callback(done)
        pool.close()
        pool.join()
        queue_process.kill()

    print(f'Took {time.perf_counter() - start} seconds in total')
