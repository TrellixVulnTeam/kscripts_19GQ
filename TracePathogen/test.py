import logging
from pkgs import Trace

# 设置运行日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(asctime)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
)

pipe = Trace.phyloCORE(infile="/sdbb/bioinfor/mengxf/Project/5.trace_pathogen/rawdata/core/Blastomyces_dermatitidis/trace_core_input.yaml")
pipe.execute()
