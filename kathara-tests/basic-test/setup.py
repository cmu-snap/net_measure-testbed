import os
import ast
import importlib
from queue import PriorityQueue
import json
import argparse
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
from collections import defaultdict

def dijkstra(graph, start):
    """
    Function to compute the shortest path from a source node to all other nodes in the graph
    param: graph: the graph of the network
    param: start: the source/start node from where minimum distance to other nodes is calculated.
    return: Distance dictionary, where each element is a tuple of distance from source node and 
    the previous node in the shortest path from the source.
    """
    # Initialize the distance dictionary and set the distance of the start node to 0
    dist = {}
    for node in graph:
        dist[node] = [float('inf'), node]
    dist[start][0] = 0

    # Initialize the priority queue and add the start node with distance 0
    pq = PriorityQueue()
    pq.put((0, start))

    # Traverse the graph using BFS and update the distance for each neighbor node
    while not pq.empty():
        current_dist, current_node = pq.get()
        if current_dist > dist[current_node][0]:
            continue
        for neighbor, weight in graph[current_node]:
            # weights are bandwidth values
            distance = current_dist + 1. / weight[0]
            if distance < dist[neighbor][0]:
                dist[neighbor] = [distance, current_node]
                pq.put([distance, neighbor])
<<<<<<< HEAD
=======

>>>>>>> 9d77c960f09c1c8f16e49614660907df1fa1b5b7
    # Return the distance dictionary
    return dist

def build_image(img_name, img_path):
    """
    Build docker image
    :param img_name: name of image
    :param img_path: path of Dockerfile
    :return: None
    """
    cmd = f"docker build -t {img_name} {img_path}"
    print(cmd)
    os.system(cmd)

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

def create_device(lab, device_name, image, links, cmds):
    """
    Create and start device
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param device_name: name of device
    :param ip: container ip address
    :param img_name: name of image
    :param link: link name on eth0 interface
    :param ip: ip address of node on link
    :return: None
    """
    print(f'Setting up device {device_name} with arguments ({image}, {links}, {cmds})')
    
    device = setup_device(lab, device_name, image, links, cmds)
    print(f'Succesfully added device {device_name}')

def attach(lab, ip, link_name, device_name, interface, tc_params):
    """
    Attach container to subnet
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param ip (string): 
    :param link_name: name of link/collision domain
    :param device_name: name of device
    :param tc_params: tuple (bandwidth, burst, latency)
    :return: None
    """
    configure_link(lab, device_name, interface, tc_params)


def remove_link(lab, link):
    """
    Remove link from lab
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param link: name of link (i.e. Kathara collision domain)
    :return: None
    """
    link = lab.get_link(link)
    Kathara.get_instance().undeploy_link(link)

def remove_device(lab, device_name):
    """
    Remove device from lab
    :param lab (Kathara.model.Lab): Kathara lab scenario

    :param device_name: name of device
    :return: None
    """
    device = lab.get_machine(device_name)
    
    Kathara.get_instance().undeploy_machine(device)


def add_route(lab, device_name, ip_range, gateway_ip, interface):
    """
    :param lab (Kathara.model.Lab): Kathara lab scenario
    Add routing rule for packets from a device to a subnet
    :param device_name: name of src device
    :param ip_range: destination subnet
    :param gateway_ip: ip of next hop gateway
    :param interface: interface through which packets will be sent
    :return: None
    """
    cmd = f"ip route add {ip_range}" \
          f" via {gateway_ip} dev {interface}"
    (stout, stderr, cmdValue) = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=device_name, command=cmd, stream=False, wait=True)

    if cmdValue != 0:
        cmd = f"ip route change {ip_range}" \
              f" via {gateway_ip} dev {interface}"

        (stout, stderr, cmdValue) = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=device_name, command=cmd, stream=False, wait=True)



def del_route(lab, machine_name, ip_range):
    """
    Deleting routing rule corresponding to a link
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param machine_name (string): name of src machine
    :param ip_range (string): destination node ip address
    :return: None
    """
    cmd = f"ip route delete {ip_range}"
    (stdout, stderr, cmdValue) = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=machine_name, command=cmd, stream=False, wait=True)
    


