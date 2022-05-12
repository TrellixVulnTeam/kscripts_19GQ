use lib "/sdbb/share/lib/GDHR";
use strict;
use GDHR;
use Utils;

# 读入命令行参数
my $dir=shift;
my $pipe=shift;

# 配置可变文字
my %pipe_hash = (
    "wgs"   => "全基因组多序列比对(WGMSA)",
    "snp"   => "变异(SNP)",
    "core"  => "核心基因(Core Gene)"
);

# 标题
my $report;
$report = GDHR->new(-outdir => $dir,
    -pipe                   => "溯源进化树分析结果",
    -nonlazy                => 1);

# 项目介绍
my $section;
$section = $report->section(id => "introduction");
$section->menu("进化树介绍");
$section->desc("进化树，又称系统发育树，展示具有亲缘关系的物种/基因之间的种系发生历史的树状图。进化树由结点和进化分支组成，每一结点表示一个分类学单元，进化分支定义了分类单元之间的关系。");

# 结果
my $section;
$section = $report->section(id => "result");
$section->menu("分析结果");
$section->desc("本次分析基于<b>$pipe_hash{$pipe}</b>使用最大似然法构建进化树。");
# 多图
my @prefix_tree = qw(rectangular rectangular_bl slanted circular);
my @fig_tree = map {"3.PhylogeneticTree/$_.png"} @prefix_tree;
my @labels = qw(矩形 矩形真实距离 倾斜 圆形);
Image($section, \@fig_tree, \@labels, "进化树图");

# 最后
$report->write();
