#!/usr/bin/python 
# -*- coding: utf-8 -*-
__author__ = "Michael Tsai"
'''
The program parallelly connect to the virtual machines and SCG devices to simulate the AP and clients behaviors.

The steps and environment are listed below:
	1 2-nodes SCG cluster
	1 host server for running the automation script
	Mutiple simulator servers for running the MadSZ

After running the automation scripts:
	1.	Host connect to SCG and deploy the environment by the restful api.
		a.	Create zones
		b.	Create registration rules
		c.	Create authentication service
		d.	Create authentication profile
		e.	Create accounting service
		f.	Create accounting profile
		g.	Create wlans for each zone 
		h.	Apply the authentication/accounting profile or service for the wlans.
		i.	Store the zone, registration rules and wlan info receive from the restful api.

	2.	Host create the ap/client config file for each simulator servers.
		a.	Calculate the ip, mac and then replace  the contents in the ap config files for each simulator servers.
		b.	Retrieve the mac and wlan id and then replace the contents in the client files for each simulator servers.

	3.	Host connect the 10 simulator servers through ssh.
		a.	Change the authorities of the ap and client config files on each simulator then copy the modified ones from the host server.
		b.	Run the AP bringing up command on each server.

Usage:
    python parallel_remote.py -a <opt1> -c <opt1>

    -a : AP behaviors after deployment (RUN, STOP, None)
    -c : Clean the existing environment (y, n)	
'''
import threadpool
import time
import conf.simpcs as simpcs
import argparse
from functools import partial
from lib.scg_api import scg_api
from lib.scg_api import scgCluster
from lib.log import log
from lib.ap import ap
from lib.create_zone_class import create_zone

def scg_ops(scg):
    scg_op = create_zone(scg)
    scg_op.login_scg()
    scg_op.create_zone()
    scg_op.create_registration_rules()
    scg_op.create_radius_server()

    scg_op.create_auth_service()
    scg_op.create_auth_profile()
    scg_op.auth_profile_realm()
    scg_op.create_acct_service()
    scg_op.create_acct_profile()
    scg_op.acct_profile_realm()

    scg_op.create_portal_service()
    scg_op.create_standard_wlan()
    scg_op.create_8021x_wlan()
    scg_op.create_hotspot_wlan()
    scg_op.create_mac_auth_wlan()
    scg_op.create_hotspot_mac_wlan()
    zone_list, vm_zone_table, ap_ip_ranges, ap_start_ip_vm = scg_op.get_data()
    return zone_list, vm_zone_table, ap_ip_ranges, ap_start_ip_vm

def create_zones():
    zone_list, vm_zone_table = {}, {}
    scg_node = simpcs.scgs_management.keys()
    zone_list_temp, vm_zone_table_temp, ap_ip_ranges, ap_start_ip_vm = scg_ops(scg_node)
    zone_list.update(zone_list_temp)
    vm_zone_table.update(vm_zone_table_temp)
    return zone_list, vm_zone_table, ap_ip_ranges, ap_start_ip_vm

