import os
import sys
import yaml
import logging
import re
from functools import partial
from glob import glob
import itertools
import time
from subprocess import run
from subprocess import PIPE
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from lib import general
from lib.general import MyRule, MyRuleS
from lib.general import MyLoggingInfo
from lib.general import link2upload
import pdb


# 给库添加日志
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler)


class PhyloWGS():
    """
    溯源进化树 - 全基因组多序列比对法
    [infile]    输入YAML文件
    """
    def __init__(self, infile):
        self.dir_bin = sys.path[0] + os.sep + "bin"
        self.dir_config = sys.path[0] + os.sep + "conf"
        self.assign_soft_dict()
        self.assign_parameters()
        self.yaml_input = infile
        self.assign_base_info()
        self.mylog = MyLoggingInfo()
    
    def assign_soft_dict(self):
        """软件路径"""
        logging.info("读取软件配置文件")
        with open(self.dir_config + os.sep + "software.yml", "rt") as fh:
            self.dict_soft = yaml.load(fh, Loader=yaml.SafeLoader)

    def assign_parameters(self):
        """软件配置相关类参数"""
        logging.info("读取软件参数配置文件")
        with open(self.dir_config + os.sep + "parameters.yaml", "rt") as fh:
            self.dict_params = yaml.load(fh, Loader=yaml.SafeLoader)
        self.thread = self.dict_params["thread"]
        self.parallel = self.dict_params["parallel"]

    def assign_base_info(self):
        """基础信息"""
        logging.info("读取输入配置文件")
        with open(self.yaml_input, "rt") as fh:
            self.dict_input = yaml.load(fh, Loader=yaml.SafeLoader)
        self.library = self.dict_input["library"]
        self.outdir = self.dict_input["result_dir"] + os.sep + self.library
        self.dict_sample = self.dict_input['samples']

    def make_result_dir(self, dirs:list):
        """创建结果目录,Upload在创建一遍"""
        self.mylog.info("创建结果目录")
        # 数字开头的目录才上传到Upload目录
        uploads_release = [dd for dd in dirs if re.match("^\d\.", dd)]
        uploads = list(map(lambda x:f"Upload/{x}", uploads_release))
        general.mymakedirs(dirs+uploads, self.outdir)

    def merge_fasta(self):
        self.mylog.info("合并FASTA文件")
        self.fasta_merged = f"{self.outdir}/1.MergeFA/{self.library}.fa"
        general.merge_wgs_fasta(mfasta=self.fasta_merged, dict_sample=self.dict_sample)

    def msa(self):
        self.mylog.info("MSA 多序列比对")
        self.rule_msa = MyRule(
            software    = self.dict_soft["mafft"],
            infile      = self.fasta_merged,
            outfile     = f"{self.outdir}/2.MSA/{self.library}.aln.fa",
            log         = f"{self.outdir}/Logs/{self.library}.mafft",
            params      = "--auto --maxiterate 1000",
            thread      = self.thread,
            ptn         = "{software} --thread {thread} {params} {infile} > {outfile}"
        )
    
    def build_tree(self):
        self.mylog.info("进化树构建")
        # fasttree 建树
        self.rule_phylo = MyRule(
            software    = self.dict_soft["fasttree"],
            infile      = self.rule_msa.outfile,
            outfile     = f"{self.outdir}/3.PhylogeneticTree/{self.library}.tre",
            log         = f"{self.outdir}/Logs/{self.library}.fasttree",
            params      = "-nt",
            ptn         = "{software} {params} {infile} > {outfile}"
        )
        # R ggtree 作图
        self.rule_rtree = MyRule(
            software    = f"{self.dict_soft['Rscript']} {self.dir_bin}/tree.R",
            infile      = self.rule_phylo.outfile,
            log         = f"{self.outdir}/Logs/{self.library}.rtree",
            ptn         = "{software} {infile}"
        )
        general.magick_dir(
            dir_fig=f"{self.outdir}/3.PhylogeneticTree",
            path_magick=self.dict_soft["magick"],
            suffix_from="svg",
            suffix_to="png"
        )

    def upload(self):
        self.mylog.info("上传数据")
        tree_figs = ["rectangular", "rectangular_bl", "slanted", "circular"]
        link2upload(self.fasta_merged, f"{self.outdir}/Upload/1.MergeFA")
        link2upload(self.rule_msa.outfile, f"{self.outdir}/Upload/2.MSA")
        link2upload(self.rule_phylo.outfile, f"{self.outdir}/Upload/3.PhylogeneticTree")
        # 进化树图软连接到Upload目录
        mylink = partial(link2upload, dir_upload=f"{self.outdir}/Upload/3.PhylogeneticTree")
        for tf in tree_figs:
            mylink(f"{self.outdir}/3.PhylogeneticTree/{tf}.png")
            mylink(f"{self.outdir}/3.PhylogeneticTree/{tf}.svg")

    def report(self):
        self.mylog.info("生成报告")
        self.rule_report = MyRule(
            software=f"{self.dict_soft['perl']} {self.dir_bin}/report.pl",
            infile=f"{self.outdir}/Upload",
            log=f"{self.outdir}/Logs/{self.library}.report",
            params="wgs",
            ptn="{software} {infile} {params}"
        )

    def zip_result(self):
        general.zip_dir(f"{self.outdir}/Upload", zip_dst=f"{self.outdir}/{self.library}.zip")

    def execute(self):
        logging.info("溯源进化树>全基因组多序列比对流程: 开始分析!")
        self.make_result_dir(["1.MergeFA", "2.MSA", "3.PhylogeneticTree", "Logs"])
        self.merge_fasta()
        self.msa()
        self.build_tree()
        self.upload()
        self.report()
        self.zip_result()
        logging.info("溯源进化树>全基因组多序列比对流程: 分析完成!")


