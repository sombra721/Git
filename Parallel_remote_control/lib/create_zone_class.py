#!/usr/bin/python
import ast
import json
from scg_api import scg_api
from scg_api import scgCluster
import conf.simpcs as simpcs
import itertools


class create_zone(object):
    def __init__(self, scg):
        self.scg = scg[0]
        self.scg_username = simpcs.scg_username
        self.scg_password = simpcs.scg_password
        self.domainid = '8b2081d5-9662-40d9-a3db-2a3cf4dde3f7'
        scginfo = {'ip': self.scg, 'username': self.scg_username, 'passwd': self.scg_password, 'port': 7443,
                   'version': "v5_0",
                   'resource': "wlan", 'domainId': self.domainid, 'zoneId': ""}
       
        self.vms = simpcs.scg_vm_list
        
        print "===receive====:\n"
        print simpcs
        # login SCG
        self.api_session = scg_api(scginfo['ip'], scginfo['port'], scginfo['username'], scginfo['passwd'],
                                   api_ver=scginfo['version'])

    def login_scg(self):
        res = self.api_session.PLogin()
        cluster = scgCluster(self.api_session)
        self.ues = cluster.get_wlan_list()

    def create_zone(self):
        self.zone_list = {}
        self.vm_zone_table = {}
        #        print "=========vms========:\n", self.vms

        print "self.vms:\n", self.vms 
        print "simpcs.vm_settings:\n", simpcs.vm_settings
        for i_vm in range(len(self.vms)):
            for i_zone in range(simpcs.vm_settings[self.vms[i_vm]]["no_of_zone"]):
                zone_name = simpcs.vm_settings[self.vms[i_vm]]["prefix"] + "_" + str(
                    self.vms[i_vm].split(".")[-1]) + "_" + str(i_zone + 1)
                create_zone_payload = {"domainId": self.domainid, "name": zone_name,
                                       "login": {"apLoginName": self.scg_username,
                                                 "apLoginPassword": self.scg_password}}
                res = self.api_session.POST('rkszones', create_zone_payload, condition='')
                zone_id = ast.literal_eval(res)["id"]
                self.zone_list[zone_name] = {"vm": self.vms[i_vm], "id": zone_id}
                if self.vms[i_vm] in self.vm_zone_table:
                    self.vm_zone_table[self.vms[i_vm]].append(zone_name)
                else:
                    self.vm_zone_table[self.vms[i_vm]] = [zone_name]

    def calculate_ip(self, start_ip, no_ap):
        ip_sections = start_ip.split(".")
        total_no = int(ip_sections[0]) * pow(255, 3) + int(ip_sections[1]) * pow(255, 2) + int(
            ip_sections[2]) * 255 + int(ip_sections[3]) + no_ap - 1
        end_ip = ""
        count = 3

        while total_no:
            temp = total_no / pow(255, count)
            end_ip += str(temp)
            total_no -= temp * (pow(255, count))
            if count != 0:
                end_ip += "."
            count -= 1
        return end_ip

    def create_registration_rules(self):
        #        print "=======self.zone_list=====\n:", self.zone_list
        self.ap_ip_ranges = {}
        ip_prefix = ".".join(simpcs.scgs_management.keys()[0].split(".")[2:]) + "."
        start_ip = ip_prefix + "0.1"
        #        print "===========vms:\n", self.vms
        #        print "===========vm_zone_table:\n", self.vm_zone_table
        self.ap_start_ip_vm = {}
        for vm in self.vms:
            no_ap = simpcs.vm_settings[vm]["no_of_AP_per_zone"]
            self.ap_start_ip_vm[vm] = start_ip
            for zone in self.vm_zone_table[vm]:
                end_ip = self.calculate_ip(start_ip, no_ap)
                #                print "============="
                print "vm: ",vm, " zone: ", zone
                print "start_ip: ", start_ip, " end_ip: ", end_ip

                payload = {"description": "Zone used for " + zone,
                           "type": "IPAddressRange",
                           "ipAddressRange": {
                               "fromIp": start_ip,
                               "toIp": end_ip
                           },
                           "mobilityZone": {
                               "id": self.zone_list[zone]["id"]
                           }
                           }
                res = self.api_session.POST('apRules', payload, condition='')
                self.ap_ip_ranges[zone] = {"start_ip": start_ip, "end_ip": end_ip}
                start_ip = self.calculate_ip(end_ip, 2)

    def create_auth_service(self):
        name = "RADIUS_auth_service"
        ip = simpcs.radius_ip
        radius_sharedsecret = simpcs.sharedsecret
        payload = "{{" \
                  "\"name\": \"{0}\", " \
                  "\"domainId\": \"{1}\", " \
                  "\"primary\": {{" \
                  "\"ip\": \"{2}\"," \
                  "\"port\": {3}," \
                  "\"sharedSecret\": \"{4}\"" \
                  "}}}}".format(name, self.domainid, ip, "1812", radius_sharedsecret)

        url = "services/auth/radius"
        res = self.api_session.POST(url, payload, dump=False)
        radius_auth_service_id = ast.literal_eval(res)["id"]
        self.radius_auth_service = {"id": radius_auth_service_id, "name": name}

    def create_auth_profile(self):
        name = "RADIUS_auth_profile"
        payload = "{{" \
                  "\"domainId\": \"{0}\", " \
                  "\"name\": \"{1}\", " \
                  "\"gppSuppportEnabled\" : false," \
                  "\"aaaSuppportEnabled\" : false" \
                  "}}".format(self.domainid, name)

        url = "profiles/auth"
        res = self.api_session.POST(url, payload, dump=False)
        radius_auth_profile_id = ast.literal_eval(res)["id"]
        self.radius_auth_profile = {"id": radius_auth_profile_id, "name": name}

    def auth_profile_realm(self):
        payload = [{"realm": "No Match",
                    "id": self.radius_auth_service["id"],
                    "name": self.radius_auth_service["name"],
                    "serviceType": "RADIUS",
                    "authorizationMethod": "NonGPPCallFlow"},
                   {
                       "realm": "Unspecified",
                       "id": self.radius_auth_service["id"],
                       "name": self.radius_auth_service["name"],
                       "serviceType": "RADIUS",
                       "authorizationMethod": "NonGPPCallFlow"
                   }]
        url = "profiles/auth/" + self.radius_auth_profile["id"] + "/realmMappings"
        res = self.api_session.PATCH(url, payload, dump=True)

    def wlan_apply_auth(self, service_or_profile, zone_id, wlan_id):
        url = "rkszones/" + zone_id + "/wlans/" + wlan_id + "/authServiceOrProfile"
        if service_or_profile == "profile":
            radius_auth_id = self.radius_auth_profile["id"]
        elif service_or_profile == "service":
            radius_auth_id = self.radius_auth_service["id"]
        payload = "{{" \
                  "\"throughController\" : true," \
                  "\"id\": \"{0}\", " \
                  "\"locationDeliveryEnabled\" : false" \
                  "}}".format(radius_auth_id)
        #        print "  ==========apply auth url=============:\n", url
        #        print "  ==========apply auth payload=============:\n", payload
        res = self.api_session.PATCH(url, payload, condition="", dump=False)

    #        print "  ==========apply auth res=============:\n", res

    def create_acct_service(self):
        name = "RADIUS_accounting_service"
        ip = simpcs.radius_ip
        radius_sharedsecret = simpcs.sharedsecret
        payload = "{{" \
                  "\"name\": \"{0}\", " \
                  "\"domainId\": \"{1}\", " \
                  "\"primary\": {{" \
                  "\"ip\": \"{2}\"," \
                  "\"port\": {3}," \
                  "\"sharedSecret\": \"{4}\"" \
                  "}}}}".format(name, self.domainid, ip, "1813", radius_sharedsecret)

        url = "services/acct/radius"
        res = self.api_session.POST(url, payload, dump=False)
        radius_accounting_service_id = ast.literal_eval(res)["id"]
        self.radius_accounting_service = {"id": radius_accounting_service_id, "name": name}

    def create_acct_profile(self):
        name = "RADIUS_accounting_profile"
        radius_sharedsecret = simpcs.sharedsecret
        payload = {"domainId": self.domainid,
                   "name": name
                   }
        url = "profiles/acct"
        res = self.api_session.POST(url, payload, dump=True)
        radius_accounting_profile_id = ast.literal_eval(res)["id"]
        self.radius_accounting_profile = {"id": radius_accounting_profile_id, "name": name}

    def acct_profile_realm(self):
        payload = [{"realm": "No Match",
                    "id": self.radius_accounting_service["id"],
                    "name": self.radius_accounting_service["name"],
                    "serviceType": "RADIUS",
                    "authorizationMethod": "NonGPPCallFlow"},
                   {
                       "realm": "Unspecified",
                       "id": self.radius_accounting_service["id"],
                       "name": self.radius_accounting_service["name"],
                       "serviceType": "RADIUS",
                       "authorizationMethod": "NonGPPCallFlow"
                   }]

        url = "profiles/auth/" + self.radius_accounting_profile["id"] + "/realmMappings"
        res = self.api_session.PATCH(url, payload, dump=True)

    def wlan_apply_accounting(self, service_or_profile, zone_id, wlan_id):
        url = "rkszones/" + zone_id + "/wlans/" + wlan_id + "/accountingServiceOrProfile"
        if service_or_profile == "profile":
            radius_accounting_id = self.radius_accounting_profile["id"]
            radius_accounting_name = self.radius_accounting_profile["name"]
        elif service_or_profile == "service":
            radius_accounting_id = self.radius_accounting_service["id"]
            radius_accounting_name = self.radius_accounting_service["name"]
        payload = "{{" \
                  "\"throughController\" : true," \
                  "\"id\": \"{0}\", " \
                  "\"name\": \"{1}\", " \
                  "\"interimUpdateMin\" : {2}," \
                  "\"accountingDelayEnabled\" : false" \
                  "}}".format(radius_accounting_id, radius_accounting_name, "10")
        # print "  ==========apply accounting url=============:\n  ", url
        # print "  ==========apply accounting payload=============:\n  ", payload
        res = self.api_session.PATCH(url, payload, condition="", dump=False)
        # print "  ==========apply accounting res=============:\n  ", res

    def create_standard_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            for i in range(simpcs.vm_settings[self.zone_list[zone]["vm"]]["no_of_wlan"][0]):
                name = ssid = "wlan_standard_" + str(i + 1)
                description = "standard wlan " + str(i + 1)
                payload = {
                    "name": name,
                    "ssid": ssid,
                    "description": description
                }
                url = "rkszones/" + zone_id + "/wlans"
                res = self.api_session.POST(url, payload, condition='')
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
                # print "*************** creating standard wlan in ",zone,"*****************"
                self.wlan_apply_accounting("profile", zone_id, wlan_id)
            self.zone_list[zone]["standard_wlan"] = wlan_list

    def create_radius_server(self):
        for zone in self.zone_list:
            name = zone + "_radius_server"
            zone_id = self.zone_list[zone]["id"]
            ip = simpcs.radius_ip
            radius_sharedsecret = simpcs.sharedsecret
            payload = "{{" \
                      "\"name\": \"{0}\", " \
                      "\"primary\": {{" \
                      "\"ip\": \"{1}\"," \
                      "\"port\": {2}," \
                      "\"sharedSecret\": \"{3}\"" \
                      "}}}}".format(name, ip, "1812", radius_sharedsecret)

            url = "rkszones/" + zone_id + "/aaa/radius"
            res = self.api_session.POST(url, payload, dump=False)
            radius_server_id = ast.literal_eval(res)["id"]
            self.zone_list[zone]["radius_server"] = {"id": radius_server_id, "name": name}

    def create_8021x_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            auth_service_name = zone + "_auth_service"
            for i in range(simpcs.vm_settings[self.zone_list[zone]["vm"]]["no_of_wlan"][1]):
                name = ssid = "8021x_" + str(i + 1)
                auth_service_name = auth_service_name + "_" + str(i + 1)
                description = "8021x wlan " + str(i + 1)
                payload = "{{" \
                          "\"name\" :\" {0}\", " \
                          "\"ssid\" : \"{1}\", " \
                          "\"description\" : \"{2}\"," \
                          "\"authServiceOrProfile\" : {{" \
                          "\"throughController\" : false," \
                          "\"id\" : \"{3}\"," \
                          "\"name\" : \"{4}\"" \
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"],
                                        self.zone_list[zone]["radius_server"]["name"])
                url = "rkszones/" + zone_id + "/wlans/standard80211"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
                # print "*************** creating 8021x wlan in ",zone,"*****************"
                #self.wlan_apply_accounting("profile", zone_id, wlan_id)
                #self.wlan_apply_auth("profile", zone_id, wlan_id)
            self.zone_list[zone]["8021x_wlan"] = wlan_list

    def disable_portal_show(self, zone_id, portal_service_id):
        language = "en_US"
        payload = "{{" \
                  "\"language\" : \"{0}\", " \
                  "\"termsAndConditionsRequired\" : false" \
                  "}}".format(language)

        url = "rkszones/" + zone_id + "/portals/hotspot/" + portal_service_id + "/portalCustomization"
        res = self.api_session.PATCH(url, payload, dump=False)

    def create_portal_service(self):
        for zone in self.zone_list:
            name = description = zone + "_portal_service"
            zone_id = self.zone_list[zone]["id"]
            payload = "{{" \
                      "\"name\": \"{0}\", " \
                      "\"description\": \"{1}\", " \
                      "\"smartClientSupport\": \"None\", " \
                      "\"location\": {{" \
                      "\"id\": \"\"," \
                      "\"name\": \"\"" \
                      "}}," \
                      "\"macAddressFormat\": {2}, " \
                      "\"walledGardens\": {3} " "}}".format(name, description, "2", "[]")
            url = "rkszones/" + zone_id + "/portals/hotspot/internal"
            res = self.api_session.POST(url, payload, dump=False)
            portal_service_id = ast.literal_eval(res)["id"]
            self.zone_list[zone]["portal_service"] = {"id": portal_service_id, "name": name}
            self.disable_portal_show(zone_id, portal_service_id)

    def create_hotspot_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            for i in range(simpcs.vm_settings[self.zone_list[zone]["vm"]]["no_of_wlan"][2]):
                name = ssid = "hotspot_" + str(i + 1)
                description = "hotspot wlan " + str(i + 1)
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
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"],
                                        self.zone_list[zone]["radius_server"]["name"],
                                        self.zone_list[zone]["portal_service"]["id"],
                                        self.zone_list[zone]["portal_service"]["name"])
                url = "rkszones/" + zone_id + "/wlans/wispr"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
                # print "*************** creating hotspot wlan in ",zone,"*****************"
                self.wlan_apply_accounting("service", zone_id, wlan_id)
                self.wlan_apply_auth("service", zone_id, wlan_id)
            self.zone_list[zone]["hotspot_wlan"] = wlan_list

    def create_mac_auth_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            wlan_list = []
            for i in range(simpcs.vm_settings[self.zone_list[zone]["vm"]]["no_of_wlan"][3]):
                name = ssid = "mac_auth_" + str(i + 1)
                description = "mac auth wlan " + str(i + 1)
                payload = "{{" \
                          "\"name\" :\" {0}\", " \
                          "\"ssid\" : \"{1}\", " \
                          "\"description\" : \"{2}\"," \
                          "\"authServiceOrProfile\" : {{" \
                          "\"throughController\" : false," \
                          "\"id\" : \"{3}\"," \
                          "\"name\" : \"{4}\"" \
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"],
                                        self.zone_list[zone]["radius_server"]["name"])
                url = "rkszones/" + zone_id + "/wlans/standardmac"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
                # print "*************** creating mac auth wlan in ",zone,"*****************"
                self.wlan_apply_accounting("profile", zone_id, wlan_id)
                self.wlan_apply_auth("profile", zone_id, wlan_id)
            self.zone_list[zone]["mac_auth_wlan"] = wlan_list

    def create_hotspot_mac_wlan(self):
        for zone in self.zone_list:
            zone_id = self.zone_list[zone]["id"]
            portal_service_id, portal_service_name = self.zone_list[zone]["portal_service"]["id"], \
                                                     self.zone_list[zone]["portal_service"]["name"]
            wlan_list = []
            for i in range(simpcs.vm_settings[self.zone_list[zone]["vm"]]["no_of_wlan"][4]):
                name = ssid = "hotspot_mac_" + str(i + 1)
                description = "hotspot mac wlan " + str(i + 1)
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
                          "}}}}".format(name, ssid, description, self.zone_list[zone]["radius_server"]["id"],
                                        self.zone_list[zone]["radius_server"]["name"], portal_service_id,
                                        portal_service_name)
                url = "rkszones/" + zone_id + "/wlans/wisprmac"
                res = self.api_session.POST(url, payload, condition='', dump=False)
                wlan_id = ast.literal_eval(res)["id"]
                wlan_list.append(wlan_id)
                # print "*************** creating hotspot mac wlan in ",zone,"*****************"
                self.wlan_apply_accounting("service", zone_id, wlan_id)
                self.wlan_apply_auth("service", zone_id, wlan_id)
            self.zone_list[zone]["hotspot_mac_wlan"] = wlan_list

    def get_data(self):
        return self.zone_list, self.vm_zone_table, self.ap_ip_ranges, self.ap_start_ip_vm

