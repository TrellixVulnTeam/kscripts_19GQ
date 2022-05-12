# README

一个用来生成HTML报告的Perl模块

## 示例
```perl5
# 导入模块
use lib "/sdbb/bioinfor/renchaobo/test/GDHR";
use GDHR;

# 新建一个HTML对象
my $report;
$report = GDHR->new(-outdir => "./Demo",
    -pipe                   => "DemoReport",
    -nonlazy                => 0);

# 新建一个section对象
my $section;
$section = $report->section(id => "introduction");
$section->menu("项目介绍");

# 添加描述信息
$section->desc("这是一段描述信息");

# 添加图片
$section->img2html(
    -file => "img.png",
    -name => "信息分析流程图");

# 添加两个并排的图片
$section->imgs2html2(
    -files1 => "img1.png",
    -desc1  => "P1",
    -files2 => "img2.png",
    -desc2  => "P2");

# 添加一个表格
$section->tsv2html(
    -file   => "T1.tsv",
    -name   => "T1",
    -header => 1);

# 添加一个
## 生成HTML报告
$report->write();

```
