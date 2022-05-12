package GDHR;
use strict;
use warnings;

use GDHR::DEBUG;
use GDHR::HTML;
use File::Basename qw/basename dirname/;

require Exporter;
our @ISA = qw(Exporter);

sub new {
    my ($class, %opts) = @_;

    # check the ENV
    # my $root = $ENV{'GDHR_PATH'} or die "GDHR_PATH is not defined in your ENV!";
    my $root = dirname(__FILE__);

    my $report = {};
    $report->{path}->{root} = $root;

    bless $report, $class;

    # init the report dir 
    $report->init_report(%opts);

    return $report;
}

sub init_report {
    my ($class, %opts) = @_;

    # create the outdir 
    my $outdir = $opts{'-outdir'} || ".";
    mkdir $outdir unless -d $outdir;
    $class->{path}->{outdir} = $outdir;

    # the public vars
    $class->{resp_htabs_cnt} = 1;  # for parent horizontal tabs
    $class->{resp_vtabs_cnt} = 1;  # for parent vertical tabs
    $class->{child_vtabs_cnt} = 1; # for child tabs in parent horizontal tab
    #    $class->{child_htabs_cnt} = 1; # for child tabs in parent vertical tabs

    $class->{menu_cnt} = 0;
    $class->{submenu_cnt} = 0;
    $class->{img_cnt} = 0;
    $class->{tab_cnt} = 0;
    $class->{container_cnt} = 0;
    $class->{json} = "";
    $class->{getPic} = "";
    $class->{brief} = {};

    # the report 's pipe type
    my $pipe = $opts{'-pipe'} || "补充";
    $class->{pipe} = $pipe;

    # the main index name 
    my $name = $opts{'-name'} || "index";
    $class->{name} = $name;

    # copy the config files to outdir
    $class->cp_conf_files();

    # the company info
    my $company = "微远基因";
    my $fullname = "微远基因";
    my $url = "";
    $class->{company} = $company;
    $class->{company_fullname} = $fullname;
    $class->{url} = $url;
    $class->{logo} = "logo.png";

    if ($opts{'-logo'}) {
        system("cp $opts{'-logo'} $outdir/src/image");
        $class->{logo} = basename($opts{'-logo'});
    }

    $class->{nonlazy} = $opts{'-nonlazy'} || $opts{nonlazy} ? 1 : 0;
    $class->init_main_html();
}

sub cp_conf_files {
    my $class = shift;

    my $outdir = $class->{path}->{outdir};
    my $root = $class->{path}->{root};
    my $conf_dir = "$root/src";

    mkdir "$outdir/src" unless -d "$outdir/src";

    system("cp -r $conf_dir/* $outdir/src");
    timeLOG("init the config done ... ");
}

sub init_main_html {
    my $class = shift;

    my $html = "";
    $class->{html} = $html;
}

sub section {
    my ($class, %opts) = @_;
    my $section = GDHR::HTML->section($class, %opts);

    push @{$class->{section}}, $section;
    return $section;
}

sub write {
    my ($class, %opts) = @_;

    my $outdir = $class->{path}->{outdir};

    my $head = $class->main_html_head();
    my $tail = $class->main_html_tail(%opts);

    my $html = $class->{html};
    foreach my $section (@{$class->{section}}) {
        $html .= $section->innerHTML;
    }

    open OUT, ">", "$outdir/index.html";
    print OUT $head;
    print OUT $html;
    print OUT $tail;
    close OUT;

    unless ($class->{nonlazy}) {
        open JSON, ">", "$outdir/src/js/pic.js" or die $!;
        print JSON "getPic ({$class->{json}})";
        close JSON;
    }

    timeLOG("The html report 'index.html' was create done :)");
}

