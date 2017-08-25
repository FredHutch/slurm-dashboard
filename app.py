#! /usr/bin/env python

from io import StringIO

import pandas
import paramiko


def run_ssh_command(command):

    # print("trying to run {}".format(command))

    username = 'dtenenba'
    key_file = 'slurmdashboard_rsa'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # how bad is this?

    ssh.connect("rhino", key_filename=key_file, username=username)
    _, stdout, _ = ssh.exec_command(command)
    # TODO check for errors?
    ret = "".join(stdout.readlines())
    # print("about to return: \n{}".format(ret))
    return ret





featurefilter=''
partitionfilter=''

squeuecmd = "squeue --format=%i;%t;%D;%C;%a;%u"
sinfocmd = "sinfo --format=%n;%c;%m;%f"

if partitionfilter != '':
    squeuecmd += ' --partition={}'.format(partitionfilter)

squeue = run_ssh_command(squeuecmd)
sinfo = run_ssh_command(sinfocmd)

# import IPython;IPython.embed()


jobs = pandas.read_table(StringIO(squeue), sep=';')
nodes = pandas.read_table(StringIO(sinfo), sep=';')


if featurefilter != '':
    nodes = nodes[(nodes['FEATURES'].str.contains(featurefilter))]

print(jobs.groupby(["ACCOUNT","USER"]).sum()["CPUS"])

print('\n CPU core Inventory:')
print('Total:', nodes.sum()["CPUS"])
print('Running:', jobs[jobs['ST'] == 'R'].sum()["CPUS"])
print('Pending:', jobs[jobs['ST'] == 'PD'].sum()["CPUS"])
