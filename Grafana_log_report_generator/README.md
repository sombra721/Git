commands to build the docker image:
    sudo docker build -t michael/grafana_performance .

after building the docker image, check the image ID:
    docker images

Run the grafana monitor report tool:
    docker run -t -i -v <cluster path>:/share <docker image id>
    
    cluster path: The path of the cluster to be parsed and plotting
