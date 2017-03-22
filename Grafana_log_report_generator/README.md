commands to build the docker image:<\br>
    sudo docker build -t michael/grafana_performance .

after building the docker image, check the image ID:<\br>
    docker images

Run the grafana monitor report tool:<\br>
    docker run -t -i -v \<cluster path\>:/share \<docker image id\><\br><\br> 
    cluster path: The path of the cluster to be parsed and plotting
