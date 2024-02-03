<table>
  <tr>
    <td> <img src="https://github.com/batscs/cloudflare-dns-sync/assets/31670615/58296fbd-9a48-4263-a491-308e49035aba" alt="image" width="130" height="auto"> </td>
    <td><h1>bats' Docker-ELK-Monitor</h1></td>
  </tr>
</table>

### Table of Contents  
[Introduction](#introduction)  
[Installation](#installation)  
[Dashboard](#configuration)  
[Known Issues](#help)  

<a name="introduction"/>

## Introduction  
![image](https://github.com/batscs/docker-elk-monitor/assets/31670615/2d8323f3-35fd-4c4e-8d85-7ebb3e6edf4e)

Periodically collect metrics of all your docker containers and send the data to your elasticsearch endpoint to display a monitoring dashboard in Kibana.

This is intentend to be as lightweight as possible. The script is implemented in python for a comfortable use of the elasticsearch provided python packages.

If you need help or run into problems feel free to open an issue for this repository.

#### Features:
- Automatic deployment to a docker container from docker-compose
- Automatic collection of other docker container metrics on the host system
- Automatic communication to to elasticsearch endpoint to send the collected container metrics

#### Requirements:
- Docker
- Docker Compose

<a name="installation"/>

## Installation

Download the `docker-compose.yml` file.
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/batscs/docker-elk-monitor/main/docker-compose.yml
```

Edit the following three lines under the `environment` header in the `docker-compose.yml` file to have your specific values.
If you use `monitor-0001` as the index_name, then you can import the dashboard [provided here](#configuration).
ElasticSearch will also automatically increment the last four digits each time a set data limit has been exceeded.
```yml
environment:
  - elastic_domain=http://elasticsearch:9200
  - elastic_api_key=change_to_your_api_key
  - elastic_index_name=monitor-0001 # Recommended: monitor-0001
```

After adjusting your docker-compose.yml file you can now deploy the container.
```bash
docker-compose up -d
```

<a name="configuration"/>

## Dashboard Configuration  
You can import the dashboard from the screenshot at the beginning of this README if you follow these steps:

1. Download the `dashboard.ndjson` file from this github repository.
2. Open your Kibana Web UI.
3. Go to Stack Management -> Kibana (on the left) -> Saved Objects
4. At the top right click on `Import` and upload the dashboard.ndjson file


<a name="help"/>

## Known Issues

#### Verify if script is working
To verify whether or not your script is working go to your directory with the `docker-compose.yml` file, and view the content of the `data/app.log` file.
The content of the end of the file should be in a JSON-Format, this is the response from the elasticsearch endpoint.

#### app.log file is empty
If the app.log file is empty there probably is an issue with the connection to the elasticsearch endpoint. If your elasticsearch server runs in a docker container on the same host, then make sure they are in the same network. I recommend using this [github repository](https://github.com/deviantony/docker-elk) for setting up the ELK-Stack in docker. This is also the configuration I've been using.

Add these lines to the very end of your docker-compose.yml for the monitor, make sure to change the value after `name` to the same network your elasticsearch container is in.
```yml
networks:
  default:
    name: my-network
    external: true
    driver: bridge
```
