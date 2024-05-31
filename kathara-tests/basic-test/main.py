import subprocess
import sys
import os
from utils.experiment_helpers import iperf3_server, iperf3_client, capture_traffic, pathneck, parse_pathneck_result, parse_iperf3_bandwidth, ptr, ptr_client, ptr_server
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
from setup import setup_topology
import seaborn as sns
import matplotlib.pyplot as plt
import docker
import time

def main():

    try:
        lab, links, nodes = setup_topology()

        # print(nodes)
        # for node in nodes:
        #     (stdout, stderr, retcode) = iperf3_server(lab, node)

        # run iperf between every pair of nodes
        # results = {}
        # for dest, (ip, _) in nodes.items():
        #     for source in nodes:
        #         if(source != dest and source[0] != 'r' and dest[0] != 'r' ):
        #             (stdout, stderr, retcode) = iperf3_client(lab, dest, ip)
        #             if(retcode == 0):
        #                 results[(source,dest)] = parse_iperf3_bandwidth(stdout)
        #             else:
        #                 results[(source, dest)] = stderr
        # print(results)
        # setup iperf server on bottleneck link destination
        # global variables
        n_iter = 20
        bottleneck_bandwidth = []
        data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}

        server = {'name': 's1', 'ip': '10.0.4.4'}
        contesting_client = 'c2'
        client = 'c1'
        bottleneck_link_dest = {'name': 'r6', 'ip': '10.0.8.4'}
        bottleneck_router = 'r5'
        # iperf3_server(lab, bottleneck_link_dest['name'])
        iperf3_server(lab, 's1')
        # ptr_server(lab, 'r2')


        # generate background traffic
        pid = os.fork()
        if pid == 0:
            # iperf3_client(lab, contesting_client, bottleneck_link_dest['ip'])
            # ptr_client(lab, 'c1', 'r2')
            return
        else:
            # capture traffic on bottleneck router
            print("ptr_client...")
            # ptr_client(lab, 'c1', 'r2')
            capture_traffic(lab, bottleneck_router, 'eth1', '180', 'traffic-capture')
            # run pathneck from client to server
            for i in range(n_iter):
                result = pathneck(lab, client, server['ip'])
                # result = ptr(lab, client, server['ip'])
                print("result:",result)
                print("end")
                bottleneck, bottleneck_bw = parse_pathneck_result(result)
                if bottleneck is not None:
                    bottleneck_bandwidth.append(bottleneck_bw)
                    data[bottleneck].append(bottleneck_bw)

            # plot bandwidth test results
            total_data = [data[key] for key in data]
            sns.stripplot(data=total_data, jitter=True, color='black')
            sns.boxplot(total_data)
            plt.xlabel('Hop ID')
            plt.ylabel('Measured bandwidth ')
            plt.title(f'Bandwidth [Mbits/sec] distributions of detected bottlenecks')
            plt.savefig('pathneck-boxplot')
            plt.show()

            Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except Exception as e:
        print(e)
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except KeyboardInterrupt:
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)

main()

