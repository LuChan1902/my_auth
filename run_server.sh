#!/bin/bash
export test_tree_path=/home/luchan19022/mytrees
# 打印一下，确保真的有
echo "Server Tree Path: $test_tree_path"
# 启动服务
./mdsip_local -s -p 8888 -h ./proxy.hosts

