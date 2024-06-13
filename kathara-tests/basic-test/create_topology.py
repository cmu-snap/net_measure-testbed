from setup import setup_topology
import json 

def main():
    try:
        lab, links, nodes = setup_topology()
        with open("./tmp/lab_detail.json", "w") as f:
            json.dump({"lab_name": lab.name, "lab_hash": lab.hash}, f)
    except Exception as e:
        print(e)