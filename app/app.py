import argparse
import docker
import pprint
from elastic_api import ElasticAPI

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


# --------------------------------------------------------------------------------------------------------------------------------

def main():
    stats = get_stats()

    total = {
        "container": "total",
        "cpu": 0,
        "memory_mb": 0,
        "tx_mb": 0,
        "rx_mb": 0,
        "pids": 0,
        "storage_gb": 0
    }

    for container in stats:
        document = {}
        document["container"] = container
        for stat in stats[container]:
            document[stat] = stats[container][stat]
            total[stat] += document[stat]

        elastic.append_data(document)

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


# --------------------------------------------------------------------------------------------------------------------------------

def get_stats():
    result = {}
    for container in client.containers.list():
        name = "Unknown"
        try:
            data = {}
            stats = container.stats(decode=None, stream=False)
            name = stats['name']
            data["cpu"] = calculate_cpu_percent(stats)
            data["memory_mb"] = round(stats["memory_stats"]["usage"] / 1000 / 1000, 2)
            data["tx_mb"] = round(stats["networks"]["eth0"]["tx_bytes"] / 1000 / 1000, 2)
            data["rx_mb"] = round(stats["networks"]["eth0"]["rx_bytes"] / 1000 / 1000, 2)
            data["pids"] = stats["pids_stats"]["current"]
            result[name] = data
            print(f"Fetched Information for Docker Container {name}")
        except:
            print(f"Error while fetching Information about {name} Container")

    # Because Storage-Usage is not in container.stats()
    info = client.df()
    for container in info['Containers']:
        if 'SizeRw' in container:
            for name in container["Names"]:
                if name in result:
                    result[name]["storage_gb"] = round(container["SizeRw"] / 1000 / 1000 / 1000, 3)

    return result

# --------------------------------------------------------------------------------------------------------------------------------

# Execute main()-function if this script is being run as a standalone
if __name__ == '__main__':
    main()
