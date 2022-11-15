# kTrimPrimer
## 介绍  
自编去引物脚本  
- `FQTrimPrimer.py` 支持单端双端FQ数据去引物,双端数据合并pair-end为单端,然后继续分析  
- `SAMTrimPrimer.py` SAM数据去引物  

## 更新
- [221010] 增加部分注释  
- [221011] 软件逻辑优化   
    1)考虑软剪切问题, seq,qual按照CIGAR S标识截断, 2)短read过滤,原始数据和剪切的数据都要在这个阈值内
