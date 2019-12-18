#!/usr/bin/python
# encoding:utf8
# -*- coding: utf-8 -*-
# Realize： Run jenkins job to upgrade docker service auto on rancher dev env
# Prerequisite
#   1. Run on Linux machine.
#   2. Jenkins jar package(CLI) exist on Linux virtual machine && have configured user/passwd in jenkins
# How to execute the python script: eg: python jenkins_rancher_build.py --service=xxx-service --branch='dev'
import jenkins
import getopt
import sys
import os
import re
import ast
from time import sleep

# get parameter: service, branch
# 获取微服务名称、分支名称
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

# 执行jenkins job： 实现自动升级rancher 上的微服务
def build_rancher_integrate_upgrade(service,branch):
    #   os.system('/usr/bin/java -jar /root/jenkins-cli.jar -auth iris:c704a1f555c4d77923f2b317bfd032eb -s http://172.16.13.101:8080/ build test &')
    url = 'http://IP'                                                                                               # 需要手动配置
    username = 'username'                                                                                           # 需要手动配置
    password = 'tocken'                                                                                             # 需要手动配置
    server = jenkins.Jenkins(url, username, password)                                                               # 实例化jenkins对象
    job_name='rancher_integrate_upgrade_'+branch

    next_build_number = server.get_job_info(job_name)['nextBuildNumber']
    server.build_job(job_name,{'SERVICE_NAME':"Backend-Mate/"+service,'DOCKER_IMAGE':"registry.xxx"+service})                                              # 需要手动配置；开始构建jenkins job
    print('现在进行编译jenkins job：%s' % job_name)
    sleep(10)
    check_status = server.get_build_info(job_name, next_build_number)['building']                                   # 判断job名为job_name的job的构建的状态
    print("check_status: %s " % check_status)
    while check_status:                                                                                             # 如果此job正在构建，则执行while循环，再给它5s执行时间；如果此job执行完毕，则会跳出while循环
        sleep(5)
        check_status = server.get_build_info(job_name, next_build_number)['building']
        print("check_status: %s " % check_status)

    build_info = server.get_build_info(job_name, next_build_number)                                                 # 查看构建详细信息
    url = server.get_build_info(job_name, next_build_number)['url']                                                 # 获取所构建的jenkins job URL
    print('url:%s' % url)
    status = build_info['result']                                                                                   # 获取所构建的jenkins job 的执行结果
    if status == "SUCCESS":
        print("执行结果：构建 %s 项目构建成功， | 构建项目编号：%s" % (job_name, next_build_number))
    elif status == "ABORTED":
        print("执行结果：构建 %s 项目意外终止，请前往查看报错详情！ | 构建项目编号：%s" % (job_name, next_build_number))
        exit(1)
    elif status == "FAILURE":
        print("报错信息：构建 %s 项目构建失败，请前往查看报错详情！| 构建项目编号：%s" % (job_name, next_build_number))
        exit(1)

if __name__ == "__main__":
    (service, branch) = get_parameter()
    build_rancher_integrate_upgrade(service, branch)

