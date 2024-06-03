"""
Helper functions and utilities useful when setting up an experiment
"""
import subprocess
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine

def capture_traffic(lab, node_name, interface, duration, filename):
    """
    Capture traffic with tcpdump on a node for a given time
    duration and write to file.
    :param node_name: name of node to run tcpdump on
    :param interface: interface to capture traffic on
    :param duration: time to measure traffic in seconds
    :param filename: file to write output to
    :return: None
    """
    command = f'touch {filename}.txt; timeout {duration} -i {interface} > {filename}.txt &'
    stdout, stderr, retcode = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node_name, command=command, stream=False, wait=True)
    if retcode != 0:
        print(stderr)

def iperf3_server(lab, pc, port=5201):
    """ 
    Starts an iperf3 server on specific device pc as Daemon (non-blocking)
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param pc (string): Kathara device to start server on
    :param port (int): Port for server to listen on
    :rtype: (bytes, bytes, int)
    :return: (stdout, stderr, return value) 
    """
    
    command = f"iperf3 -s -D -p {port} &"
    return Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc, command=command, stream=False, wait=True)

def ptr_server(lab, pc, port=10241):
    print("starting ptr_server...")
    command = f"./igi-ptr-2.1/ptr-server -p {port} -v -h &"
    stdout, stderr, retcode = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc, command=command, stream=False, wait=True)
    return stdout.decode('utf-8')
        
def iperf3_client(lab, pc, server_ip, port=5201):
    """ 
    Starts an iperf3 client on specific device pc,
    connecting to server at ip at given port. Note that
    this function blocks.
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param pc (string): Kathara device to start client on
    :param server_ip (string): IP address of server
    :param port (int): Port for client to listen connect to
    :rtype: (bytes, bytes, int)
    :return: (stdout, stderr, return value) 
    """
    command = f"iperf3 -c {server_ip} -t 0 -p {port} &"
    stdout, stderr, retcode = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc, command=command, stream=False, wait=True)
    return stdout.decode('utf-8')

def ptr_client(lab, pc, server_ip, port=10241):
    command = f"./igi-ptr-2.1/ptr-client -n 60 -s 500B -p {port} -v -h {server_ip} &"
    return Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc, command=command, stream=False, wait=True)

def parse_iperf3_bandwidth(stdout):
    """
    Returns bandwidth in Mbits/sec
    """
    output_string = stdout.decode('utf-8')
    output_tokens = output_string.split()

    bandwidth, unit = None, None

    reversed_tokens = list(reversed(output_tokens))

    for i, token in enumerate(reversed_tokens):
        if token.endswith("/sec"):
            bandwidth, unit = float(reversed_tokens[i+1]), token
            break

    if 'Kbits' in unit:
        bandwidth /= 1000
    elif 'Gbits' in unit:
        bandwidth *= 1000
    
    return bandwidth

def pathneck(lab, client_name, server_ip):
    """
    Run pathneck from client to server
    :param client_name: name of client node
    :param server_ip: ip address of server node
    :return: String containing output of Pathneck
    run with online flag set
    """
    command = f'./pathneck-1.3/pathneck -o {server_ip}'
    stdout, stderr, retcode = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=client_name, command=command, stream=False, wait=True)
    return stdout.decode('utf-8')


def parse_pathneck_result(pathneck_result):
    """
    Returns detected bottleneck and estimated bandwidth
    :param pathneck_result: result of pathneck run such as output
    of pathneck function
    :return: tuple (bottleneck, bottleneck_bandwidth)
    the detected bottleneck and the estimated bottleneck bandwidth if found,
    else returns None
    """
    for line in pathneck_result.splitlines():
        line = line.split()
        if len(line) == 8:
            if line[5] == '1':
                bottleneck = line[0]
                bottleneck_bw = float(line[6])
                return bottleneck, bottleneck_bw
    return None, None
