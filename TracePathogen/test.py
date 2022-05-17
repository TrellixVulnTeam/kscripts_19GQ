import logging
from lib import Trace
from lib import general

# 设置运行日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(asctime)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
)

pipe = Trace.PhyloSNPFQ(infile="/sdbb/bioinfor/mengxf/Project/5.trace_pathogen/rawdata/snp_fastq/trace_wgs_input.yaml")
pipe.execute()
