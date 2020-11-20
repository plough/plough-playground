#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
python 实现管道功能

用例：
python pipe.py "cat pipe.py|grep def|wc -l"
"""
import os
import sys


def main(cmdtext):
    cmds = [cmd.strip() for cmd in cmdtext.split("|")]
    # 第一条指令左边没有管道
    run_cmds(cmds, ())


def run_cmd(cmd, left_pipe, right_pipe):
    print cmd, os.getpid(), os.getppid()
    if left_pipe:
        os.dup2(left_pipe[0], sys.stdin.fileno())
        os.close(left_pipe[0])
        os.close(left_pipe[1])
    if right_pipe:
        os.dup2(right_pipe[1], sys.stdout.fileno())
        os.close(right_pipe[0])
        os.close(right_pipe[1])
    # 分割指令参数
    args = [arg.strip() for arg in cmd.split()]
    args = [arg for arg in args if arg]
    try:
        # 传入指令名称、指令参数数组
        # 指令参数数组的第一个参数就是指令名称
        os.execvp(args[0], args)
    except OSError as ex:
        print "exec error:", ex


# 指令的列表以及下一条指令左边的管道作为参数
def run_cmds(cmds, left_pipe):
    # 取出指令串的第一个指令，即将执行这第一个指令
    cur_cmd = cmds[0]
    other_cmds = cmds[1:]
    # 创建管道
    pipe_fds = ()
    if other_cmds:
        pipe_fds = os.pipe()
    # 创建子进程
    pid = os.fork()
    if pid < 0:
        print "fork process failed"
        return
    if pid > 0:
        # 父进程来执行指令
        # 同时传入左边和右边的管道(可能为空)
        run_cmd(cur_cmd, left_pipe, pipe_fds)
    elif other_cmds:
        # 莫忘记关闭不再使用的描述符
        if left_pipe:
            os.close(left_pipe[0])
            os.close(left_pipe[1])
        # 子进程递归继续执行后续指令，携带新创建的管道
        run_cmds(other_cmds, pipe_fds)


if __name__ == "__main__":
    main(sys.argv[1])
