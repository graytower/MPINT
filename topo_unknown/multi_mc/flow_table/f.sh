#!/bin/bash

THRIFT_PORT=9090
cd ../flow_table

for((i=1; i<=13; i++));
do
    simple_switch_CLI --thrift-port=$THRIFT_PORT < `find . -name "s$i.txt"`
    let 'THRIFT_PORT += 1 '
done