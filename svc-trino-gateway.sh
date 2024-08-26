#!/bin/sh
if test $# != 1
then
  echo "Must start or stop."
  exit 1
fi

cd `dirname $(readlink -f $0)`

function start(){
  nohup python -u trino-gateway.py >trino-gateway.log 2>&1 &
  echo $! > trino-gateway.pid
}

function stop(){
  if test -f trino-gateway.log;then rm trino-gateway.log;fi
  if test -f trino-gateway.pid;then cat trino-gateway.pid | xargs kill -9 && rm trino-gateway.pid;fi
}

case $1 in
  start)
  start
  ;;
  stop)
  stop
  ;;
  *)
  echo "Only start or stop"
esac
