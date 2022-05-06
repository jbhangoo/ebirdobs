#!/bin/sh -v

simargs=""

for var in "$@"
do
    simargs="$simargs $var"
done

cd diversity/src

./eelf $simargs

echo "./eelf $simargs"
