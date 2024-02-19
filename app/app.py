import argparse
import docker
import pprint
from elastic_api import ElasticAPI
import re as regex

# --------------------------------------------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser(
    prog="bats' ELK-Monitor",
    description='Application monitoring your docker container stats.',
    epilog='github.com/batscs/docker-elk-monitor')

parser.add_argument('elastic_domain')

parser.add_argument('elastic_api_key')

parser.add_argument('elastic_index_name')

parser.add_argument('-o', '--offline', action='store_true',
                    help="dont upload data to elasticsearch endpoint")

parser.add_argument('-v', '--verbose', action='store_true',
                    help="show debug & informational messages")

args = parser.parse_args()

# If false no debug prints will appear
debug = args.verbose

# If false no data will be submitted to ElasticSearch, used for debugging pre-upload
elastic_upload = not args.offline  # Default: True

# ElasticSearch Deployment Server
elastic_domain = args.elastic_domain

# ElasticSearch API Key with Kibana Authorization
elastic_api_key = args.elastic_api_key

# ElasticSearch Index Name
elastic_index_name = args.elastic_index_name

# --------------------------------------------------------------------------------------------------------------------------------

client = docker.from_env()
elastic = ElasticAPI(elastic_domain, elastic_api_key, elastic_index_name, debug=debug, connect=elastic_upload)
pp = pprint.PrettyPrinter(indent=4)

collapse_stacks = True

# --------------------------------------------------------------------------------------------------------------------------------

def main():
    stats = get_stats()

    total = {
        "name": "total",
        "type": "total",
        "cpu": 0,
        "memory.b": 0,
        "tx.b": 0,
        "rx.b": 0,
        "pids": 0,
    }

    for container in stats:
        for stat in container:
            if stat != "type" and stat != "name":
                total[stat] += container[stat]

        elastic.append_data(container)

    elastic.append_data(total)
    elastic.submit_data()


# --------------------------------------------------------------------------------------------------------------------------------

# this is taken directly from docker client:
# https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/client/stats.go#L309
def calculate_cpu_percent(status):
    cpuDelta = status["cpu_stats"]["cpu_usage"]["total_usage"] - status["precpu_stats"]["cpu_usage"]["total_usage"]
    systemDelta = status["cpu_stats"]["system_cpu_usage"] - status["precpu_stats"]["system_cpu_usage"]
    # print("systemDelta: "+str(systemDelta)+" cpuDelta: "+str(cpuDelta))
    cpuPercent = (cpuDelta / systemDelta) * (status["cpu_stats"]["online_cpus"]) * 100
    cpuPercent = round(cpuPercent, 2)
    return cpuPercent

# ---------------

def add(collection, containername, stats):
    found = False
    for container in collection:
        if container["name"] == containername:
            found = True
            for stat in stats:
                container[stat] += stats[stat]
                container["type"] = "stack"

    if not found:
        container = (stats)
        container["name"] = containername
        container["type"] = "container"
        collection.append(container)

# --------------------------------------------------------------------------------------------------------------------------------

def get_stats():
    result = []
    for container in client.containers.list():
        name = "Unknown"
        try:
            data = {}
            stats = container.stats(decode=None, stream=False)
            name = stats['name']

            match = regex.search("\/(.*)(-|_)(.*)(-|_)[0-9]", name)
            # if container is part of stack, use stack name instead of full container name
            if collapse_stacks and bool(match):
                name = match.group(1)

            data["cpu"] = calculate_cpu_percent(stats)
            # Memory Usage subtracted with inactive_files to mirror behavior of 'docker stats' and linux ram calculation, ignoring buffer/cache
            data["memory.b"] = stats["memory_stats"]["usage"] - stats["memory_stats"]["stats"]["inactive_file"]
            data["tx.b"] = stats["networks"]["eth0"]["tx_bytes"]
            data["rx.b"] = stats["networks"]["eth0"]["rx_bytes"]
            data["pids"] = stats["pids_stats"]["current"]

            if data["cpu"] >= 0:
                print(f"Fetched Information for Docker Container {stats['name']}")
                add(result, name, data)
            else:
                print(f"Error while fetching Information about {name} Container (Negative CPU-Usage)")
        except:
            print(f"Error while fetching Information about {name} Container")

    return result

# --------------------------------------------------------------------------------------------------------------------------------

# Execute main()-function if this script is being run as a standalone
if __name__ == '__main__':
    main()
