package GDHR::CHART;
#-----------------------------------------------+
#    [APM] This moudle was created by amp.pl    |
#    [APM] Created time: 2017-09-20 15:58:26    |
#-----------------------------------------------+
=pod

=head1 Name

CHART

=head1 Synopsis



=head1 Feedback

Author: Peng Ai
Email:  aipeng0520@163.com

=head1 Version

Version history

=head2 v1.0

Date: 2017-09-20 15:58:26

=cut


use strict;
use warnings;

require Exporter;
our @ISA = qw(Exporter);

use File::Basename qw/basename/;

use lib "$ENV{GDHR_PATH}/lib";
use GDHR::DEBUG;
use GDHR;

sub new
{
    my ($class,%opts) = @_;
    
    my $chart = {};
    
    $chart->{js}   = "";
    $chart->{html} = "";
    $chart->{id} = 0;

    bless $chart , $class;
    return $chart;
}

#===  FUNCTION  ================================================================
#         NAME: pie
#      PURPOSE: 
#   PARAMETERS: data, needed
#               -title , default NULL
#               -legend_title, default 'Series'
#
#      RETURNS: the id of the pie chart 
#  DESCRIPTION: draw pie chart with highcharts
#       THROWS: no exceptions
#     COMMENTS: none
#     SEE ALSO: n/a
#===============================================================================
sub pie
{
    my ($class,$data,%opts) = @_;
    $opts{'-title'} //= "";
    $opts{'-legend_title'} //= "";
    $class->{id} ++;
    
    my $pie_data;
    if (ref $data eq "ARRAY")
    {
        $pie_data = array2json_pie($data);
    }
    elsif (-e $data)
    {
        my @array;
        open my $fh , "<" , $data or die $!;
        
        <$fh> if ($opts{'-header'});
        while(<$fh>)
        {
            chomp;
            my ($name,$val) = (split /\t/)[0,1];
            push @array , [$name,$val] if ($name && $val);
        }
        close $fh;

        $pie_data = array2json_pie(\@array);
    }
    
    my $id = $class->id;
    my $pie_js = <<JS;
Highcharts.chart('$id', {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
    },
    title: {
        text: '$opts{'-title'}'
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
            enabled: false
        },
        showInLegend: true
        }
    },
    series: [{
        name: '$opts{'-legend_title'}',
        colorByPoint: true,
        $pie_data
    }]
});
JS
    
    my $pie_html = <<HTML;
<div id="$id" style="min-width: 310px; height: 400px; max-width: 600px; margin: 0 auto"></div>
HTML
    $class->add_html($pie_html);
    $class->add_js($pie_js);
    
    return $id;
}

sub array2json_pie
{
    my $array = shift;

    my @js = map { "{ name: \'$_->[0]\', y: $_->[1] }" } @$array;
    my $js = join "," , @js;
    return "data: [$js]\n";
}

sub pca_plot {
    my ($class,$data,%opts) = @_;
    my $id = $class->id(%opts);
}

sub bar {
    my ($class,$data,%opts) = @_;
    my $id = $class->id(%opts);

    my $json = "";
    if (ref $data eq "ARRAY"){
        $json = array2json_bar($data);
    } elsif (-e $data){
        my @array;
        open my $fh , "<" , $data or die $!;
        
        <$fh> if ($opts{'-header'});
        while(<$fh>)
        {
            chomp;
            my ($name,$val) = (split /\t/)[0,1];
            push @array , [$name,$val] if ($name && $val);
        }
        close $fh;

        $json = array2json_bar(\@array);
    }
    
    my $js = <<JS;
var init_data = $json

var div = new Param({
    id:'$id',
    drawObj:ZZT,
    drawData:{
        initData:init_data
    }
})
JS

    $class->add_div(id=>$id);
    $class->add_js($js);

    return $id;
}

*simple_bar = \&bar;

sub array2json_bar {
    my $array = shift;

    my @js = map { "$_->[0]:$_->[1]" } @$array;
    my $js = join "," , @js;
    return "{ $js };";
}

sub id {
    my ($class,%opts) = @_;
    if ($opts{'id'}){
        return $opts{id};
    }else{
        $class->{id} ++;
        return "div" . $class->{id};
    }
}

sub add_div {
    my ($class,%opts) = @_;
    my $id = $opts{id} or die "id must be defined for <div> of fig";
    
    my $html = <<HTML;
<div id="$id" style="min-width: 310px; height: 400px; max-width: 600px; margin: 0 auto"></div>
HTML
    
    $class->add_html($html);
}

sub add_html
{
    my $class = shift;
    my $str = shift;

    my $main = $class->{html};
    $main .= $str;

    $class->{html} = $main;
}

sub add_js
{
    my $class = shift;
    my $str = shift;

    my $main = $class->{js};
    $main .= $str;

    $class->{js} = $main;
}

sub save
{
    my ($class,%opts) = @_;
    ERROR("no_file_defined","the -file must be set for save the chart js code") unless $opts{'-file'};
    $opts{'-format'} //= "js";

    my $context;
    if ($opts{'-format'} eq "html")
    {
        $context = <<HTML;
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">

<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="http://192.168.123.53/webcode/front/common/d3.min.js"></script>
<script src="http://192.168.123.53/webcode/front/protogenesis/myColor/MyColor.min.js"></script>
<script src="http://192.168.123.53/webcode/front/common/func.js"></script>
<script src="http://192.168.123.53/webcode/front/protogenesis/Param/Param.js"></script>
<script src="http://192.168.123.53/webcode/front/protogenesis/ZZT/zzt.js"></script>

</head>

<body>
$class->{html}

<script type="text/javascript">
$class->{js}
</script>
</body>
HTML
    }
    elsif ($opts{'-format'} eq "js")
    {
        $context = $class->{js};
    }

    open my $ofh , ">" , "$opts{'-file'}" or die $!;
    print $ofh $context;
    close $ofh;
}
