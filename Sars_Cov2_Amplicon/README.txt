[2022.03.01 更新]
1. 加入 snpEff 变异注释
2. 沈博建议流程在 temp 文件中

[2022.02.23 重大更新]
1. 加入 ivar trim 流程，重要参数 -e
2. 开发测试沈杨博士的去 primer 方法
3. mask reference 细节，
    bedtools 统计低深度区域（length>20bp），使用低深度区域 mask reference，基于 masked reference
   使用 freebayes 进行 call variant，使用上面得到的 vcf 构建 consensus

[2022.02.17 重大更新]
1. 提高覆盖度阈值，
    a.低覆盖区域屏蔽(<10x)
    b.freebayes min alt count > 10x min alt fraction > 0.2
2. fastp 参数，增加 Q 值及滑窗剪切参数

[2022.02.11 重大更新]
1. .tsv 后缀改为 .xls
2. 进化树图优化，单图长度
3. *删除单样本流程中的 InDelRealign 步骤（多样本出现 JAVA 内存不足报错，考虑 gatk3 版本较老，放弃改步骤）
4. cov lineage 结果表格 .xlsx

[2022.02.07 更新]
1. 北京疾控潘阳老师要求 concensus fastq
2. 进化树图调整高度，样本多太挤了
3. pangolin trans 表格 tsv 后缀改成 xls

[2022.01.27 更新]
1. 报告细节优化，表头替换为中文，并解释；
2. 删除不必要的说明描述?

[2022.01.21 更新]
1. 报告系统升级为公卫生信组统一的 perl 报告框架
2. sars_cov2_pipe.sh: trim_galore 替换为 fastp, 需要过滤前后质控信息；fastp json 结果转成 table 格式
3. genome_coverage.R 加入新冠基因组层数
4. 重新整理 VCF 输出
5. pangolin 结果优化整理脚本，加入中文配置文件
