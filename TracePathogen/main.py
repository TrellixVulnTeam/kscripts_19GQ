# @CreateTime       : 2022/04/26
# @Author           : mengxf
# @version          : v1.0
# @LastModified     : 2022/05/13

import sys
import logging
from lib import general
from lib import Trace


# 设置运行日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(asctime)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
)

# 命令行参数
args = general.get_args()

# 判断并运行流程
if args.subparser_name == "wgs":
    pipe = Trace.PhyloWGS(infile=args.infile)
    pipe.execute()
elif args.subparser_name == "snp":
    pipe = Trace.PhyloSNP(infile=args.infile)
    pipe.execute()
elif args.subparser_name == "core":
    pipe = Trace.PhyloCORE(infile=args.infile)
    pipe.execute()
else:
    logging.error("不存在的情况")
