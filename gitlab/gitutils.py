#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from shlex import split as arg_split
from subprocess import Popen, PIPE, STDOUT
from sys import stderr


def die(text, exit_code=1):
    stderr.write("ERROR: {0}\n".format(text))
    exit(exit_code)


def console(command, stream=False):
    ret = None
    out = None
    print(command)
    try:
        process = Popen(arg_split(command), stdout=PIPE, stderr=STDOUT)
        if stream:
            for line in iter(process.stdout.readline, b''):
                print line.rstrip()
        process.wait()
    except Exception as e:
        ret = e.args[0]
        out = e
    else:
        ret = process.returncode
        out = process.stdout.read()
    finally:
        return {"code": ret, "message": out}


class GitUtils:
    def __init__(self):
        pass

    @staticmethod
    def clone(repository_url):
        command = "git clone {0}".format(repository_url)
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def fetch():
        command = "git fetch origin"
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def pull():
        command = "git pull"
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def checkout(commit_id):
        command = "git checkout {0}".format(commit_id)
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def init():
        command = "git init"
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def remote_add(remote_repository):
        command = "git remote add origin {0}".format(remote_repository)
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def add(files):
        command = "git add {0}".format(files)
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def commit(commit_message):
        command = "git commit -m '{0}'".format(commit_message)
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])

    @staticmethod
    def push(push_command):
        command = "git push {0}".format(push_command)
        res = console(command, True)
        if res["code"] != 0:
            die(res["message"], res["code"])