def config_ue(scg_ip):
    api_session=scg_api(scg_ip, 7443, simpcs.scg_username, simpcs.scg_password, api_ver="v5_0")
    res = api_session.PLogin()
    cluster = scgCluster(api_session)
    ues = cluster.get_wlan_list()
    ori_ue_setting = [line.rstrip("\n").rstrip("\r") for line in open("template/ue.conf")]
    type_method_table = {
                          "Standard_Open": [1, 1, "", "", "", "", "", "", ""], 
                          "Standard_8021X": [1, 2, "cs", "cs1", 1, "", "", "", ""], 
                          "Standard_Mac": [1, 3, "", "", "", "", "", "", ""], 
                          "Hotspot": [2, 1, "cs", "cs1", "", 9998, 30, 1024, 30], 
                          "Hotspot_MacByPass": [2, 3, "cs", "cs1", "", 9998, 30, 1024, 30]
                        }
						
    zone_ue = {}
    for zone in ues.keys():
        temp_no = zone.split("_")[1]
        local_ue_setting_temp = "template/ue.conf"+temp_no
        zone_ue[zone] = local_ue_setting_temp
        wlan_count = 0
        with open(local_ue_setting_temp, "wb") as outfile:
            for line in ori_ue_setting:
                if "total_wlan_profiles" in line:
                    outfile.write("total_wlan_profiles="+str(len(ues[zone]))+"\n")
                elif "sta_base_mac" in line:
                    if len(temp_no) <= 1:
                        mac_add = "00:00:00:0"+temp_no+":00:00"
                    else:
                        mac_add = "00:00:00:"+temp_no[-2:]+":00:00"
                    outfile.write("sta_base_mac="+mac_add+"\n")
                elif "sta_base_ip" in line:
                    if len(temp_no) <= 1:
                        ip_add = "99."+temp_no+".0.1"
                    else:
                        ip_add = "99."+temp_no[-2:]+".0.1"
                    outfile.write("sta_base_ip="+ip_add+"\n")

                else:
                    outfile.write(line+"\n")
        with open(local_ue_setting_temp, "a") as f1:
            for wlan in ues[zone]:
                wlan_count += 1
                f1.write("#WLan "+str(wlan_count)+" profile\n")
                f1.write("wlan_ssid="+wlan["wlan_ssid"]+"\n")
                f1.write("auth_type="+str(type_method_table[wlan["auth_type"]][0])+"\n")
                f1.write("auth_method="+str(type_method_table[wlan["auth_type"]][1])+"\n")
                f1.write("aaa_user="+type_method_table[wlan["auth_type"]][2]+"\n")
                f1.write("aaa_pwd="+type_method_table[wlan["auth_type"]][3]+"\n")
                f1.write("sta_dot1x_method="+str(type_method_table[wlan["auth_type"]][4])+"\n")
                f1.write("portal_port="+str(type_method_table[wlan["auth_type"]][5])+"\n")
                f1.write("login_delay=1"+"\n")
                f1.write("req_timeout="+str(type_method_table[wlan["auth_type"]][6])+"\n")
                f1.write("low_speed_limit="+str(type_method_table[wlan["auth_type"]][7])+"\n")
                f1.write("low_speed_time="+str(type_method_table[wlan["auth_type"]][8])+"\n")
                f1.write("logout=1\n")
                f1.write("END_WLAN_PROFILE\n\n")
    return zone_ue

def madsz_operation(action, create, log_filename, ap_start_ip_vm, vm_ue, host):
    if action == "stop":
        op = ap(host, log_filename, simpcs, "")
        op.connect()
        op.stop_ap()
    else:
        if create == "y":
            op = ap(host, log_filename, simpcs, vm_ue[host])
            op.connect()
            op.modify_ap(ap_start_ip_vm)
            op.download()
        if action == "run":
            op.run_ap()
    op.close()

def run_ap(args, ap_start_ip_vm, vm_ue, log_filename):
    remote_servers = []
    for sim_pc in simpcs.scg_vm_list:
        remote_servers.append(sim_pc)
    pool = threadpool.ThreadPool(10)
    func = partial(madsz_operation, args.action, args.create, log_filename, ap_start_ip_vm, vm_ue)
    reqs = threadpool.makeRequests(func, remote_servers)
    [pool.putRequest(req) for req in reqs]
    pool.wait()
    pool.dismissWorkers(10, do_join=True)

def pair_vm_ue(zone_list, zone_ue):
    vm_ue = {}
    for zone in zone_list:
        vm_ue[zone_list[zone]["vm"]] = zone_ue[zone]
    return vm_ue

if __name__ == "__main__":
    log_filename = "./log/"+time.strftime("%Y_%m_%d_%H_%M_%S")+".log"
    f = open(log_filename, "w")
    f.write("***************Start automation process***************\n\n")
    f.close()

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--create', required=False,  help='create the environment in SimPCs', default='n', choices=('y','n'))
    parser.add_argument('-a', '--action', required=False,  help='run or stop the APs', default=None, choices=('run','stop',"none"))
    args = parser.parse_args()
   
    if args.action == "stop":
        remote_servers = []
        for sim_pc in simpcs.scg_vm_list:
            remote_servers.append(sim_pc)
        pool = threadpool.ThreadPool(10)
        func = partial(madsz_operation, args.action, args.create, log_filename, "", "")
        reqs = threadpool.makeRequests(func, remote_servers)
        [pool.putRequest(req) for req in reqs]
        pool.wait()
        pool.dismissWorkers(10, do_join=True)

    elif args.create == "y":
        zone_list, vm_zone_table, ap_ip_ranges, ap_start_ip_vm = create_zones()
        zone_ue = config_ue(simpcs.scgs_management.keys()[0]) 
        vm_ue = pair_vm_ue(zone_list, zone_ue)   
        if args.action == "run": 
            run_ap(args, ap_start_ip_vm, vm_ue, log_filename)
