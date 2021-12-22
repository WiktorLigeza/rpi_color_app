#!bin/bash
cd ${0%/*}
./dist/main --stop
./dist/main --run
