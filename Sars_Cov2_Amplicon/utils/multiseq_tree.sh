#!/usr/bin/env bash

#~ merge consensus .fa
cat $REFERENCE \
    ${RESULT_DIR}/*/4.consensus/*consensus.fa \
    > ${RESULT_DIR}/multiseq_phylogenetic_tree/merged.consensus.fa
#~ multiple sequences alignment
mafft --auto --maxiterate 1000 \
    ${RESULT_DIR}/multiseq_phylogenetic_tree/merged.consensus.fa \
    > ${RESULT_DIR}/multiseq_phylogenetic_tree/merged.consensus.aln.fa \
    2> ${RESULT_DIR}/logs/mafft.e
#~ FastTree
fasttree -nt ${RESULT_DIR}/multiseq_phylogenetic_tree/merged.consensus.aln.fa \
    > ${RESULT_DIR}/multiseq_phylogenetic_tree/merged.consensus.tree \
    2> ${RESULT_DIR}/logs/multiseqfasttree.e
#~ multi-seq phylogenetic tree 
Rscript ${SCRIPTS_PATH}/utils/tree.R \
    ${RESULT_DIR}/multiseq_phylogenetic_tree/merged.consensus.tree \
    > ${RESULT_DIR}/logs/multiseqtree.R.o \
    2> ${RESULT_DIR}/logs/multiseqtree.R.e
