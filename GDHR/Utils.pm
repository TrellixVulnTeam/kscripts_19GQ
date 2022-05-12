package Utils;

use strict;
use warnings;

require Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(BlankLine blank Image FileLink);

sub BlankLine {
    # 空白行
    my $section = shift;
    my $line_num = shift;
    my $blank = "<br>" x $line_num;
    $section->desc($blank);
    return;
}

sub blank {
    # 空格
    my $num = shift;
    my $res = "&nbsp;" x $num;
    return ($res);
}

sub Image {
    # 各种图片函数的封装
    my $section = shift;
    my $png_arr = shift;
    my $desc_arr = shift;
    my $title = shift;
    my $png_arr2 = shift;
    my $desc_arr2 = shift;
    my $name_arr = shift;
    my @add_para = @_;

    if (@{$png_arr} != @{$desc_arr}) {
        print STDERR "the number of names is not equal to the number of images\n@{$png_arr}\n@@{$desc_arr}\n";
        die;
    }

    if (defined $png_arr2 && scalar(@$png_arr2) > 0) {
        if (@{$png_arr2} != @{$desc_arr}) {
            print STDERR "the number of names is not equal to the number of images\n@{$png_arr2}\n@@{$desc_arr}\n";
            die;
        }
        if (@{$png_arr} == 1) {
            $section->img2html2(-file1 => @{$png_arr}, -name1 => @{$desc_arr}, -file2 => @{$png_arr2}, -name2 => @{$desc_arr2}, @add_para);
        }
        else {
            $section->imgs2html2(-files1 => $png_arr, -desc1 => $desc_arr, -names => $name_arr, -files2 => $png_arr2, -desc2 => $desc_arr2, -name => $title, @add_para);
        }
    }
    else {
        if (@{$png_arr} == 1) {
            $section->img2html(-file => @{$png_arr}, -name => @{$desc_arr}, @add_para);
        }
        else {
            $section->imgs2html(-files => $png_arr, -names => $desc_arr, -name => $title, @add_para);
        }
    }

    return;
}

sub FileLink {
    my $section = shift;
    my $desc = shift;
    my %opts = @_;
    my ($link) = $desc =~ /<link=(.*)>/;
    my ($name) = $link =~ /.*\/(.*)/;
    $desc =~ s#<link=$link>#: <a href=\"$link\" target=\"_blank\">$name</a>#;
    $section->desc($desc, %opts);
    return;
}
