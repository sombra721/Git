commands to build the docker image:<p>
#sudo docker build -t michael/grafana_performance .

after building the docker image, check the image ID:<p>
#docker images

Run the grafana monitor report tool:<p>
#docker run -t -i -v \<cluster path\>:/share \<docker image id\><p><p>
cluster path: The path of the cluster to be parsed and plotting