# pack the report folder, this function will use the pack cmd of system, so just for Linux now.
# support pack format: gz, bz2, zip, rar
sub pack {
    my ($class, %opts) = @_;

    my $outdir = $class->{path}->{outdir};
    chop $outdir if ($outdir =~ /\/$/);

    my $out_name = basename($outdir);
    my $out_dir = dirname($outdir);

    my $format = $opts{'-format'} || "bz2";

    my $cmd = "";
    if ($format eq "bz2") {
        $cmd = "cd $out_dir; tar -h -cjf $out_name.tar.bz2 $out_name";
    }
    elsif ($format eq "gz") {
        $cmd = "cd $out_dir; tar -h -czf $out_name.tar.gz $out_name";
    }
    elsif ($format eq "zip") {
        $cmd = "cd $out_dir; zip -r $out_name.zip $out_name";
    }
    elsif ($format eq "rar") {
        $cmd = "cd $out_dir; rar a -r $out_name.rar $out_name";
    }
    else {
        ERROR("pack format error, now just support format: gz, bz2, zip, rar.", $format);
    }

    system("$cmd 1>/dev/null");
    timeLOG("The html report has been packed :)");
}

sub main_html_head {
    my $class = shift;
    my $pipe = $class->{pipe};
    my $company = $class->{company};
    my $head = <<HTML;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <!-- 基本信息 -->
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="shortcut icon" href="src/image/icon.png" type="image/x-icon">
        <title>$company 分析报告</title>
        
        <!-- CSS文档 -->
        <link rel="stylesheet" type="text/css" href="src/css/index.css" />
        <link rel="stylesheet" type="text/css" href="src/css/jquery.dataTables.min.css" />
        <link rel="stylesheet" type="text/css" href="src/css/report.css" />
        <link rel="stylesheet" type="text/css" href="src/css/jumpto.css" />
        <link rel="stylesheet" type="text/css" href="src/css/easy-responsive-tabs.css" />
        <link rel="stylesheet" type="text/css" href="src/css/toggle.css" />

        <!-- JS脚本 -->
        <script src="src/js/jquery-1.9.1-min.js"></script>
        <script src="src/js/modernizr-min.js"></script>
        <script src="src/js/jquery.jumpto.js"></script>
        <script src="src/js/toggle.js"></script>

        <script src="src/js/jquery.nicescroll-min.js"></script>
        <script src="src/js/easyResponsiveTabs-min.js"></script>
        <script src="src/js/show_help-min.js"></script>
        <script src="src/js/jquery.dataTables.min.js"></script>

    </head>
    <body>
        <section>
            <div id="header_banner">
            <div id="banner_logo"></div>
            <div id="banner_title"><span> $pipe </span></div>
            <div id="banner_bg_image"></div>
            </div>
        </section>
        <div class="toggleNav">
            <span class="fold1">收起</span>
            <span class="fold2 close">展开</span>
        </div>
        <div id="report_body">
HTML
    return $head;
}

