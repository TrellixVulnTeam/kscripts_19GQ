#!/usr/bin/env python

import os
import re
import sys
from openpyxl import Workbook


def parse_vcfinfo(info):
    """return INFO dict. DP,AC,AF..."""
    info_dict = dict()
    info_list = info.strip().split(";")
    for il in info_list:
        il_list = il.strip().split("=")
        info_dict[il_list[0]] = il_list[1]
    return info_dict

def parse_header_ANN(annline):
    """return ANN position dict. Allele, Annotation, Annotation_Impact, Gene_Name..."""
    pattern = re.compile("Functional annotations: \'(.*?)\' \">", re.S)
    annres = re.findall(pattern, annline)[0]
    header_list = annres.strip().split(" | ")
    annpos_dict = {en[1]: en[0] for en in enumerate(header_list)}
    return annpos_dict

def extract_anno_snpeff(ANN, annpos_dict):
    """
    extract HGVS annotation information from snpEff VCF results, column 'INFO'.
    return [Gene_Name, HGVS.c, HGVS.p]
    """
    ann_list = ANN.strip().split(",")
    # choose position 1 items
    annitem_list = ann_list[0].strip().split("|")
    genename = annitem_list[annpos_dict["Gene_Name"]]
    hgvsc = annitem_list[annpos_dict["HGVS.c"]]
    hgvsp = annitem_list[annpos_dict["HGVS.p"]]
    return [genename, hgvsc, hgvsp]

def tsv2xlsx(tfile):
    outfile = re.sub(r".txt|.tsv|.xls|.csv", ".xlsx", tfile)
    wb = Workbook()
    ws = wb.active
    with open(tfile, "rt") as fh:
        for line in fh:
            ws.append(line.strip().split("\t"))
    wb.save(outfile)

def vcf2table(vfile:str):
    outfile = os.path.dirname(vfile) + os.sep + "trans.txt"
    with open(vfile) as f, open(outfile, "wt", encoding="utf-8", newline="") as g:
        g.write("参考基因组\t变异位置\t参考碱基\t替换碱基\t基因名\tDNA变异\t氨基酸变异\t变异深度\n")
        for line in f:
            if line.startswith("##"):
                if "ID=ANN" in line:
                    annpos_dict = parse_header_ANN(line)
                continue
            elif line.startswith("#CHROM"):
                header_list         = line.strip().split("\t")
                header_dict         = {hie[1]: hie[0] for hie in enumerate(header_list)}
            else:
                linelist    = line.strip().split("\t")
                chrom       = linelist[header_dict["#CHROM"]]
                pos         = linelist[header_dict["POS"]]
                ref         = linelist[header_dict["REF"]]
                alt         = linelist[header_dict["ALT"]]
                qual        = float(linelist[header_dict["QUAL"]])
                info        = linelist[header_dict["INFO"]]
                info_dict   = parse_vcfinfo(info)
                ann3_list   = extract_anno_snpeff(info_dict["ANN"], annpos_dict)
                if "DP" not in info_dict:
                    print("WARNING - vcf2table.py - {}".format(info))
                    continue
                # filter quality 1
                elif qual < 1:
                    continue
                else:
                    depth   = format(int(info_dict["DP"]), ",")
                    outlist = [chrom, pos, ref, alt] + ann3_list + [depth]
                    g.write("\t".join(outlist) + "\n")

# main
if __name__ == "__main__":
    assert len(sys.argv) == 2, "ERROR - vcf2table.py - Just need 1 Arguments, VCF!"
    assert os.path.exists(sys.argv[1]), "ERROR - vcf2table.py - VCF not exists!"
    vcf_file = sys.argv[1]
    vcf2table(vcf_file)
    tsv2xlsx(os.path.dirname(vcf_file) + os.sep + "trans.txt")
