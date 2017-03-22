#!/usr/bin/python
import ast
import json
from scg_api import scg_api
from scg_cluster import scgCluster
import itertools

class zone(object):
    def __init__(self, scg, simpcs):
        self.scg = scg
        self.simpcs = simpcs
        self.scg_username = simpcs.scg_username
        self.scg_password = simpcs.scg_password
        self.simpcs = simpcs
        self.domainid = "8b2081d5-9662-40d9-a3db-2a3cf4dde3f7"
        self.zoneid = ''
        self.scginfo = {'ip': self.scg, 'username': self.scg_username, 'passwd': self.scg_password, 'port': 7443, 'version': "v5_0",
                   'resource': "wlan", 'domainId': self.domainid, 'zoneId': self.zoneid}

        self.api_session=scg_api(self.scginfo['ip'],  self.scginfo['port'], self.scginfo['username'], self.scginfo['passwd'], api_ver=self.scginfo['version'])
        self.vms = simpcs.scg_vm_list[simpcs.scgs_management[self.scg]]

    def login_scg(self):
        self.res = self.api_session.PLogin()
        self.cluster = scgCluster(self.api_session)
        self.ues = self.cluster.get_wlan_list()
    
    def create_zone(self):
        zone_list = {}
        vm_zone_table = {}
        for i in range(len(self.vms)):
            zone_name = "Zone_"+str(self.vms[i].split(".")[-1])
            create_zone_payload = {"domainId" : self.domainid, "name" : zone_name,
                                   "login" : {"apLoginName" : self.scg_username, "apLoginPassword": self.scg_password}}
            res = self.api_session.POST('rkszones', create_zone_payload, condition='')
            zone_id = ast.literal_eval(res)["id"]
            zone_list[zone_name] = {"vm": self.vms[i], "id": zone_id}
            vm_zone_table[self.vms[i]] = zone_name
        self.zone_list = zone_list
        self.vm_zone_table =  vm_zone_table

    def create_registration_rulesself(self):
        ap_ip_ranges = {}
        for vm in self.vms:
            ip_prefix = ".".join(vm.split(".")[2:])+"."
            start_ip = ip_prefix+"0.0"
            end_ip = ip_prefix+"255.255"
            payload={"description" : "Zone used for "+vm,
                                     "type" : "IPAddressRange",
                                     "ipAddressRange" : {
                                             "fromIp" : start_ip,
                                             "toIp" : end_ip
                                        },
                                     "mobilityZone" : {
                                            "id" : self.zone_list[self.vm_zone_table[vm]]["id"]
                                        }
                                    }
            res = self.api_session.POST('apRules', payload, condition='')
            ap_ip_ranges[vm] = {"start_ip": start_ip, "end_ip": end_ip}
        self.ap_ip_ranges = ap_ip_ranges

    def create_standard_wlan(self):
        for zone in self.zone_list.keys():
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            for i in range(self.simpcs.no_standard_wlan):
                name = ssid = "wlan_standard_"+str(i+1)
                description = "standard wlan "+str(i+1)
                payload = {
                              "name" : name,
                              "ssid" : ssid,
                              "description" : description
                }
                url = "rkszones/"+zone_id+"/wlans"
                res = self.api_session.POST(url, payload, condition='')
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)    
            self.zone_list[zone]["standard_wlan"] = wlan_list

    def create_radius_server(self):
        for zone in self.zone_list:
            name = zone+"_radius_server"
            zone_id = self.zone_list[zone]["id"]
            ip = self.simpcs.radius_ip
            radius_sharedsecret = self.simpcs.sharedsecret
            payload = "{{" \
                          "\"name\": \"{0}\", " \
                          "\"primary\": {{" \
                              "\"ip\": \"{1}\"," \
                              "\"port\": {2}," \
                              "\"sharedSecret\": \"{3}\"" \
                      "}}}}".format(name, ip, "1812", radius_sharedsecret)
    
            url = "rkszones/"+zone_id+"/aaa/radius"
            res = self.api_session.POST(url, payload, dump=False)
            radius_server_id = ast.literal_eval(res)["id"]
            self.zone_list[zone]["radius_server"] = {"id": radius_server_id, "name": name}

    def create_8021x_wlan(self):
        for zone in self.zone_list.keys():
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            auth_service_name = zone+"_auth_service"
            for i in range(self.simpcs.no_8021x_wlan):
                name = ssid = "8021x_"+str(i+1)
                auth_service_name = auth_service_name+"_"+str(i+1)
                description = "8021x wlan "+str(i+1)
                payload = "{{" \
                          "\"name\" :\" {0}\", " \
                          "\"ssid\" : \"{1}\", " \
                          "\"description\" : \"{2}\"," \
                          "\"authServiceOrProfile\" : {{" \
                              "\"throughController\" : false," \
                              "\"id\" : \"{3}\"," \
                              "\"name\" : \"{4}\"" \
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"], self.zone_list[zone]["radius_server"]["name"]) 
                url = "rkszones/"+zone_id+"/wlans/standard80211"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
            self.zone_list[zone]["8021x_wlan"] = wlan_list

    def disable_portal_show(self, zone_id, portal_service_id):
        language = "en_US"
        payload = "{{" \
                  "\"language\" : \"{0}\", " \
                  "\"termsAndConditionsRequired\" : false" \
                  "}}".format(language )

        url = "rkszones/"+zone_id+"/portals/hotspot/"+portal_service_id+"/portalCustomization"
        res = self.api_session.PATCH(url, payload, dump=False)

    def create_portal_service(self):
        for zone in self.zone_list:
            name = description = zone+"_portal_service"
            zone_id = self.zone_list[zone]["id"]
            payload = "{{" \
                          "\"name\": \"{0}\", " \
                          "\"description\": \"{1}\", " \
                          "\"smartClientSupport\": \"None\", " \
                          "\"location\": {{" \
                              "\"id\": \"\"," \
                              "\"name\": \"\"" \
                          "}},"\
                          "\"macAddressFormat\": {2}, " \
                          "\"walledGardens\": {3} " "}}".format(name, description, "2", "[]")
            url = "rkszones/"+zone_id+"/portals/hotspot/internal"
            res = self.api_session.POST(url, payload, dump=False)
            portal_service_id = ast.literal_eval(res)["id"]
            self.zone_list[zone]["portal_service"] = {"id": portal_service_id, "name": name}
            self.disable_portal_show(zone_id, portal_service_id)
        
    
    def create_hotspot_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []  
            for i in range(self.simpcs.no_hotspot_wlan):
                name = ssid = "hotspot_"+str(i+1)
                description = "hotspot wlan "+str(i+1)
                payload = "{{" \
                  "\"name\" :\" {0}\", " \
                  "\"ssid\" : \"{1}\", " \
                  "\"description\" : \"{2}\"," \
                      "\"authServiceOrProfile\" : {{" \
                          "\"throughController\" : false," \
                          "\"id\" : \"{3}\"," \
                          "\"name\" : \"{4}\"" \
                          "}}," \
                      "\"portalServiceProfile\" : {{" \
                          "\"id\" : \"{5}\"," \
                          "\"name\" : \"{6}\"" \
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"], self.zone_list[zone]["radius_server"]["name"], self.zone_list[zone]["portal_service"]["id"], self.zone_list[zone]["portal_service"]["name"])
                url = "rkszones/"+zone_id+"/wlans/wispr"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
            self.zone_list[zone]["hotspot_wlan"] = wlan_list
               
    def create_mac_auth_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            for i in range(self.simpcs.no_mac_auth_wlan):
                name = ssid = "mac_auth_"+str(i+1)
                description = "mac auth wlan "+str(i+1)
                payload = "{{" \
                  "\"name\" :\" {0}\", " \
                  "\"ssid\" : \"{1}\", " \
                  "\"description\" : \"{2}\"," \
                      "\"authServiceOrProfile\" : {{" \
                          "\"throughController\" : false," \
                          "\"id\" : \"{3}\"," \
                          "\"name\" : \"{4}\"" \
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"], self.zone_list[zone]["radius_server"]["name"])
                url = "rkszones/"+zone_id+"/wlans/standardmac"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
            self.zone_list[zone]["mac_auth_wlan"] = wlan_list
    
    def create_hotspot_mac_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            portal_service_id, portal_service_name = self.zone_list[zone]["portal_service"]["id"], self.zone_list[zone]["portal_service"]["name"] 
            wlan_list = []
            for i in range(self.simpcs.no_hotspot_mac_wlan):
                name = ssid = "hotspot_mac_"+str(i+1)
                description = "hotspot mac wlan "+str(i+1)
                payload = "{{" \
                  "\"name\" :\" {0}\", " \
                  "\"ssid\" : \"{1}\", " \
                  "\"description\" : \"{2}\"," \
                      "\"authServiceOrProfile\" : {{" \
                          "\"throughController\" : false," \
                          "\"id\" : \"{3}\"," \
                          "\"name\" : \"{4}\"" \
                          "}}," \
                      "\"portalServiceProfile\" : {{" \
                          "\"id\" : \"{5}\"," \
                          "\"name\" : \"{6}\"" \
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"], self.zone_list[zone]["radius_server"]["name"], portal_service_id, portal_service_name)
                url = "rkszones/"+zone_id+"/wlans/wisprmac"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
            self.zone_list[zone]["hotspot_mac_wlan"] = wlan_list
    