sub main_html_tail {
    my $class = shift;
    my %opts = @_;
    my $url = $class->{url};
    my $lazy_load = $class->lazy_load();

    my $tail = <<HTML;
        </div>
        
        <div id="goTop" style="display:none;">
            <a title="返回顶部" class="backtotop">
                <img class="back-top" src="src/image/goTop.jpg">
            </a>
        </div>
        
        <!-- 帮助文档窗口 -->
        <div id="show_help">
            <h3>帮助文档</h3>
            <iframe id="help_page" name="help_page" src="$url"></iframe>
        </div>
        
        <!-- JS插件初始化 -->
        <script type="text/javascript">
            \$(function(){
                \$(".abbrTab").each(function(){
                var len=\$(this).attr("data");
                var mess=\$(this).text();
                \$(this).attr("title",mess);
                if(mess.length>len-1){
                mess=mess.substring(0,len-1);
                mess +='<span class="brief">...</span>';
            }
                \$(this).html(mess);

                });

                \$(".brief").click(function(){
                var info=\$(this).parent().attr("title");
                  messshow (info);
                 });
                
                \$(".func_table").DataTable({"ordering": false,"scrollX": true} );
            });
            
            \$(document).ready(function() {
                \$("#report_body").jumpto({
                    innerWrapper: "section",
                    firstLevel: "> h3",
                    secondLevel: "> h5",
                    offset: 0,
                    anchorTopPadding: 90,
                    animate: 600,
                    showTitle: "目录",
                    closeButton: false
                });
                
                // init parent vertical tabs
                for (var i = 1; i < $class->{resp_vtabs_cnt}; i++){
                    \$('#resp-vtabs-list' + i).niceScroll({cursoropacitymax:0.5,cursorwidth:"8px"});
                    \$('#resp-vtabs-container' + i).niceScroll({cursoropacitymax:0.5,cursorwidth:"8px"});
                    \$('#parentVerticalTab' + i).easyResponsiveTabs({
                        type: 'vertical', //Types: default, vertical, accordion
                        width: 'auto', //auto or any width like 600px
                        fit: true, // 100% fit in a container
                        closed: 'accordion', // Start closed if in accordion view
                        tabidentify: 'hor_' + i, // The tab groups identifier
                        activate: function(event) { // Callback function if tab is switched
                            var \$tab = \$(this);
                            var \$info = \$('#nested-tabInfo2');
                            var \$name = \$('span', \$info);
                            \$name.text(\$tab.text());
                            \$info.show();
                        }
                    });
                }
                
                for (var i=1; i < $class->{resp_htabs_cnt}; i++){
                    \$('#parentHorizontalTab' + i).easyResponsiveTabs({
                        type: 'default', //Types: default, vertical, accordion
                        width: 'auto', //auto or any width like 600px
                        fit: true, // 100% fit in a container
                        closed: 'accordion', // Start closed if in accordion view
                        tabidentify: 'hor_' + i, // The tab groups identifier
                        activate: function(event) { // Callback function if tab is switched
                            var \$tab = \$(this);
                            var \$info = \$('#nested-tabInfo2');
                            var \$name = \$('span', \$info);
                            \$name.text(\$tab.text());
                            \$info.show();
                        }
                    });
                }
                
                // init child vertical tabs
                for (var i=1; i < $class->{child_vtabs_cnt}; i++){
                    \$('#child-vtabs-list' + i).niceScroll({cursoropacitymax:0.5,cursorwidth:"8px"});
                    \$('#child-vtabs-container' + i).niceScroll({cursoropacitymax:0.5,cursorwidth:"8px"});
                    \$('#ChildVerticalTab' + i).easyResponsiveTabs({
                        type: 'vertical',
                        width: 'auto',
                        fit: true,
                        tabidentify: 'ver_' + i,
                        activetab_bg: '#fff',
                        inactive_bg: '#F5F5F5',
                        active_border_color: '#c1c1c1',
                        active_content_border_color: '#5AB1D0'
                    });
                }
            });

        window.onload=function(){ 
            \$('.jumpto-first').css('max-height', (\$(window).height()*0.98 - 48) + 'px');
            \$('.jumpto-first').niceScroll({cursoropacitymax:0.5,cursorwidth:"6px",cursorborder:"0px"});
        } 

            /****表格悬浮显示全部内容****/
            function messshow (info) {
            var str='<div class="topBg"><div class="toppicBox"><div class="inBox" style="text-align:center;"><br><textarea class="pinfo" cols=56>'+info+'</textarea><br><br></div><img class="topClose" width="27" height="27" src="src/image/topclose.png" onclick="topclose()"></div></div>';
                  \$("body").append(str);}

            function topclose(){
            \$(".topBg").remove();
            }

            \$('.hl_table tr').has('td').each(function(){
                \$(this).attr('onmouseover', 'this.style.backgroundColor = "#DDDDDD"');
                \$(this).attr('onmouseout', 'this.style.backgroundColor = "#FFFFFF"');
            });
            
            \$('.func_table tr').has('td').each(function(){
                \$(this).attr('onmouseover', 'this.style.backgroundColor = "#DDDDDD"');
                \$(this).attr('onmouseout', 'this.style.backgroundColor = "#FFFFFF"');
            });
            
            \$(".logo").click(function(){\$(window).scrollTop(0);});

            var width = \$('.func_table:eq(0)').parents('section').width();
            if (width < 200)
            {
                width = 1000;
            }
            \$(".func_table caption").css('width',width);
            \$(".func_table").parents('.dataTables_scrollBody').scroll(function(){
            \$(this).parent().find('caption').css('margin-left',\$(this).scrollLeft());
        });
        </script>
        
        $lazy_load

    </body>
</html>
HTML

    return $tail;
}


sub lazy_load {
    my $class = shift;
    my $getPic = $class->{getPic};

    my $js = <<JS;
        <script src="src/js/lazy_load_pre.js"></script>
        <script type="text/javascript">
            // fetch the data from json file
            function getPic(res){
                $getPic
            }
        </script>

        <script src="src/js/lazy_load_main.js"></script>
        <script src="src/js/pic.js?callback=getPic"></script>
JS

    return $js;
}
