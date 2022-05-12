#!/usr/bin/env bash
#condition: R=4.1+ ,package:knitr,kableExtra,rmarkdown
#copy CSS file
# ${SCRIPTS_PATH}/utils/zhu/


#================================================================PREPARE==========================================================================================================
#=================================================================================================================================================================================		


cp -r ${SCRIPTS_PATH}/utils/zhu/css_file  ${RESULT_DIR}
wait
# check total_list_report.Rmd exists, delete!
if [ -f ${RESULT_DIR}/css_file/total_list_report.Rmd ];then
    rm ${RESULT_DIR}/css_file/total_list_report.Rmd
fi

cp -r ${SCRIPTS_PATH}/utils/zhu/total_list_report.Rmd  ${RESULT_DIR}/css_file/total_list_report.Rmd


echo -e "\n#######################################################prepare complete################################################################################"
	


for i in `less ${RESULT_DIR}/intermedia/sample_path_table.txt|cut -f1`; 
do
    SAMPLE_NAME=$i
    fastqc_data=${RESULT_DIR}/details/${SAMPLE_NAME}/1.qc/fastqc
    variants_data=${RESULT_DIR}/details/${SAMPLE_NAME}/3.variants
				
    #unzip fastqc.zip file
    #YF3583-Y16_S1_R1_001_fastqc.gz
    unzip -n ${fastqc_data}/*R1*fastqc.zip -d ${fastqc_data}
    unzip -n ${fastqc_data}/*R2*fastqc.zip -d ${fastqc_data}

    cp -r ${fastqc_data}/*R1*fastqc ${fastqc_data}/${SAMPLE_NAME}_1_fastqc
    cp -r ${fastqc_data}/*R2*fastqc ${fastqc_data}/${SAMPLE_NAME}_2_fastqc
    cp -r  ${fastqc_data}/*R1*fastqc.html ${fastqc_data}/${SAMPLE_NAME}_1_fastqc.html
    cp -r ${fastqc_data}/*R2*fastqc.html ${fastqc_data}/${SAMPLE_NAME}_2_fastqc.html 
    wait

    #sed basic message
    sed -n '3,10p' ${fastqc_data}/${SAMPLE_NAME}_1_fastqc/fastqc_data.txt |sed  's/#//g' >${fastqc_data}/${SAMPLE_NAME}_1_fastqc/${SAMPLE_NAME}_1_basic_content.txt
    sed -n '3,10p' ${fastqc_data}/${SAMPLE_NAME}_2_fastqc/fastqc_data.txt |sed  's/#//g' >${fastqc_data}/${SAMPLE_NAME}_2_fastqc/${SAMPLE_NAME}_2_basic_content.txt
    wait

    #confirm .vcf file has variants
    if test  -z  "$(less ${variants_data}/${SAMPLE_NAME}.vcf |grep -v "#")" ;then
  	echo "no var"
    
   else
       less ${variants_data}/${SAMPLE_NAME}.vcf |grep -v "#" |sed 's/;/\t/g'|awk '{print "'${SAMPLE_NAME}'","\t" $1 "\t" $2 "\t" $4 "\t" $5 "\t" $6}'>${variants_data}/${SAMPLE_NAME}_vcf_result.txt
       sed -i '1i sample \t ref_reads \t var_pos \t ori_base \t var_base \t qual' ${variants_data}/${SAMPLE_NAME}_vcf_result.txt
   fi  
   wait
	
done



echo -e "############################################################unzip complete############################################################################\n\n\n"



#copy RMD file to run 
for i in `less ${RESULT_DIR}/intermedia/sample_path_table.txt|cut -f1`; 
do
	echo -e "#######################################${i} report start product#########################################################################"
	
	
    sed 's/{sample}/'${i}'/g' ${SCRIPTS_PATH}/utils/zhu/html_output_demo.Rmd >${RESULT_DIR}/css_file/output_demo.Rmd
    wait
	
    Rscript ${SCRIPTS_PATH}/utils/zhu/output.R ${RESULT_DIR}/css_file/output_demo.Rmd ${RESULT_DIR}/details/${i}/${i}_report.html
    wait
	
	echo -e "################${i} add to total_list_report.RMD \n\n"
    echo -e "<a href=\"./details/${i}/${i}_report.html\" target=\"_Blank\"><font size=\"4.5\">Click to view the ${i}_report</font></a><br>" >> ${RESULT_DIR}/css_file/total_list_report.Rmd
    wait
	
done

dos2unix ${RESULT_DIR}/css_file/total_list_report.Rmd
wait
Rscript ${SCRIPTS_PATH}/utils/zhu/output.R ${RESULT_DIR}/css_file/total_list_report.Rmd ${RESULT_DIR}/total_list_report.html




# rm -rf ${RESULT_DIR}/css_file 
