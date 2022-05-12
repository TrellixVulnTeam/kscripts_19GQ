# TracePathogen
## 介绍
溯源分析流程，输入FASTA，输出进化溯源结果报告。  
流程分为三条路线：  
- 核心基因 
- 全基因组SNP
- 全基因组多序列比对  

## 使用方法
#### 获取帮助
```
python main.py -h
```
全局参数:  
```
-i, --infile INFILE     输入样本信息YAML文件  
```


#### 应用示例
```
python main.py wgs -i input.yaml
python main.py snp -i input.yaml
python main.py core -i input.yaml
```