def write_state_json(nodes, links, node_vs_ip, node_vs_eth):
    """
    Reads from the current state (consisting of all the input parameters of this function)
    and stores it in the state.json file
    :param nodes: node information in the format as defined in json file.
    :param links: link information in the format as defined in json file.
    :param node_vs_ip: list of ips associated with the nodes
    :param: node_vs_eth: the highest ethernet interface number used.
    :return: the current state of the graph in dictionary format
    """
    with open("./tmp/state.json", "w") as f:
        json.dump({"nodes": nodes, "links": links, "node_vs_ip": node_vs_ip, "node_vs_eth": node_vs_eth}, f, indent=4)


def read_state_json():
    """
    Read the state json file which stores the current state.
    :param: None
    :return: the current state of the graph in dictionary format
    """
    with open("./tmp/state.json", "r") as f:
        current_state = json.load(f)
    return current_state


def generate_link_param(node_vs_eth, link_info):
    """
    Generates more parameters from the limited set of info taken form config file.
    :param node_vs_eth: contains the node vs ethernet number mapping to decide the next
    ethernet available to use for the link.
    :param link_info: contains the info provided for the link in the config file or add
    and delete link commands.
    :return: link_name, node_vs_eth, link_param
    """
    node0 = link_info[0]
    node1 = link_info[1]
    link_name = node0[0] + "-" + node1[0]
    subnet_ip = ".".join(node0[1].split(".")[:3]) + ".0/24"
    if node0[0] not in node_vs_eth:
        node_vs_eth[node0[0]] = 0
    else:
        node_vs_eth[node0[0]] += 1
    if node1[0] not in node_vs_eth:
        node_vs_eth[node1[0]] = 0
    else:
        node_vs_eth[node1[0]] += 1
    link_param = (subnet_ip, ((node0[0], node0[1], "eth" + str(node_vs_eth[node0[0]])),
                              (node1[0], node1[1], "eth" + str(node_vs_eth[node1[0]]))), link_info[2])
    return link_name, node_vs_eth, link_param


def configure_link(lab, node, interface, tc_params):
    """
    Configure interface on node
    :param lab (Kathara.model.Lab): Kathara lab scenario
    :param node (string): node to configure
    :param interface (string): interface to configure
    :param tc_params: tuple (bandwidth, burst, latency)
    :return: None
    """
    print(f'Configuring node {node} with arguments ({interface}, {tc_params[0]}, {tc_params[1]}, {tc_params[2]})')

    bandwidth, burst, latency = tc_params
    cmd_bandwidth = f"tc qdisc add dev {interface} " \
                    f"root handle 1: tbf rate {bandwidth}mbit burst {burst}kb latency 10ms"
    cmd_latency = f"tc qdisc add dev {interface} " \
                  f"parent 1:1 handle 10: netem delay {latency}ms"

    (stdout1, stderr1, cmd_value_bandwidth) = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node, command=cmd_bandwidth, stream=False, wait=True)
    (stdout2, stderr2, cmd_value_latency) = Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node, command=cmd_latency, stream=False, wait=True)

    # Error handling for cmd_bandwidth and cmd_latency
    if cmd_value_bandwidth != 0 or cmd_value_latency != 0:
        clear_child = f"tc qdisc del dev {interface} parent 1:1 handle 10"
        clear_cmd = f"tc qdisc del dev {interface} root"
        Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node, command=clear_child, stream=False, wait=True)
        Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node, command=clear_cmd, stream=False, wait=True)
        
        Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node, command=cmd_bandwidth, stream=False, wait=True)
        Kathara.get_instance().exec(lab_hash=lab.hash, machine_name=node, command=cmd_latency, stream=False, wait=True)
    print(f'Completed configuring node {node}')

<<<<<<< HEAD
def setup_topology():
    """
    Sets up configured topology as described by args parameters
    :param args: parameters describing network topology
    :
    :return: 
    """
    try:
        # parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-al', '--add-link', type=str, required=False, default=None,
                            help='link info of link to add')
        parser.add_argument('-rl', '--remove-link', type=str, required=False,
                            default=None, help='link info of link to remove')
        parser.add_argument('-c', '--config', type=str, required=False, default='topology_config',
                            help='config file describing topology to set up '
                                '(see examples folder for examples)')
        args = parser.parse_args()

