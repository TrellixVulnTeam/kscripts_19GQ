#!/usr/bin/env python

from ast import Load
import os
import sys
import subprocess
import argparse
import multiprocessing
import yaml


# Need
# 1.result dir, 2.sample path table, 3.sars_cov2.yaml

def getargs():
    parser = argparse.ArgumentParser()
    parser.description = "Parallel for sars_cov2_pipe.sh"
    parser.add_argument("-S", "--sample_table", type=str, 
                        help="Sample path table, example: S1\\tS1.R1.fq1,S1.R1.fq2", required=True)
    parser.add_argument("-R", "--result_dir", type=str, help="Library results directory.", required=True)
    parser.add_argument("--sars2_config", type=str, help="Sars-Cov-2 yaml configure file.")
    args = parser.parse_args()
    return args

# run single sample sars_cov2_pipe function
def run_single(xtuple):
    name, rawdata = xtuple
    cml = "bash {scripts}/sars_cov2_pipe.sh {name} {rawdata} {result}".format(
        scripts=scripts_dir,
        name=name,
        rawdata=rawdata,
        result=result_dir
    )
    runres = subprocess.run(cml, shell=True, capture_output=True, check=True, encoding="utf-8", env=sars_cov2_dict)
    ofile = "{}/logs/{}.sars_cov2_pipe.o".format(result_dir, name)
    efile = "{}/logs/{}.sars_cov2_pipe.e".format(result_dir, name)
    with open(ofile, "wt", encoding="utf-8", newline="") as gh:
        gh.write(runres.stdout)
    with open(efile, "wt", encoding="utf-8", newline="") as gh:
        gh.write(runres.stderr)
    # print(cml)

# main
# parameters
global result_dir, scripts_dir, sars_cov2_dict
args                = getargs()
sample_path_file    = args.sample_table
result_dir          = args.result_dir
os.makedirs(result_dir + os.sep + "logs", exist_ok=True)
#~ locate scripts path & sars_cov2 parameter yaml file
utils_dir           = sys.path[0]
scripts_dir         = os.path.dirname(utils_dir)
if args.sars2_config:
    sars_cov2_yaml  = args.sars2_config
else:
    sars_cov2_yaml  = scripts_dir + os.sep + "libs/sars_cov2.yaml"
#~ check parameters
assert os.path.exists(sample_path_file), "ERROR - parallel.py - <sample_path_table> not exists!"
assert os.path.exists(sars_cov2_yaml), "ERROR - parallel.py - <sars_cov2_yaml> not exists!"
# sars_cov2 dictionary
with open(sars_cov2_yaml, "rt") as fh:
    sars_cov2_dict = yaml.load(fh, Loader=yaml.BaseLoader)
sars_cov2_dict["SCRIPTS_PATH"] = scripts_dir

# function arguments tuples list
run_single_args = list()
with open(sample_path_file) as fh:
    for line in fh:
        ltuple = tuple(line.strip().split("\t"))
        run_single_args.append(ltuple)

# multiprocessing
with multiprocessing.Pool(int(sars_cov2_dict["JOBS"])) as ph:
    ph.map(run_single, run_single_args)
