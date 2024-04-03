"""
Helper functions and utilities useful when setting up an experiment
"""
import subprocess
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine

def capture_traffic(node_name, interface, duration, filename):
    """
    Capture traffic with tcpdump on a node for a given time
    duration and write to file.
    :param node_name: name of node to run tcpdump on
    :param interface: interface to capture traffic on
    :param duration: time to measure traffic in seconds
    :param filename: file to write output to
    :return: None
    """
    try:
        subprocess.check_call(f"docker exec {node_name} timeout {duration} -i {interface} > {filename} &", shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command {e.cmd} returned non-zero exit status: {e.returncode}")

def iperf3_server(lab, pc, port):
    """ 
    Starts an iperf3 server on specific device pc as Daemon
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param pc (Kathara.model.Machine): Kathara device to start server on
    :param port (int): Port for server to listen on
    :rtype: Generator[Tuple[bytes, bytes]]
    :return: A generator of tuples containing the stdout and stderr in bytes 
    """
    command = f"iperf3 -s -D -p {port} &"
    return Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc.name, command=command, stream=True, wait=True)
        
def iperf3_client(lab, pc, server_ip, port):
    """ 
    Starts an iperf3 client on specific device pc,
    connecting to server at ip at given port
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param pc (Kathara.model.Machine): Kathara device to start client on
    :param server_ip (string): IP address of server
    :param port (int): Port for client to listen connect to
    :rtype: Generator[Tuple[bytes, bytes]]
    :return: A generator of tuples containing the stdout and stderr in bytes 
    """
    command = f"iperf3 -c {server_ip} -p {port}"
    return Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc.name, command=command, stream=False, wait=True)

def parse_iperf3_bandwidth(stdout):
    """
    Returns bandwidth in Mbits/sec
    """
    output_string = stdout.decode('utf-8')
    output_tokens = output_string.split()

    bandwith, unit = None, None

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


def pathneck(client_name, server_ip):
    """
    Run pathneck from client to server
    :param client_name: name of client node
    :param server_ip: ip address of server node
    :return: String containing output of Pathneck
    run with online flag set
    """
    result = subprocess.run(['docker', 'exec', f'{client_name}', './pathneck-1.3/pathneck', '-o', f'{server_ip}'],
                            stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


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
