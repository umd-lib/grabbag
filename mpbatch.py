#!/usr/bin/env python3

from multiprocessing import Pool
from subprocess import run, CalledProcessError
from argparse import ArgumentParser, FileType
from os import cpu_count
from time import time, gmtime, strftime
import logging
import sys

'''
Run multiple subprocesses in the background. Report their results in an
orderly fashion as they finish. Exit when the last subprocess has completed.
'''

logger = logging.getLogger('mpbatch')

DATE = "%a, %d %b %Y %H:%M:%S +0000"


class Command():
    ''' The external command to execute as a subprocess. '''

    def __init__(self, args):
        self.args = args
        self.start = None
        self.stop = None
        self.returncode = None
        self.stdout = None
        self.stderr = None


def execute(command):
    ''' Execute a single command in a subprocess and collect the results. '''

    # Execute the command in a subprocess and record start and stop time
    command.start = time()
    logger.debug(f'Starting {command.args}')

    result = run(command.args, capture_output=True)

    command.stop = time()

    # Get return values from the subprocess
    command.returncode = result.returncode
    command.stdout = result.stdout
    command.stderr = result.stderr

    return command


def elapsed(e):
    ''' Return elapsed time in hh:mm:ss.mmm format. '''
    e = int(e * 1000)
    e, mil = divmod(e, 1000)
    e, sec = divmod(e, 60)
    hr, min = divmod(e, 60)

    return(f'{hr:02d}:{min:02d}:{sec:02d}.{mil:03d}')


if __name__ == '__main__':

    # Setup command line arguments
    parser = ArgumentParser()

    parser.add_argument("-n", "--threads",
                        type=int, default=0,
                        help='''number of simultaneous threads; default is
 os.cpu_count() - 1''')

    parser.add_argument("-j", "--json-logfile",
                        type=FileType('w', encoding='UTF-8'),
                        help="json format log file")

    parser.add_argument("-r", "--raw", action="store_true",
                        help='''commands are tab delimited list of subprocess
 args; default is single argument to /bin/bash -c''')

    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debug logging")

    # Process command line arguments
    args = parser.parse_args()

    # Logging
    logger.addHandler(logging.StreamHandler())
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Threads
    if args.threads == 0:
        cpus = cpu_count()
        args.threads = 1 if cpus is None else cpus - 1

    logger.debug(f'''Arguments:
  threads={args.threads}
  json-logfile={args.json_logfile.name if args.json_logfile else None}
  raw={args.raw}
  debug={args.debug}''')

    # Read the input commands to run
    commands = []
    for line in sys.stdin.readlines():
        line = line.strip()
        if line.startswith('#') or line == "":
            continue
        if args.raw:
            cmd = Command(line.split('\t'))
        else:
            cmd = Command(['/bin/bash', '-c', line])
        commands.append(cmd)

    # Begin execution
    returncode = 0
    start = time()
    cumulative = 0

    logger.debug(f'Beginning execution of {len(commands)} command(s)')

    with Pool(processes=args.threads) as pool:
        for cmd in pool.imap(execute, commands):
            logger.debug("===")
            logger.info(f'''Completed {cmd.args} with
 return code {cmd.returncode}''')

            logger.debug(f'  Started:   {strftime(DATE, gmtime(cmd.start))}')
            logger.debug(f'  Completed: {strftime(DATE, gmtime(cmd.stop))}')
            logger.debug(f'  Elapsed:   {elapsed(cmd.stop - cmd.start)}')
            logger.debug(f'  Stdout:    {cmd.stdout}')
            logger.debug(f'  Stderr:    {cmd.stderr}')

            if cmd.returncode != 0:
                returncode = 1

            cumulative += cmd.stop - cmd.start

    stop = time()

    logger.debug("===")
    logger.debug("Summary:")
    logger.debug(f'  Started:    {strftime(DATE, gmtime(cmd.start))}')
    logger.debug(f'  Completed:  {strftime(DATE, gmtime(cmd.stop))}')
    logger.debug(f'  Elapsed:    {elapsed(stop - start)}')
    logger.debug(f'  Cumulative: {elapsed(cumulative)}')
