#!/usr/bin/python
# encoding:utf8
# -*- coding: utf-8 -*-
# Prerequisite
#   1. This scripts runs on Linux virtual machine(we run on jenkins slave node)
#   2. mate-common-service lib exsit on Linux virtual machine
# How to execute the python script: eg: python check_common_version.py --service=xxx-service --branch='dev|test|uat|prod'
import jenkins
import getopt
import sys
import os
import re
import ast

# get parameter: service, branch
def get_parameter():
    opts, args = getopt.getopt(sys.argv[1:], '-h-s:-b:', ['help', 'service=', 'branch='])
    for opt_name, opt_value in opts:
        if opt_name in ('-h', '--help'):
            print("How to run: python check_common_version.py --service=xxx-service --branch='dev|test|uat|prod'")

        if opt_name in ('-s', '--service'):
            line = re.match(r'(.*?)/(.*)', opt_value)
            service_name = line.group(2)
            print("微服务：%s " % service_name)

        if opt_name in ('-b', '--branch'):
            branch = opt_value
            print("所在分支：%s" % branch)
    return service_name, branch

# execute command, and return the output
def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text


# define function: judge common version exist in common repository or not
def check_common_version(service, branch):
    num = 0
    if os.path.exists(service):
        os.chdir(service)
    os.system("git checkout %s" % branch)
    pom_common_version_tmp = execCmd("sed -n '/<artifactId>xxx/{n;p}' pom.xml")         # 需要手动配置 find common version in pom.xml
    pom_common_version = re.match(r"(.*?)<(\w*)>(.*)<(/\w*)>\n", pom_common_version_tmp)
    pom_common_version = pom_common_version.group(3)

    matchObj = re.match(r"(.*?)-"+branch+"-(.*)",pom_common_version,re.I)     # 检查 pom文件common版本中是否含有dev|test|uat|prod
    if matchObj:
        print("查看pom文件common service版本符合规范：%s" % pom_common_version)
    else:
        print("查看pom文件common service版本: %s 不符合规范,需要含有DEV/TEST/UAT/PROD关键字" % pom_common_version)
        exit(1)

#    print('pom.xml文件中 的common 版本：', pom_common_version)
    lines = execCmd("ls ~/.m2/xxx")                     # 需要手动配置 loop local common repository to get all common version
    repo_common_version_list = lines.split('\n')                                                        # clean '\n' ; change str to array
    for repo_common_version in repo_common_version_list:                                                # compare common version with common repo
        if repo_common_version == pom_common_version:
 #           print("pom.xml 所需common 版本 ", pom_common_version,"已经存在")
            num = 1
            continue
    return num

def build_common_service(branch):
    #   os.system('/usr/bin/java -jar /root/jenkins-cli.jar -auth iris:c704a1f555c4d77923f2b317bfd032eb -s http://172.16.13.101:8080/ build test &')
    #   os.system('sleep 90')
    url = 'IP'                                                                   # 需要手动配置
    username = 'username'                                                                                   # 需要手动配置
    password = 'tocken'                                                       # 需要手动配置
    server = jenkins.Jenkins(url, username, password)  # 实例化jenkins对象
    job_name='xxx'+branch                                                         # 需要手动配置

    next_build_number = server.get_job_info(job_name)['nextBuildNumber']
    server.build_job(job_name)                                              # build job
    print('没有找到我们需要的commoon 版本，现在进行编译jenkins job：%s.' % job_name)
    from time import sleep
    sleep(90)

    build_info = server.get_build_info(job_name, next_build_number)
    status = build_info['result']

    if status == "SUCCESS":
        print("构建 %s 项目构建成功， | 构建项目编号：%s" % (job_name, next_build_number))
    else:
        print("报错信息：构建 %s 项目构建失败，请前往 %s 查看报错详情！" % (job_name,job_name))
        exit(1)

if __name__ == "__main__":
    (service, branch) = get_parameter()                                                             # get parameters when run python script
    check_commom_version_result = check_common_version(service, branch)                             # check common version exist or not
    if check_commom_version_result == 0:
 #       print('没有找到我们需要的commoon 版本，现在进行编译 %s 环境 common服务',branch)
        build_common_service(branch)                                                                      # build jenkins job: common version
#        print('service & branch',service,branch)
        check_commom_version_result = check_common_version(service, branch)                         # check common version exist or not again
        if check_commom_version_result == 0:
            print('报错信息：编译了 common service，还是没有pom.xml中需要的common版本，请检查提交的pom.xml文件是否正确！')
            exit(1)
        else:
            print('执行结果: 所需的common 版本现已存在，进行下一步。')
    else:
        print('执行结果: 所需的common 版本已存在，进行下一步。')
