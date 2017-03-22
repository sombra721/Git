MadSZ_link = "http://tdc-jenkins.video54.local:7777/repo/simtool/packages/madsz/38/madSZ-v3.5-27.tar.xz"
remote_MadSZ_path = "/"
decompressed_remote_MadSZ_path = remote_MadSZ_path+"/BUILD"
remote_ap_setting_path = decompressed_remote_MadSZ_path+"/scripts/"

# <management ip>: <control ip> 
scgs_management = {"172.17.29.136": "192.168.29.136"}
sysinit = "template/sysinit.sh"

# <scg control ip>: <vm ip series iteration>
scg_vm_list=[
    "172.17.29.111",
    "172.17.29.112",
    "172.17.29.113",
    "172.17.29.114",
    "172.17.29.115",
    "172.17.29.116",
    "172.17.29.117",
    "172.17.29.118",
    "172.17.29.119",
    "172.17.29.120",
                    ]
					
vm_settings={
"172.17.29.111": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.112": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.113": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.114": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.115": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.106": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.117": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.118": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.119": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
"172.17.29.120": {"no_of_zone": 1, "prefix": "hotspot", "no_of_AP_per_zone": 700, "no_of_wlan": [0, 0, 1, 0, 0]},
}


scg_username = "admin"
scg_password = "admin12345!"


fw_version = "3.5.0.0.1286"
model = "R710"
ap_num = "10"
ap_per_sec ="3"

username = "root"
password = "lab4man1"
port = 22

#====================
# ue settings
#====================
total_client_num = 10000
ue_rate = 100
online_duration = 1800
offline_duration = 60
ap_associate_method = 1
wlan_associate_method = 2


#===================
# wlan settings
#===================
# wlan number list
no_standard_wlan = 1
no_8021x_wlan = 1
radius_ip = "192.168.29.243"
sharedsecret = "testing123"
no_hotspot_wlan = 1
no_mac_auth_wlan = 1
no_hotspot_mac_wlan = 1
