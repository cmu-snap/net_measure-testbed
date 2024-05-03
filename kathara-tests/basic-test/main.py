import subprocess
import sys
import threading
import os
from utils.experiment_helpers import iperf3_server, iperf3_client, capture_traffic, pathneck, parse_pathneck_result, parse_iperf3_bandwidth, close_iperf3_server
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
from setup import remove_link, read_state_json, add_link, update_tables
import seaborn as sns
import matplotlib.pyplot as plt
import time


def main():

    try:
        state = read_state_json()
        nodes = state['nodes']
        lab = Kathara.get_instance().get_lab_from_api(state['lab_hash'])

        for node,_ in nodes.items():
            (stdout, stderr, retcode) = iperf3_server(lab, node)

        # run iperf between every pair of nodes
        results = {}
        for dest, (ip, _) in nodes.items():
            for source, (_, _) in nodes.items():
                print(dest, " ", ip, " ", source, " ", "")
                if(source != dest and source[0] != 'r' and dest[0] != 'r' ):
                    (stdout, stderr, retcode) = iperf3_client(lab, source, ip)
                    if(retcode == 0):
                        results[(source,dest)] = parse_iperf3_bandwidth(stdout)
                    else:
                        results[(source, dest)] = stderr
        print(*(results.items()), sep='\n')

        for node,_ in nodes.items():
            close_iperf3_server(lab, node)


        # do traceroute/ping and measure RTT
        # setup iperf server on bottleneck link destination
        # global variables
        # n_iter = 20
        # bottleneck_bandwidth = []
        # data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}

        # server = {'name': 's1', 'ip': '10.0.4.4'}
        # contesting_client = 'c2'
        # client = 'c1'
        # bottleneck_link_dest = {'name': 'r6', 'ip': '10.0.8.4'}
        # bottleneck_router = 'r5'
        # iperf3_server(lab, bottleneck_link_dest['name'])

        # iperf3_client(lab, contesting_client, bottleneck_link_dest['ip'])
        
        # generate background traffic
        # thread = threading.Thread(target=iperf3_client, args=(lab, contesting_client, bottleneck_link_dest['ip']))
        # thread.start()
        
        
        # capture traffic on bottleneck router
        # capture_traffic(lab, bottleneck_router, 'eth1', '180', 'traffic-capture')
        # run pathneck from client to server
        # for i in range(n_iter):
        #     result = pathneck(lab, client, server['ip'])
        #     print(result)
        #     bottleneck, bottleneck_bw = parse_pathneck_result(result)
        #     if bottleneck is not None:
        #         bottleneck_bandwidth.append(bottleneck_bw)
        #         data[bottleneck].append(bottleneck_bw)

        # # plot bandwidth test results
        # total_data = [data[key] for key in data]
        # sns.stripplot(data=total_data, jitter=True, color='black')
        # sns.boxplot(total_data)
        # plt.xlabel('Hop ID')
        # plt.ylabel('Measured bandwidth ')
        # plt.title(f'Bandwidth [Mbits/sec] distributions of detected bottlenecks')
        # plt.savefig('pathneck-boxplot1')
        # plt.show()
        
        
        # change link to s1

        link1 = (("r1", "10.0.4.2"), ("s1", "10.0.4.4"), (1, 12500, 10))
        link2 = (("r1", "10.0.6.2"), ("r2", "10.0.6.4"), (200, 12500, 1))
        add_link(lab, link1)
        remove_link(lab, link2)

        # reroute
        update_tables(lab)
        state = read_state_json()
        nodes = state['nodes']

        for node,_ in nodes.items():
            (stdout, stderr, retcode) = iperf3_server(lab, node)

        results = {}
        for dest, (ip, _) in nodes.items():
            for source, (_, _) in nodes.items():
                if(source != dest and source[0] != 'r' and dest[0] != 'r' ):
                    (stdout, stderr, retcode) = iperf3_client(lab, source, ip)
                    if(retcode == 0):
                        results[(source,dest)] = parse_iperf3_bandwidth(stdout)
                    else:
                        results[(source, dest)] = stderr
        print(*(results.items()), sep='\n')

        for node,_ in nodes.items():
            (stdout, stderr, retcode) = close_iperf3_server(lab, node)
        
        # global variables
        # n_iter = 20
        # bottleneck_bandwidth = []
        # data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}

        # server = {'name': 's1', 'ip': '10.0.4.4'}
        # contesting_client = 'c2'
        # client = 'c1'
        # bottleneck_link_dest = {'name': 'r6', 'ip': '10.0.8.4'}
        # bottleneck_router = 'r5'
        # iperf3_server(lab, bottleneck_link_dest['name'])

        # iperf3_client(lab, contesting_client, bottleneck_link_dest['ip'])
        
        # generate background traffic
        # thread = threading.Thread(target=iperf3_client, args=(lab, contesting_client, bottleneck_link_dest['ip']))
        # thread.start()
        
    
        # capture traffic on bottleneck router
        # capture_traffic(lab, bottleneck_router, 'eth1', '180', 'traffic-capture')
        # run pathneck from client to server
        # for i in range(n_iter):
        #     result = pathneck(lab, client, server['ip'])
        #     print(result)
        #     bottleneck, bottleneck_bw = parse_pathneck_result(result)
        #     if bottleneck is not None:
        #         bottleneck_bandwidth.append(bottleneck_bw)
        #         data[bottleneck].append(bottleneck_bw)

        # # plot bandwidth test results
        # total_data = [data[key] for key in data]
        # sns.stripplot(data=total_data, jitter=True, color='black')
        # sns.boxplot(total_data)
        # plt.xlabel('Hop ID')
        # plt.ylabel('Measured bandwidth ')
        # plt.title(f'Bandwidth [Mbits/sec] distributions of detected bottlenecks')
        # plt.savefig('pathneck-boxplot2')
        # plt.show()

    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()

