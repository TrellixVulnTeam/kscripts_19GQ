#!/home/ionadmin/software/miniconda3/envs/data_analysis/bin/python
# -*- coding:utf-8 -*-

import os, sys
import argparse
from subprocess import run
from multiprocessing import Pool
from pprint import pprint


def execute_linux_commandline(cmd):
    print("Command Line: " + cmd)
    a = run(cmd, shell=True, check=True, encoding='utf-8')
    print(a.returncode)

def main(shell_scripts, processes):
    with open(shell_scripts, 'rt', encoding='utf-8') as f:
        cmd_list = [line.strip() for line in f]

    pool = Pool(processes)
    pool.map_async(execute_linux_commandline, cmd_list)
    print('Waiting for all subprocesses done...')
    pool.close()
    pool.join()
    print('All subprocesses done.')

def get_argparses():
    parser = argparse.ArgumentParser()
    parser.description = 'Parallel Program for execute Linux CommandLine!!'
    parser.add_argument('shell_scripts', type=str, help='所有并行脚本的总 shell 文件')
    parser.add_argument('-p', '--processes', default=4, type=int, help='并行的程序数，也可以当作核心数 (default: 4)')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_argparses()
    shell_scripts = args.shell_scripts
    processes = args.processes
    main(shell_scripts, processes)
