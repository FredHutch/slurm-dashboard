#! /usr/bin/env python

"""
Simple python3 web app to show slurm cluster usage stats.
Based on https://git.io/v53W2
and https://git.io/v53Ww .
"""

# stdlib imports
from io import StringIO
import socket

# third-party imports
import pandas
import paramiko
import flask

def run_ssh_command(command):
    """
    Run an ssh command. The 'ssh' executable is not required
    as this uses the pure-python paramiko library.
    """
    # print("trying to run {}".format(command))

    username = 'dtenenba'
    # This key restricts users to squeue and sinfo commands,
    # see dashboard_wrapper.sh.
    key_file = 'slurmdashboard_rsa'
    host = "rhino" # let DNS load-balance between different rhinos.

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # how bad is this?

    ssh.connect(host, key_filename=key_file, username=username)
    _, stdout, _ = ssh.exec_command(command)
    # TODO check for errors?
    ret = "".join(stdout.readlines())
    # print("about to return: \n{}".format(ret))
    return ret



def get_local_ip():
    """requires internet access"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    local_ip = sock.getsockname()[0]
    sock.close()
    return local_ip

def is_at_home():
    """Is dan at home without hutch network access?"""
    return get_local_ip().startswith("192.168.")


def get_data(featurefilter='', partitionfilter=''):
    """Get the slurm usage data."""
    squeuecmd = "squeue --format=%i;%t;%D;%C;%a;%u"
    sinfocmd = "sinfo --format=%n;%c;%m;%f"

    # TODO test this
    if partitionfilter != '':
        squeuecmd += ' --partition={}'.format(partitionfilter)

    if is_at_home():
        squeue_fh = open("squeue.txt")
        sinfo_fh = open("sinfo.txt")
    else:
        squeue = run_ssh_command(squeuecmd)
        sinfo = run_ssh_command(sinfocmd)
        squeue_fh = StringIO(squeue)
        sinfo_fh = StringIO(sinfo)


    jobs = pandas.read_table(squeue_fh, sep=';')
    nodes = pandas.read_table(sinfo_fh, sep=';')

    squeue_fh.close()
    sinfo_fh.close()


    if featurefilter != '':
        nodes = nodes[(nodes['FEATURES'].str.contains(featurefilter))]

    data = dict(table=jobs.groupby(["ACCOUNT", "USER"]).sum()["CPUS"].reset_index(name="CPUS"),
                total=nodes.sum()["CPUS"],
                running=jobs[jobs['ST'] == 'R'].sum()["CPUS"],
                pending=jobs[jobs['ST'] == 'PD'].sum()["CPUS"])

    return data

app = flask.Flask(__name__) # pylint: disable=invalid-name

@app.route("/")
def show_table():
    """Route for /, display slurm usage data as web page."""
    all_data = get_data()
    data = all_data['table']
    html = data.to_html().replace("<table ", "<table id='slurm_table' ")
    return flask.render_template('show_table.html', table=html,
                                 total=all_data['total'],
                                 running=all_data['running'],
                                 pending=all_data['pending'])

# Run me like this:
# FLASK_APP=app.py FLASK_DEBUG=True flask run
# then visit http://localhost:5000
