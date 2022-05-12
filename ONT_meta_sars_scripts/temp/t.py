#!/usr/bin/env python

import sys
import os
import subprocess
import yaml


# Metagenomics Sars-Cov-2 analysis environments
env_yaml = "/sdbb/bioinfor/mengxf/Project/4.nanopore_pipe/metagenomics_sars_scripts/libs/meta_sars2_ont.yaml"
with open(env_yaml) as fh:
    env_dict = yaml.safe_load(fh)

# main
cmd = "bash {}".format("/sdbb/bioinfor/mengxf/Project/4.nanopore_pipe/metagenomics_sars_scripts/sars_cov2_meta_ont.sh")
s = subprocess.run(cmd, shell=True, capture_output=True, check=True, encoding='utf-8', env=env_dict)
ofile = "results/logs/barcode01.sars_cov2_meta_ont.o"
efile = "results/logs/barcode01.sars_cov2_meta_ont.e"
with open(ofile, "w", encoding="utf-8", newline="") as gh:
    gh.write(s.stdout)
with open(efile, "w", encoding="utf-8", newline="") as gh:
    gh.write(s.stderr)