class PhyloSNP(PhyloWGS):
    """
    溯源进化树 - SNP
    FASTA 输入
    [infile]    输入YAML文件
    """
    def __init__(self, infile):
        super().__init__(infile)
    
    def assign_base_info(self):
        """基础信息"""
        super().assign_base_info()
        self.reference = self.dict_input["reference"]
        
    def snippy_multiple(self):
        """snippy多样本并行"""
        # snippy输出需要: 1.output输出目录; 2.prefix样本前缀
        # 后面"PE reads fastq"也用这个办法写输入
        self.mylog.info("变异检测流程")
        _infiles, _logs, _outfiles = list(), list(), list()
        for samp in self.dict_sample:
            _infiles.append(self.dict_sample[samp])
            _logs.append(f"{self.outdir}/Logs/{samp}.snippy")
            dir_tmp = f"{self.outdir}/1.Variants/{samp}"
            _outfiles.append(f"--outdir {dir_tmp} --prefix {samp}")
        # rules
        self.rules_snippy = MyRuleS(
            software=self.dict_soft["snippy"],
            infiles=_infiles,
            outfiles=_outfiles,
            logs=_logs,    
            params=f"--force --ref {self.reference}",
            thread=self.thread,
            parallel=self.parallel,
            ptn="{software} --cpus {thread} {params} {outfile} --ctgs {infile}"
        )

    def merge_vcf(self):
        self.mylog.info("合并变异文件")
        os.makedirs(f"{self.outdir}/2.MergeVCF", exist_ok=True)
        file_merge_vcf = f"{self.outdir}/2.MergeVCF/vcf_list.txt"
        with open(file_merge_vcf, "wt", encoding="utf-8", newline="") as gh:
            for samp in self.dict_sample.keys():
                gh.write( f"{self.outdir}/1.Variants/{samp}/{samp}.vcf.gz\n")
        # rule snippy
        self.rule_mergevcf = MyRule(
            software=self.dict_soft["bcftools"],
            infile=file_merge_vcf,
            outfile=f"{self.outdir}/2.MergeVCF/{self.library}.vcf",
            log=f"{self.outdir}/Logs/{self.library}.merge_vcf",
            params="-m snps -f PASS,. --force-samples --output-type v",
            ptn="{software} merge {params} --file-list {infile} -o {outfile}"
        )

    def build_tree(self):
        self.mylog.info("进化树构建")
        # 1.vcf转phy
        self.rule_vcf2phy = MyRule(
            software=f"{self.dict_soft['python']} {self.dir_bin}/vcf2phylip.py",
            infile=self.rule_mergevcf.outfile,
            outfile=f"{self.outdir}/3.PhylogeneticTree",
            params="-m 1",
            log=f"{self.outdir}/Logs/{self.library}.vcf2phy",
            ptn="{software} {params} -i {infile} --output-folder {outfile}"
        )
        # 2.fasttree
        self.rule_fasttree = MyRule(
            software=self.dict_soft["fasttree"],
            infile=f"{self.outdir}/3.PhylogeneticTree/{self.library}.min1.phy",
            outfile=f"{self.outdir}/3.PhylogeneticTree/{self.library}.tre",
            log=f"{self.outdir}/Logs/{self.library}.fasttree",
            params="-nt",
            ptn="{software} {params} {infile} > {outfile}"
        )
        # 3.r-ggtree
        self.rule_rtree = MyRule(
            software=f"{self.dict_soft['Rscript']} {self.dir_bin}/tree.R",
            infile=self.rule_fasttree.outfile,
            log=f"{self.outdir}/Logs/{self.library}.rtree",
            ptn="{software} {infile}",
        )
        general.magick_dir(
            dir_fig=f"{self.outdir}/3.PhylogeneticTree",
            path_magick=self.dict_soft["magick"],
            suffix_from="svg",
            suffix_to="png"
        )

    def remove_intermedia(self):
        """删除中间文件"""
        general.delete_wildcard_path(f"{self.outdir}/1.Variants/*/ref*")

    def upload(self):
        self.mylog.info("上传数据")
        tree_figs = ["rectangular", "rectangular_bl", "slanted", "circular"]
        link2upload(self.rule_mergevcf.outfile, f"{self.outdir}/Upload/2.MergeVCF")
        link2upload(self.rule_fasttree.outfile, f"{self.outdir}/Upload/3.PhylogeneticTree")
        # 进化树图软连接到Upload目录
        mylink = partial(link2upload, dir_upload=f"{self.outdir}/Upload/3.PhylogeneticTree")
        for tf in tree_figs:
            mylink(f"{self.outdir}/3.PhylogeneticTree/{tf}.png")
            mylink(f"{self.outdir}/3.PhylogeneticTree/{tf}.svg")

    def report(self):
        self.mylog.info("生成报告")
        self.rule_report = MyRule(
            software=f"{self.dict_soft['perl']} {self.dir_bin}/report.pl",
            infile=f"{self.outdir}/Upload",
            log=f"{self.outdir}/Logs/{self.library}.report",
            params="snp",
            ptn="{software} {infile} {params}"
        )

    def execute(self):
        logging.info("溯源进化树>全基因组SNP流程: 开始分析!")
        self.make_result_dir(["1.Variants", "2.MergeVCF", "3.PhylogeneticTree", "Logs"])
        self.snippy_multiple()
        self.merge_vcf()
        self.build_tree()
        self.remove_intermedia()
        self.upload()
        self.report()
        self.zip_result()
        logging.info("溯源进化树>全基因组SNP流程: 分析完成!")


