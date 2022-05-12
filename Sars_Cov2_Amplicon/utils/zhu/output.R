#! /usr/local/bin/Rscript --vanilla

args <- commandArgs(T)

cat("input_file is  ",args[1])
cat("\n")
cat("output_file is  ",args[2])
#output_file needs absolute path
rmarkdown::render(args[1],output_file=args[2])

