#!/usr/bin/python

import urllib2
import sys
import paramiko
from log import log
import time 
from colors import colors

RETRY = 10

class ap(object):
    def __init__(self, host, log_filename, simpcs="", ue_config=""):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.RETRY = 10
        self.host = host
        self.log = log_filename
        self.f = log(log_filename)
        self.simpcs = simpcs
        self.MadSZ_filename = self.simpcs.MadSZ_link.split("/")[-1]
        self.new_MadSZ = self.MadSZ_filename[:self.MadSZ_filename.index(".tar")]
        self.MadSZ_dir = self.simpcs.remote_MadSZ_path
        self.change_to_MadSZ_dir = "cd " + self.MadSZ_dir
        self.change_to_script_dir = "cd " + "/" + self.new_MadSZ + "/scripts"
        self.move_to_root = "sudo mv " + self.MadSZ_dir + "/" + self.new_MadSZ + " /"
        self.apsim_path = "/" + self.new_MadSZ + "/scripts/apsim.cfg"
        self.ue_path = "/" + self.new_MadSZ + "/conf/ue.conf"
        self.scg = self.simpcs.scgs_management.values()[0]
        self.ue_config = ue_config
        self.sysinit_path = "/" +self.new_MadSZ +"/scripts/sysinit.sh"

    def modify_ap(self, ap_start_ip_vm):
        # apsim.cfg file content for each vm

        self.sim_pc_settings = {}
        for sim_pc in self.simpcs.scg_vm_list:
            if sim_pc == self.host:
                temp = sim_pc.split(".")
                self.sim_pc_settings[sim_pc] = {}
                self.sim_pc_settings[sim_pc]["scg_ip"] = self.scg
                #self.sim_pc_settings[sim_pc]["ap_start_ip"] = temp[2] + "." + temp[3] + ".1.1"
#                self.sim_pc_settings[sim_pc]["ap_start_ip"] = ap_start_ip_vm
                self.sim_pc_settings[sim_pc]["ap_start_mac"] = "00:" + str(temp[2])[-2:] + ":" + str(temp[3])[-2:] + ":00:00:00"

        self.ori_sim_ap_setting = [line.rstrip('\n').rstrip('\r') for line in open("template/apsim.cfg")]

        # modify apsim.file for each vm
#        for sim_pc in self.sim_pc_settings:
        local_ap_setting_temp = "template/apsim.cfg" + str(self.host.split(".")[3])
#        print "====dealing with ",self.host
#        print "local_ap_setting_temp: ", local_ap_setting_temp
#        print "ap_start_ip_vm: ", ap_start_ip_vm[self.host]
        self.sim_pc_settings[self.host]["local_ap_setting_temp"] = local_ap_setting_temp
        with open(local_ap_setting_temp, "wb") as outfile:
            for line in self.ori_sim_ap_setting:
                if "SZIP" in line:
                    outfile.write("SZIP=\"" + self.sim_pc_settings[self.host]["scg_ip"] + "\"\n")
                elif "FWVER" in line:
                    outfile.write("FWVER=\"" + self.simpcs.fw_version + "\"\n")
                elif "MODEL" in line:
                    outfile.write("MODEL=\"" + self.simpcs.model + "\"\n")
                elif "APNUM" in line:
                    #outfile.write("APNUM=\"" + self.simpcs.ap_num + "\"\n")
                    outfile.write("APNUM=\"" + str(self.simpcs.vm_settings[self.host]["no_of_AP_per_zone"]) + "\"\n")
                elif "START_AP_IP" in line:
                    #outfile.write("START_AP_IP=\"" + self.sim_pc_settings[sim_pc]["ap_start_ip"] + "\"\n")
                    outfile.write("START_AP_IP=\"" + ap_start_ip_vm[self.host] + "\"\n")
                elif "START_AP_MAC" in line:
                    outfile.write("START_AP_MAC=\"" + self.sim_pc_settings[self.host]["ap_start_mac"] + "\"\n")
                elif "AP_PER_SEC" in line:
                    outfile.write("AP_PER_SEC=" + self.simpcs.ap_per_sec + "\n")
                else:
                    if "\r" in line:
                        line = str(line)[:-1]
                    outfile.write(str(line) + "\n")

    def connect(self, retry_count=0):
        self.retry_count = retry_count
        try:
            self.ssh.connect(self.host, username=self.simpcs.username, password=self.simpcs.password, port=self.simpcs.port)
            self.chan = self.ssh.invoke_shell()
            self.sftp = self.ssh.open_sftp()
            print colors.OKGREEN+ self.host, " successfully set up connection" + colors.ENDC
            self.f.write(self.host, "info", "successfully set up ssh connection.")
        except:
            self.retry_count += 1
            if self.retry_count <= self.RETRY:
                time.sleep(5)
                self.f.write(self.host, "warning", "attemp to retry ssh connection.")
                self.connect(self.retry_count)
