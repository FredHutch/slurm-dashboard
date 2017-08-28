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

PARTITIONS_PER_ROW = 3
ITEMS_TO_SHOW = 25

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


def get_data_for_partition(data, partition):
    ids_to_remove = []
    if not partition == "restart":
        restart = data[data['PARTITION'] == 'restart']
        ids_to_remove = restart['JOBID'].tolist()
    data = data[data['PARTITION'] == partition]
    data = data[~data['JOBID'].isin(ids_to_remove)]
    return data

def get_partitions(data):
    partitions = sorted(data['PARTITION'].unique().tolist())
    partitions.remove('campus')
    partitions.remove('largenode')
    partitions.insert(0, 'largenode')
    partitions.insert(0, 'campus')
    return partitions


def get_stats_for_data(data, nodes, partition):
    if partition == "campus":
        partition = "campus*"
    nodes = nodes[nodes['PARTITION'] == partition]


    return dict(total=nodes.sum()["CPUS"],
                running=data[data['ST'] == 'R'].sum()["CPUS"],
                pending=int(data[data['ST'] == 'PD'].sum()["CPUS"]))

def get_data(featurefilter='', partitionfilter=''):
    """Get the slurm usage data."""
    squeuecmd = "squeue --format=%i;%t;%D;%C;%u;%a;%P"
    sinfocmd = "sinfo --format=%n;%c;%m;%f;%P"

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


    # df = jobs.groupby(["ACCOUNT", "USER", "PARTITION", "JOBID", "ST"]).\
    #     sum()["CPUS"].reset_index(name="CPUS").sort_values("CPUS", 0, False)
    # cols = df.columns.tolist()
    # cols.insert(0, cols.pop(1))
    # df = df[cols]

    df = jobs.sort_values("CPUS", 0, False)

    return df, nodes

app = flask.Flask(__name__) # pylint: disable=invalid-name

def rowstart(idx):
    _, remainder = divmod(idx, PARTITIONS_PER_ROW)
    return remainder == 0

def rowend(idx):
    _, remainder = divmod(idx, PARTITIONS_PER_ROW)
    return remainder == (PARTITIONS_PER_ROW - 1)

@app.route("/")
def show_table():
    """Route for /, display slurm usage data as web page."""
    jobs, nodes = get_data()
    partitions = get_partitions(jobs)

    tables = []
    for idx, partition in enumerate(partitions):
        # print("partition is {}".format(partition))
        partition_jobs = get_data_for_partition(jobs, partition)
        grouped = partition_jobs.groupby(["ACCOUNT", "USER"])\
            .sum()["CPUS"].reset_index(name="CPUS").sort_values("CPUS", 0, False)
        cols = grouped.columns.tolist()
        cols.insert(0, cols.pop(1))
        grouped = grouped[cols]
        html = grouped.head(ITEMS_TO_SHOW).to_html(index=False)
        html = html.replace("<table ", "<table id='slurm_table' ")
        tables.append(dict(get_stats_for_data(partition_jobs, nodes, partition),
                           table=html, partition=partition,
                           rowstart=rowstart(idx),
                           rowend=rowend(idx)))
    return flask.render_template('show_table.html', tables=tables,
                                 ITEMS_TO_SHOW=ITEMS_TO_SHOW)

# Run me like this:
# FLASK_APP=app.py FLASK_DEBUG=True flask run
# then visit http://localhost:5000