=======
def main(args):
    """
    Sets up configured topology as described by args parameters
    :param args: parameters describing network topology
    :return: None
    """
    try:
>>>>>>> 9d77c960f09c1c8f16e49614660907df1fa1b5b7
        lab = Lab("basic-test")
        # if args.add_link is not None:
        #     print(f'Adding link: {args.add_link}')
        #     # Handling add_link functionality
        #     current_state = read_state_json()
        #     node_vs_eth = current_state["node_vs_eth"]
        #     link_info = ast.literal_eval(args.add_link)
        #     link_name, node_vs_eth, link_param = generate_link_param(node_vs_eth, link_info)
        #     current_state["links"][link_name] = link_param
        #     links = current_state["links"]
        #     nodes = current_state["nodes"]
        #     create_subnet(link_param[0], link_name)
        #     endpoints = link_param[1]
        #     tc_params = link_param[2]
        #     attach(endpoints[0][1], link_name, endpoints[0][0], endpoints[0][2], tc_params)
        #     attach(endpoints[1][1], link_name, endpoints[1][0], endpoints[1][2], tc_params)
        # elif args.remove_link:
        #     print(f'Removing link: {args.remove_link}')
        #     # Handling remove_link functionality
        #     current_state = read_state_json()
        #     node_vs_eth_not_used = {}
        #     link_info = ast.literal_eval(args.remove_link)
        #     link_name, node_vs_eth_not_used, link_param = generate_link_param(node_vs_eth_not_used, link_info)
        #     node_vs_eth = current_state["node_vs_eth"]
        #     endpoints = link_param[1]
        #     if link_name in current_state["links"]:
        #         start_node = endpoints[0][0]
        #         dest_node = endpoints[1][0]
        #         # deleting direct connections due to this link in routing tables
        #         for dest_node_ip in current_state["node_vs_ip"][dest_node]:
        #             del_route(start_node, dest_node_ip)
        #         # because bidirectional
        #         for start_node_ip in current_state["node_vs_ip"][start_node]:
        #             del_route(dest_node, start_node_ip)
        #         # deleting from links data structure
        #         del current_state["links"][link_name]
        #     else:
        #         print("Link being deleted not present.")
        #         exit()
        #     links = current_state["links"]
        #     nodes = current_state["nodes"]
        #     detach(link_name, endpoints[0][0])
        #     detach(link_name, endpoints[1][0])
        #     remove_subnet(link_name)  # remove subnet after detaching containers or containers will get killed.
        # Reading and storing information from the config.py file
        if args.config is not None:
            config = importlib.import_module(args.config)
            start_up_cmds = defaultdict(list)
            start_up_links = defaultdict(list)
            node_vs_ip = {}
            node_vs_eth = {}
            for node_name, node_param in config.nodes.items():
                if node_name not in node_vs_ip:
                    node_vs_ip[node_name] = []
                node_vs_ip[node_name].append(node_param[0])
            # update links to include interface and link_name
            links = {}
            for link_info in config.links:
                link_name, node_vs_eth, link_param = generate_link_param(node_vs_eth, link_info)
    
                source, dest = link_param[1][0][0], link_param[1][1][0]

                # set ip addresses for interfaces
                cmd_source = f'ip address add {link_param[1][0][1]}/24 dev {link_param[1][0][2]}'
                cmd_dest = f'ip address add {link_param[1][1][1]}/24 dev {link_param[1][1][2]}'
                start_up_cmds[source].append(cmd_source)
                start_up_cmds[dest].append(cmd_dest)

                # add collision domains
                start_up_links[source].append(link_name)
                start_up_links[dest].append(link_name)
                links[link_name] = link_param

            nodes = config.nodes

            # uncomment to rebuild
            # build_image("katharatestimage", ".")

            # create devices
            for node_name, node_param in nodes.items():
                create_device(lab, node_name, "katharatestimage", start_up_links[node_name], start_up_cmds[node_name])
 
            Kathara.get_instance().deploy_lab(lab)

            # attach devices to collision domains
            for link_name, link_param in links.items():
                endpoints = link_param[1]
                tc_params = link_param[2]
                try:
                    attach(lab, endpoints[0][1], link_name, endpoints[0][0], endpoints[0][2], tc_params)
                    attach(lab, endpoints[1][1], link_name, endpoints[1][0], endpoints[1][2], tc_params)
                except Exception as e:
                    print(e)
        else:
            print("Invalid Argument")

