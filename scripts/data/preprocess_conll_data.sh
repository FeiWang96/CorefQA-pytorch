#!/usr/bin/env bash 
# -*- coding: utf-8 -*- 


# Author: xiaoy li
# description:
# geneate datasets with conll format. 

ontonotes_path=$1
data_dir=$2

REPO_PATH=$3 #example: /home/lixiaoya/corefQA 
export PYTHONPATH=${REPO_PATH}

dlx() {
  wget -P $data_dir $1/$2
  tar -xvzf $data_dir/$2 -C $data_dir
  rm $data_dir/$2
}

download_bert(){
  model=$1
  wget -P $data_dir https://storage.googleapis.com/bert_models/2018_10_18/$model.zip
  unzip $data_dir/$model.zip
  rm $data_dir/$model.zip
  mv $model $data_dir/
}

conll_url=http://conll.cemantix.org/2012/download
dlx $conll_url conll-2012-train.v4.tar.gz
dlx $conll_url conll-2012-development.v4.tar.gz
dlx $conll_url/test conll-2012-test-key.tar.gz
dlx $conll_url/test conll-2012-test-official.v9.tar.gz

dlx $conll_url conll-2012-scripts.v3.tar.gz
dlx http://conll.cemantix.org/download reference-coreference-scorers.v8.01.tar.gz

download_bert cased_L-12_H-768_A-12
download_bert cased_L-24_H-1024_A-16

bash ${REPO_PATH}/data_preprocess/conll-2012/v3/scripts/skeleton2conll.sh -D $ontonotes_path/data/files/data $data_dir/conll-2012

function compile_partition() {
    rm -f $2.$5.$3$4
    cat $data_dir/conll-2012/$3/data/$1/data/$5/annotations/*/*/*/*.$3$4 >> $data_dir/$2.$5.$3$4
}

function compile_language() {
    compile_partition development dev v4 _gold_conll $1
    compile_partition train train v4 _gold_conll $1
    compile_partition test test v4 _gold_conll $1
}

compile_language english
#compile_language chinese
#compile_language arabic


vocab_file=${REPO_PATH}/data_preprocess/vocab.txt
python ${REPO_PATH}/data_preprocess/minimize.py $vocab_file $data_dir $data_dir false