class PhyloCORE(PhyloWGS):
    """
    溯源进化树 - 核心基因
    [infile]    输入YAML文件
    """
    def __init__(self, infile):
        super().__init__(infile)
        # 最终输出单拷贝基因合并的序列
        self.file_supergene = f"{self.outdir}/1.Orthologue/{self.library}_supergene.faa"

    def assign_base_info(self):
        super().assign_base_info()
        self.kindom = self.dict_input["kindom"]

    def format_fasta_multi(self):
        self.mylog.info("格式化输入")
        self.dict_sample_formatted = dict()
        for name,path in self.dict_sample.items():
            outfile = f"{self.outdir}/FormatFASTA/{name}.fna"
            general.format_fasta(name, path, outfile)
            self.dict_sample_formatted[name] = outfile
    
    def run_prodigal(self):
        """gene_predict: 细菌病毒用prodigal并行"""
        _infiles, _logs, _outfiles = list(), list(), list()
        for name, fasta in self.dict_sample_formatted.items():
            _infiles.append(fasta)
            _logs.append(f"{self.outdir}/Logs/{name}.genepredict")
            _outfiles.append(f"-a {self.outdir}/1.Orthologue/GenePrediction/{name}.faa "
            f"-o {self.outdir}/1.Orthologue/GenePrediction/{name}.genes")

        # rule: prodigal -i my.genome.fna -o my.genes -a my.proteins.faa
        self.rule_genepred = MyRuleS(
            software=self.dict_soft["prodigal"],
            infiles=_infiles,
            logs=_logs,
            outfiles=_outfiles,
            parallel=self.parallel,
            ptn="{software} -i {infile} {outfile}"
        )

    def run_genemark(self):
        """gene_predict: 真菌用genemark并行"""
        _infiles, _logs, _outfiles = list(), list(), list()
        for name, fasta in self.dict_sample_formatted.items():
            _infiles.append(fasta)
            _logs.append(f"{self.outdir}/Logs/{name}.genepredict")
            _outfiles.append(f"-A {self.outdir}/1.Orthologue/GenePrediction/{name}.faa "
            f"-o {self.outdir}/1.Orthologue/GenePrediction/{name}.genes "
            f"-D {self.outdir}/1.Orthologue/GenePrediction/{name}.fna")
        # rule genemark
        self.rule_genepred = MyRuleS(
            software=self.dict_soft["gmhmmp"],
            infiles=_infiles,
            outfiles=_outfiles,
            logs=_logs,
            parallel=self.parallel,
            params=f"-a -d -f G -m {self.dict_params['MetaGeneMarkMod']}",
            ptn="{software} {params} {outfile} {infile}"
        )
        # 格式化 faa 头, 原文件修改
        for name in self.dict_sample:
            with open(f"{self.outdir}/1.Orthologue/GenePrediction/{name}.faa", "rt") as fh:
                outlines = ""
                for line in fh:
                    if line.startswith(">"):
                        _list = line.strip().split("\t")
                        outlines += f"{_list[1]}_{_list[0]}\n"
                    else:
                        outlines += line
            with open(f"{self.outdir}/1.Orthologue/GenePrediction/{name}.faa", 
            "wt", encoding="utf-8", newline="") as gh:
                gh.write(outlines)

    def genepred_lenfilter(self):
        """预测基因长度筛选，蛋白长度>33bp(核酸长度>100bp)"""
        _infiles, _logs, _outfiles = list(), list(), list()
        for name in self.dict_sample:
            _infiles.append(f"{self.outdir}/1.Orthologue/GenePrediction/{name}.faa")
            _outfiles.append(f"{self.outdir}/1.Orthologue/GenePrediction/{name}_L33.faa")
            _logs.append(f"{self.outdir}/Logs/{name}.gene_predict_seqtk_seq")
        self.rules_genepred_lenfilter = MyRuleS(
            software=self.dict_soft["seqtk"],
            infiles=_infiles,
            outfiles=_outfiles,
            logs=_logs,
            params="-L 33",
            parallel=self.parallel,
            ptn="{software} seq {params} {infile} > {outfile}"
        )

    def gene_predict(self):
        """分病毒细菌和真菌两种方向"""
        self.mylog.info("基因预测")
        os.makedirs(f"{self.outdir}/1.Orthologue/GenePrediction", exist_ok=True)
        if self.kindom in ["bacteria", "viruses"]:
            self.run_prodigal()
        elif self.kindom == "fungi":
            self.run_genemark()
        else:
            logging.error("只允许 <bacteria/viruses/fungi>")
            raise Exception("错误终止分析!")
        # 长度筛选
        self.genepred_lenfilter()
        # 软连接过滤后faa到1.Orthologue
        os.makedirs(f"{self.outdir}/1.Orthologue/orthofinder_indir", exist_ok=True)
        for name in self.dict_sample:
            general.link_exist(f"{self.outdir}/1.Orthologue/GenePrediction/{name}_L33.faa", 
            f"{self.outdir}/1.Orthologue/orthofinder_indir/{name}_L33.faa")

    def orthofinder(self):
        """orthologue 第一步 orthofinder"""
        self.run_orthofinder = MyRule(
            software=self.dict_soft["orthofinder"],
            infile=f"{self.outdir}/1.Orthologue/orthofinder_indir",
            outfile=f"-o {self.outdir}/1.Orthologue/orthofinder_out -n {self.library}",
            log=f"{self.outdir}/Logs/{self.library}.orthologue",
            params="-S diamond",
            thread=int(self.thread) * int(self.parallel),
            ptn="{software} -t {thread} {params} -f {infile} {outfile}"
        )

    def make_core_gene(self, files_single_gene):
        """orthologue 第五步合并保守单拷贝基因序列"""
        seq_dict = {name:"" for name in self.dict_sample}
        for sof in files_single_gene:
            # 一样的单拷贝基因就不要了
            num_uniq_gene = len(set([str(record.seq) for record in SeqIO.parse(sof, "fasta")]))
            if num_uniq_gene == 1:
                continue
            for item in itertools.product(SeqIO.parse(sof, "fasta"), self.dict_sample.keys()):
                record, name = item
                if re.match(f"^{name}_", record.id):
                    seq_dict[name] += str(record.seq)
        out_records = [SeqRecord(Seq(v), id=k, description=k) for k, v in seq_dict.items()]
        SeqIO.write(out_records, self.file_supergene, "fasta")

    def orthologue(self):
        """1.找同源基因 2.单拷贝基因多序列比对 3.保守区域预测 4.合并成长基因序列 5.合并保守基因"""
        self.mylog.info("核心基因")
        # 同源基因
        self.orthofinder()
        # 并行数太多 MyRulS 没有运行,老办法吧
        dir_single_copy = f"{self.outdir}/1.Orthologue/orthofinder_out/"\
            f"Results_{self.library}/Single_Copy_Orthologue_Sequences"
        log_single_copy = f"{self.outdir}/Logs/{self.library}.singlecopy"
        # 生成并运行大脚本
        big_cml = f"for i in {dir_single_copy}/*.fa;\ndo\n  {self.dict_soft['muscle']} -in $i -out $i.1\n"\
        f"  {self.dict_soft['Gblocks']} $i.1 -b4=5 -b5=h -t=p -e=.2\n"\
        f"  {self.dict_soft['seqkit']} sort $i.1.2 | {self.dict_soft['seqkit']} seq -w 0 > $i.3\ndone\n"
        file_big_cml = f"{self.outdir}/1.Orthologue/singlecopy_multi.sh"
        with open(file_big_cml, "wt", encoding="utf-8", newline="") as gh:
            gh.write(big_cml)
        general.run((f"bash {file_big_cml}", log_single_copy))
        # 合并保守单拷贝基因
        self.make_core_gene(files_single_gene=glob(f"{dir_single_copy}/*.3"))
    
    def msa(self):
        self.mylog.info("MSA 多序列比对")
        self.rule_msa = MyRule(
            software    = self.dict_soft["mafft"],
            infile      = self.file_supergene,
            outfile     = f"{self.outdir}/2.MSA/{self.library}.aln.fa",
            log         = f"{self.outdir}/Logs/{self.library}.mafft",
            params      = "--auto --maxiterate 1000",
            thread      = self.thread,
            ptn         = "{software} --thread {thread} {params} {infile} > {outfile}"
        )
    
    def remove_intermedia(self):
        """删除中间文件"""
        general.delete_wildcard_path(f"{self.outdir}/1.Orthologue/singlecopy_multi.sh")

    def upload(self):
        self.mylog.info("上传数据")
        tree_figs = ["rectangular", "rectangular_bl", "slanted", "circular"]
        link2upload(self.file_supergene, f"{self.outdir}/Upload/1.Orthologue")
        link2upload(self.rule_msa.outfile, f"{self.outdir}/Upload/2.MSA")
        # 进化树图软连接到Upload目录
        mylink = partial(link2upload, dir_upload=f"{self.outdir}/Upload/3.PhylogeneticTree")
        for tf in tree_figs:
            mylink(f"{self.outdir}/3.PhylogeneticTree/{tf}.png")
            mylink(f"{self.outdir}/3.PhylogeneticTree/{tf}.svg")

    def report(self):
        self.mylog.info("生成报告")
        self.rule_report = MyRule(
            software=f"{self.dict_soft['perl']} {self.dir_bin}/report.pl",
            infile=f"{self.outdir}/Upload",
            log=f"{self.outdir}/Logs/{self.library}.report",
            params="core",
            ptn="{software} {infile} {params}"
        )

    def execute(self):
        logging.info("溯源进化树>核心基因流程: 开始分析!")
        self.make_result_dir(["1.Orthologue", "2.MSA", "3.PhylogeneticTree", "FormatFASTA", "Logs"])
        self.format_fasta_multi()
        self.gene_predict()
        self.orthologue()
        self.msa()
        self.build_tree()
        self.remove_intermedia()
        self.upload()
        self.report()
        logging.info("溯源进化树>核心基因流程: 分析完成!")