<<<<<<< HEAD
=======


>>>>>>> 9d77c960f09c1c8f16e49614660907df1fa1b5b7
        # Using Dijkstra to configure routing tables with add route function above
        graph = {}
        connections = {}
        # Create Graph
        for link_name, link_param in links.items():
            endpoints = link_param[1]
            tc_params = link_param[2]

            if endpoints[0][0] not in node_vs_ip:
                node_vs_ip[endpoints[0][0]] = []
            node_vs_ip[endpoints[0][0]].append(endpoints[0][1])
            if endpoints[1][0] not in node_vs_ip:
                node_vs_ip[endpoints[1][0]] = []
            node_vs_ip[endpoints[1][0]].append(endpoints[1][1])

            if endpoints[0][0] not in graph:
                graph[endpoints[0][0]] = []
                connections[endpoints[0][0]] = {}
            graph[endpoints[0][0]].append((endpoints[1][0], tc_params))
            connections[endpoints[0][0]][endpoints[1][0]] = (
                endpoints[1][1], endpoints[0][2])  # ip of other node,eth of itself
            if endpoints[1][0] not in graph:
                graph[endpoints[1][0]] = []
                connections[endpoints[1][0]] = {}
            graph[endpoints[1][0]].append((endpoints[0][0], tc_params))
            connections[endpoints[1][0]][endpoints[0][0]] = (endpoints[0][1], endpoints[1][2])

        for start_node in graph:
            dist = dijkstra(graph, start_node)
            hops = []
            for node in graph:
                if node == start_node:
                    continue
                prev_node = dist[node][1]
                next_hop = node
                while prev_node != start_node and dist[prev_node][0] != float('inf'):
                    next_hop = prev_node
                    prev_node = dist[prev_node][1]
                if dist[prev_node][0] == float('inf'):
                    continue
                hops.append((node, next_hop))
            print(f"\nStart Node = {start_node}")
            for dest_node, next_hop_node in hops:
                next_hop_node_ip = connections[start_node][next_hop_node][0]
                interface = connections[start_node][next_hop_node][1]
                for dest_node_ip in node_vs_ip[dest_node]:
<<<<<<< HEAD
=======
                    print(dest_node_ip)
                    print(next_hop_node_ip)
>>>>>>> 9d77c960f09c1c8f16e49614660907df1fa1b5b7
                    add_route(lab, start_node, dest_node_ip, next_hop_node_ip, interface)
                print(f"Destination Node = {dest_node}, Next hop = {next_hop_node}")

        # Store the current state to state.json file
        write_state_json(nodes, links, node_vs_ip, node_vs_eth)
<<<<<<< HEAD
        return (lab, links, nodes)
        # Kathara.get_instance().undeploy_lab(lab_name=lab.name)
=======
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
>>>>>>> 9d77c960f09c1c8f16e49614660907df1fa1b5b7
    except Exception as e:
        print(e)
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except KeyboardInterrupt:
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)

<<<<<<< HEAD
=======

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-al', '--add-link', type=str, required=False, default=None,
                        help='link info of link to add')
    parser.add_argument('-rl', '--remove-link', type=str, required=False,
                        default=None, help='link info of link to remove')
    parser.add_argument('-c', '--config', type=str, required=False, default='topology_config',
                        help='config file describing topology to set up '
                             '(see examples folder for examples)')
    args = parser.parse_args()
    # print(args)
    main(args)
>>>>>>> 9d77c960f09c1c8f16e49614660907df1fa1b5b7
