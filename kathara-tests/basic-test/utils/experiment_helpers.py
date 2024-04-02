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

def setup_device(lab, device_name, image, links, config):
	"""
	Creates a new Kathara machine with the startup commands given in config
	:param lab (Kathara.model.Lab): Kathara lab scenario
	:param device_name (string): Name of new device
	:param image (string): Name of image to start device with
	:param links (list[string]): Links to connect device to
	:param config (list[string]): startup commands for device
	:rtype: Kathara.model.Machine
	:return: Kathara machine object
	"""
	device = lab.new_machine(device_name, **{"image": image})
	for l in links:
		lab.connect_machine_to_link(device.name, l)

	lab.create_file_from_list(config, f"{device.name}.startup")
	return device

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
	return Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=pc.name, command=command, stream=True, wait=True)

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
