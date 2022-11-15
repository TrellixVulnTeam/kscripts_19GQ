# Sars_Cov2_Amplicon

## TODO


## 更新内容
- [x] [221101] 流程优化  
    选项加入"选择引物软件"  
- [221031] 流程优化  
    段落icon优化, 过滤前后fastqc  
- [221009] 流程优化  
    - haplotypecaller 改回 freebayes
    - 二聚体长度, 引物去除，1)fastp参数；2)可选去引物软件; 3)质控数据补充; 4)软剪切硬剪切参数;
                            5)pangolin加线程; 6)upload文件选择; 7)原始FQ质控表格统一  
- [220928] 报告结果优化  
    1.fastqc,bam文件目录给链接; 2.变异表格,变异深度/测序深度/变异频率  
- [220801] 发现一分钟的力量  
    fastqc和genome_coverage.R挂后台运行加速  
- [220628] 速度提升  
    1)删除进化树; 2)freebayes换成gatk HaplotypeCaller, gatk过滤使用python加快速度  
- [220613] python 重写 Sars_Cov2_Amplicon 流程  
    1)新冠全球库; 2)支持单端FASTQ输入   