#            print colors.FAIL + self.host, " has connection issue" + colors.ENDC
            self.f.write(self.host, "error", "successfully set up ssh connection.")
            self.ssh.close()
            return    
    
    def copy_ap_config(self):
#        print "apsim_path: ", self.apsim_path
        self.f.write(self.host, "info", "copy ap config file.")
        self.sftp.chmod(self.apsim_path, 755)
        self.sftp.put(self.sim_pc_settings[self.host]["local_ap_setting_temp"], self.apsim_path)

    def copy_ue_config(self):
#        print "ue_path: ", self.ue_path
#        print "ue_config: ", self.ue_config
        self.f.write(self.host, "info", "copy ue config file.")
        self.sftp.chmod(self.ue_path, 755)
        self.sftp.put(self.ue_config, self.ue_path)

    def copy_sysinit(self):
#        print "sysinit_path: ", self.sysinit_path
        self.f.write(self.host, "info", "copy sysinit file.")
        self.sftp.chmod(self.sysinit_path, 755)
        self.sftp.put(self.simpcs.sysinit, self.sysinit_path)
                           
    def send_command(self, cmd, should_print=False):
        self.chan.send(cmd)
        buff = ''
        while not (buff.endswith('# ') or buff.endswith('$ ')):
            resp = self.chan.recv(9999)
            if should_print:
                print resp
            buff += resp
        return buff

    def check_url_valid(self, url):
        try:
            f = urllib2.urlopen(urllib2.Request(url))
            deadLinkFound = False
            print colors.OKBLUE + "MadSZ link is valid" + colors.ENDC
        except:
            deadLinkFound = True
            print colors.FAIL + "MadSZ link is invalid, please check the config file." + colors.ENDC
            sys.exit()

    def download(self):
        self.transport = paramiko.Transport((self.host, 22))
        self.transport.connect(username=self.simpcs.username, password=self.simpcs.password)
        # download MadSZ file if it does not exist
        command = self.change_to_MadSZ_dir+"\n"
        self.send_command(command, False)
        command = "sudo rm -rf "+self.new_MadSZ+"\n"
        self.send_command(command, False)
        command = "ls\n"
        results = self.send_command(command, False)
        if not self.MadSZ_filename in results:
            self.f.write(self.host, "info", "begin to download madSZ.")
            self.check_url_valid(self.simpcs.MadSZ_link)
            self.send_command("sudo wget "+ self.simpcs.MadSZ_link+ "\n", False)
        else:
            self.f.write(self.host, "info", "madSZ file already exists.")
            
        # decompress the MadSZ
        command = "sudo tar Jxvf " + self.MadSZ_filename + "\n"
        self.f.write(self.host, "info", "start to unzip the madSZ.")
        self.send_command(command + "\n", False)
        self.f.write(self.host, "info", "finish unzipping the madSZ.")

        # change MadSZ name
        command = "sudo mv BUILD/  "+self.new_MadSZ
        #print "change name:\n", command
        self.send_command(command + "\n", False)
        try:
            self.copy_ap_config()
        except:
            command = "ls\n"
            results = self.send_command(command, False)
            if not "BUILD" in results:
                self.f.write(self.host, "warning", "cannot unzip the madsz, start to upgrade the zy utility")
                self.send_command("sudo dpkg --configure -a\n", False)
                self.send_command("sudo apt-get install xz-utils\n", False)
                command = "sudo tar Jxvf " + self.MadSZ_filename + "\n"
                self.f.write(self.host, "info", "start to unzip the madSZ.")
                self.send_command(command + "\n", False)
                self.f.write(self.host, "info", "finish unzipping the madSZ.")
            else:
                self.f.write(self.host, "error", "cannot unzip the madsz")
                sys.exit()

        self.copy_ue_config()
        self.copy_sysinit()
        self.transport.close()

    def close(self):
        self.ssh.close()
        self.f.write(self.host, "info", "close ssh connection.")
        self.f.write(self.host, "info", "operations are successfully done.")
        self.f.close()
        print colors.OKBLUE+ self.host, " operations are successfully done." + colors.ENDC 

    def run_ap(self):
        print colors.OKBLUE+ self.host, "run start ap commands." + colors.ENDC 
        command = self.change_to_script_dir + "\n"
        self.send_command(command + "\n", False)
        command = "sudo ./sim.sh up" + "\n"
        self.send_command(command + "\n", False)
 
    def stop_ap(self):
        print colors.OKBLUE+ self.host, "run stop and clean ap commands." + colors.ENDC 
        command = self.change_to_script_dir + "\n"
        self.send_command(command + "\n", False)
        command = "sudo ./sim.sh down" + "\n"
        self.send_command(command + "\n", True)
        command = "sudo ./sim.sh clean" + "\n"
        self.send_command(command + "\n", True)    
