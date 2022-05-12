#!/usr/bin/env python

import os
import sys
import json
from collections import defaultdict


def fastp_json2table(fpjson:str):
    """
    Translate fastp .json to qc table.
    Input: fastp.json
    Output: fastq_stats.txt
    """
    fastp_json = fpjson
    out_file = os.path.dirname(fastp_json) + os.sep + "fastq_stats.txt"

    with open(fastp_json) as f:
        fastp_dict = json.load(f)

    out_dict = defaultdict(dict)
    # before filtering
    out_dict["before"]["reads"]     = format(fastp_dict["summary"]["before_filtering"]["total_reads"], ",")
    out_dict["before"]["bases"]     = format(fastp_dict["summary"]["before_filtering"]["total_bases"], ",")
    out_dict["before"]["Q30"]       = "{:.2%}".format(fastp_dict["summary"]["before_filtering"]["q30_rate"])
    out_dict["before"]["GC"]        = "{:.2%}".format(fastp_dict["summary"]["before_filtering"]["gc_content"])
    # out_dict["before"]["adapter"]   = "{:.2%}".format(fastp_dict["adapter_cutting"]["adapter_trimmed_bases"] / \
    #     fastp_dict["summary"]["before_filtering"]["total_bases"])
    # after filtering
    out_dict["after"]["reads"]     = format(fastp_dict["summary"]["after_filtering"]["total_reads"], ",")
    out_dict["after"]["bases"]     = format(fastp_dict["summary"]["after_filtering"]["total_bases"], ",")
    out_dict["after"]["Q30"]       = "{:.2%}".format(fastp_dict["summary"]["after_filtering"]["q30_rate"])
    out_dict["after"]["GC"]        = "{:.2%}".format(fastp_dict["summary"]["after_filtering"]["gc_content"])
    # out_dict["after"]["adapter"]   = "-"
    # out
    header_list = ["", "总序列数", "总碱基数", "Q30", "GC含量"]
    ba_dict = {"before": "过滤前", "after": "过滤后"}
    outheaderlist = ["reads", "bases", "Q30", "GC"]
    with open(out_file, "wt", encoding="utf-8", newline="") as g:
        g.write("\t".join(header_list) + "\n")
        for ab in ["before", "after"]:
            outlist = [out_dict[ab][ohl] for ohl in outheaderlist]
            outlist.insert(0, ba_dict[ab])
            g.write("\t".join(outlist) + "\n")

if __name__ == "__main__":
    assert len(sys.argv) == 2, "ERROR - fastp_json2table.py - Just need 1 Arguments, FastpJSON!"
    assert os.path.exists(sys.argv[1]), "ERROR - fastp_json2table.py - FastpJSON not exists!"
    fastp_json = sys.argv[1]
    fastp_json2table(fastp_json)