class PhyloSNPFQ(PhyloSNP):
    """
    溯源进化树 - SNP
    FASTQ 输入,支持单端和双端以及单双端一起
    # 改回原始方法,每一步都声称一个shell脚本
    [infile]    输入YAML文件
    """
    def __init__(self, infile):
        super().__init__(infile)
        self.assign_soft_abspath()
        self.commands = list() # 总脚本中的所有命令列表
        
    def assign_soft_abspath(self):
        """软件路径都绑在self特征上"""
        self.snippy = self.dict_soft["snippy"]
        self.python = self.dict_soft["python"]
        self.bcftools = self.dict_soft["bcftools"]
        self.fasttree = self.dict_soft["fasttree"]
        self.Rscript = self.dict_soft["Rscript"]
        self.magick = self.dict_soft["magick"]
        self.perl = self.dict_soft["perl"]

    def snippy_multi(self):
        """snippy多样本一起跑替代snippy-multi, snippy-multi输出目录不能更改,也没有并行的功能"""
        self.mylog.info("变异检测流程")
        _shell_dir = f"{self.outdir}/Shell/snippy_multi"
        hh = open(f"{self.outdir}/Shell/snippy_multi.sh", "wt", encoding="utf-8", newline="")
        snippy_path = os.path.dirname(self.snippy)
        for name in self.dict_sample:
            gh = open(f"{_shell_dir}/{name}.sh", "wt", encoding="utf-8", newline="")
            gh.write(f"export PATH={snippy_path}:$PATH\n")
            if len(self.dict_sample[name]) == 1:
                cml = f"{self.snippy} --se {self.dict_sample[name][0]} --ref {self.reference} "\
                    f"--cpus {self.thread} --force --prefix {name} --outdir {self.outdir}/1.Variants/{name}"
            elif len(self.dict_sample[name]) == 2:
                cml = f"{self.snippy} --R1 {self.dict_sample[name][0]} --R2 {self.dict_sample[name][1]} --ref {self.reference} "\
                    f"--cpus {self.thread} --force --prefix {name} --outdir {self.outdir}/1.Variants/{name}"
            else:
                logging.error("样本列表数量错误!")
                raise Exception
            gh.write(cml+"\n")
            hh.write(f"bash {_shell_dir}/{name}.sh "
            f"> {self.outdir}/Logs/1.Variant_{name}.sh.out 2> {self.outdir}/Logs/1.Variant_{name}.sh.err\n")
            gh.close()
        hh.close()
        self.commands.append("# 并行跑snippy")
        self.commands.append(f"{self.python} {self.dir_bin}/kparallel.py -p {self.parallel} {self.outdir}/Shell/snippy_multi.sh "
        f"> {self.outdir}/Logs/snippy_multi.out 2> {self.outdir}/Logs/snippy_multi.err")

    def merge_vcf(self):
        self.mylog.info("合并变异文件")
        file_merge_vcf = f"{self.outdir}/2.MergeVCF/vcf_list.txt"
        with open(file_merge_vcf, "wt", encoding="utf-8", newline="") as gh:
            for samp in self.dict_sample.keys():
                gh.write( f"{self.outdir}/1.Variants/{samp}/{samp}.vcf.gz\n")
        self.commands.append("# 合并变异文件")
        self.commands.append(f"{self.bcftools} merge -m snps -f PASS,. --force-samples "
        f"--output-type v --file-list {file_merge_vcf} -o {self.outdir}/2.MergeVCF/{self.library}.vcf "
        f"2> {self.outdir}/Logs/bcftools_merge.err")

    def build_tree(self):
        self.mylog.info("进化树构建")
        self.commands.append("# 进化树构建")
        self.commands.append(f"{self.python} {self.dir_bin}/vcf2phylip.py -m 1 "
        f"-i {self.outdir}/2.MergeVCF/{self.library}.vcf --output-folder {self.outdir}/3.PhylogeneticTree "
        f"> {self.outdir}/Logs/vcf2phylip.out 2> {self.outdir}/Logs/vcf2phylip.err")
        self.commands.append(f"{self.fasttree} -nt {self.outdir}/3.PhylogeneticTree/{self.library}.min1.phy "
        f"> {self.outdir}/3.PhylogeneticTree/{self.library}.tre 2> {self.outdir}/Logs/fasttree.err")
        self.commands.append(f"{self.Rscript} {self.dir_bin}/tree.R {self.outdir}/3.PhylogeneticTree/{self.library}.tre "
        f"> {self.outdir}/Logs/rtree.out 2> {self.outdir}/Logs/rtree.err")
        self.commands.append(f"{self.python} {self.dir_bin}/magick.py {self.magick} {self.outdir}/3.PhylogeneticTree "
        f"> {self.outdir}/Logs/magick.out 2> {self.outdir}/Logs/magick.err")

    def remove_intermedia(self):
        self.mylog.info("删除中间文件")
        self.commands.append("# 删除中间文件")
        self.commands.append(f"rm -r {self.outdir}/1.Variants/*/ref*")
    
    def upload(self):
        self.mylog.info("上传数据")
        tree_figs = ["rectangular", "rectangular_bl", "slanted", "circular"]
        self.commands.append("# 上传数据")
        self.commands.append(f"ln -sf {self.outdir}/2.MergeVCF/{self.library}.vcf {self.outdir}/Upload/2.MergeVCF\n"
        f"ln -sf {self.outdir}/3.PhylogeneticTree/{self.library}.tre {self.outdir}/Upload/3.PhylogeneticTree")
        for tf in tree_figs:
            self.commands.append(f"ln -sf {self.outdir}/3.PhylogeneticTree/{tf}.png {self.outdir}/Upload/3.PhylogeneticTree\n"
            f"ln -sf {self.outdir}/3.PhylogeneticTree/{tf}.svg {self.outdir}/Upload/3.PhylogeneticTree")

    def report(self):
        self.mylog.info("生成报告")
        self.commands.append("# 生成报告")
        self.commands.append(f"{self.perl} {self.dir_bin}/report.pl {self.outdir}/Upload snp "
        f"> {self.outdir}/Logs/report.out 2> {self.outdir}/Logs/report.err")

    def myrun(self, runbool=False):
        """运行步骤"""
        all_script = f"{self.outdir}/Shell/all.sh"
        with open(all_script, "wt", encoding="utf-8", newline="") as gh:
            for cmd in self.commands:
                gh.write(cmd+"\n")
        if runbool: # 是否执行
            res = run(f"bash {all_script}", stdout=PIPE, stderr=PIPE, shell=True, encoding="utf-8")
            with open(f"{self.outdir}/Logs/all.sh.out", "wt", encoding="utf-8", newline="") as gh:
                gh.write(res.stdout)
            with open(f"{self.outdir}/Logs/all.sh.err", "wt", encoding="utf-8", newline="") as hh:
                hh.write(res.stderr)

    def execute(self):
        """总的执行脚本"""
        logging.info("溯源进化树>全基因组SNP-FASTQ流程: 开始分析!")
        self.make_result_dir(["Shell/snippy_multi", "Logs", "1.Variants", "2.MergeVCF", "3.PhylogeneticTree"])
        self.snippy_multi()
        self.merge_vcf()
        self.build_tree()
        self.remove_intermedia()
        self.upload()
        self.report()
        self.myrun(runbool=True)
        logging.info("溯源进化树>全基因组SNP-FASTQ流程: 分析完成!")
