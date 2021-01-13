#!/bin/bash

THRIFT_PORT=9090

for((i=1; i<=4; i++));
do
    simple_switch_CLI --thrift-port=$THRIFT_PORT < `find . -name "c$i.txt"`
    let 'THRIFT_PORT += 1 '
done

for((i=1; i<=8; i++));
do
    simple_switch_CLI --thrift-port=$THRIFT_PORT < `find . -name "a$i.txt"`
    let 'THRIFT_PORT += 1 '
done

for((i=1; i<=8; i++));
do
    simple_switch_CLI --thrift-port=$THRIFT_PORT < `find . -name "e$i.txt"`
    let 'THRIFT_PORT += 1 '
done