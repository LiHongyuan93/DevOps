#!/usr/bin/python

import jenkins

server = jenkins.Jenkins('http://172.16.13.101:8080', username='iris', password='c704a1f555c4d77923f2b317bfd032eb')
user = server.get_whoami()
version = server.get_version()
print('Hello %s from Jenkins %s' % (user['fullName'], version))