#!/usr/bin/env python
__author__ = "Michael Tsai"
'''
This script gathers the monitor data of each node from Grafana and plotting.

Monitor data be gathered and plotted:
  1. CPU usage
  2. memory usage
  3. disk I/O rate
  4. jmx heap size
  5. file system usage
  6. traffic banwidth

Users are required to choose the time frame mode:
  1. User defined start and end time.
  2. A time period to the past from now in minutes.

Script localizes the time and convert it to UTC then gather the monitor data in the specified time frame.

After parsing the data, the script does the following:
  1. Plot the diagrams based on each entity.
  2. Caculate the summary (average and maximum for each entity) then write them into a csv file.
  3. Appened the plotted images into a pdf file.

Usage:
  python perf.py
'''
import os
import sys
import csv
import pytz
import time
import datetime
import signal
import optparse
import collections
import matplotlib as mpl
mpl.use("Agg")
mpl.get_backend()
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from operator import add
from fpdf import FPDF

reports = {}

image_files = []

class grafana_ret(object):
    def __init__(self, path, from_time, until_time, escape):
        self.path = path
        self.from_time = from_time
        self.until_time = until_time
        self.total_value = []
        self.escape = escape
        try:
            (self.timeInfo, self.values) = whisper.fetch(path, from_time, until_time)
                                                     
        except whisper.WhisperException as exc:
            print "error occurs!"
            raise SystemExit('[ERROR] %s' % str(exc))
        (self.start, self.end, self.step) = self.timeInfo     
        self.time_stamp = []
        self.grafana_value = []
        
    def get_data(self):
        t = self.start
        for value in self.values:
            if options.pretty:
                timestr = time.ctime(t)                    
            else:
                timestr = str(t)
            if not value:
                t += self.step
                continue
            else:
                valuestr = "%f" % value
            self.time_stamp.append(t)
            self.grafana_value.append(float(value))
            t += self.step 
        if not self.time_stamp or not self.grafana_value:
#            print "there is no grafana data"
            if self.escape == True:
                print "escape! "                  
                return [], []
#                sys.exit(0)
        return self.time_stamp, self.grafana_value

def plotting(time_stamp, grafana_value, filename, title, y_label, debug="n"):
    filename = dir_name+"/"+filename
    image_files.append(filename)
    if time_stamp == []:
        return
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    start_time = datetime.datetime.fromtimestamp(int(time_stamp[0])).strftime('%c')
    end_time = datetime.datetime.fromtimestamp(int(time_stamp[-1])).strftime('%c')
    
    max_usage = max([float(i) for i in grafana_value])
    secs = mdate.epoch2num(time_stamp)

    if debug == "y":
        print "==============================="
        print "start time: ", start_time
        print "end time: ", end_time
        print "secs:\n", secs
        print "grafana:\n", grafana_value
        print "max_usage:  ", max_usage
        print "==============================="
    fig, ax = plt.subplots()
    
    avg = [sum([float(x) for x in grafana_value], 0.0) / len(grafana_value)]*len(grafana_value)
    
    if (len(secs)/10) > 0:
        ax.set_xticks([secs[x] for x in range(len(secs)) if x % (len(secs)/10) == 0 ])
    else:
        ax.set_xticks(secs)

    # Plot the date using plot_date rather than plot
    aaa = ax.plot_date(secs, grafana_value, ls="-", label="usage", marker=".", color="g")
    aaa = ax.plot_date(secs, avg, ls="--", label="avg", marker="", color="r")
    # Choose your xtick format string
    date_fmt = '%m-%d-%y %H:%M:%S'
    
    # Use a DateFormatter to set the data to the correct format.
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)
    #plt.axis([grafana_value[-1], grafana_value[0], secs[-1], secs[0]])
    
    legend = ax.legend(loc='upper right')
   
    fig.autofmt_xdate()
    average = str("%.3f" % (sum([float(x) for x in grafana_value], 0.0) / len(grafana_value)))    

    #plt.plot(time_stamp, grafana_value)
    plt.setp(aaa, color='r', linewidth=2.0)
    plt.xlabel('datetime (UTC)')
    plt.ylabel(y_label)
    plt.title(title+": "+average+"\nmax rate: "+str(max_usage)+"\nfrom "+start_time+"\nto "+end_time)
    plt.grid(True)
    fig.set_size_inches(12, 8)
    plt.savefig(filename)
    plt.cla()
    plt.close(fig)
    return max_usage, average

def plotting_multiple(time_stamp, grafana_list, filename, title, y_label, label_list, marker_list, debug="n", node=""):
#    dir_name = "report_image_"+datetime.datetime.fromtimestamp(int(time_stamp[0])).strftime("%d_%m_%Y_%H:%M:%S")+"_to_"+datetime.datetime.fromtimestamp(int(time_stamp[-1])).strftime("%d_%m_%Y_%H:%M:%S")
    filename = dir_name+"/"+filename
    image_files.append(filename)
    if time_stamp == []:
        return
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    start_time = datetime.datetime.fromtimestamp(int(time_stamp[0])).strftime('%c')
    end_time = datetime.datetime.fromtimestamp(int(time_stamp[-1])).strftime('%c')
    
    max_usage = []
    ave_usage = []
    secs = mdate.epoch2num(time_stamp)
    fig, ax = plt.subplots()
    
    if (len(secs)/10) > 0:
        ax.set_xticks([secs[x] for x in range(len(secs)) if x % (len(secs)/10) == 0 ])
    else:
        ax.set_xticks(secs)

    if debug == "y":
        print "==============================="
        print "start time: ", start_time
        print "end time: ", end_time
        print "secs:\n", secs
        print "grafana:\n", grafana_value
        print "max_usage:  ", max_usage
        print "==============================="

    count = 0

    for grafana_value in grafana_list:     
        ave_usage.append(str("%.3f" % (sum([float(x) for x in grafana_value], 0.0) / len(grafana_value))))
        max_usage.append(max([float(i) for i in grafana_value]))
        # Plot the date using plot_date rather than plot
#        print "==========================="
#        print "count = ", count
#        print "marker = ", markers[count]
#        print "color = ", colors[count]
#        print "==========================="

        aaa = ax.plot_date(secs, grafana_value, ls="-", label=label_list[count], marker=marker_list[count])
        count += 1
 
    # Choose your xtick format string
    date_fmt = '%m-%d-%y %H:%M:%S'
    
    # Use a DateFormatter to set the data to the correct format.
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)
    #plt.axis([grafana_value[-1], grafana_value[0], secs[-1], secs[0]])
    
    legend = ax.legend(loc='upper right')
   
    fig.autofmt_xdate()

    #plt.plot(time_stamp, grafana_value)
    plt.setp(aaa, color='r', linewidth=2.0)
    plt.xlabel('datetime (UTC)')
    plt.ylabel(y_label)
    title = "                          {:>40}{:>20}{:>20}{:>20}".format(node, "max", "average", "(GB)")
    for i in range(len(max_usage)):
        title += "\n{:>40}{:>20}{:>20}{:>20}".format(label_list[i], max_usage[i], ave_usage[i], "")
    plt.title(title, size=10)
    plt.grid(True)
    fig.set_size_inches(12, 8)
    plt.savefig(filename)
    plt.cla()
    plt.close(fig)
    return max_usage, ave_usage

def none_negative_deriv(grafana_value):
    grafana_value = [abs(float(j)-float(i)) for i, j in zip(grafana_value[:-1], grafana_value[1:])]
    return grafana_value

def scale(grafana_value, divisor):
    grafana_value = map(lambda x: "%.3f"%(float(x)/divisor), grafana_value)
    return grafana_value

def get_memory(node, from_time, until_time):
    path = node+"/SCG/memory/memory/used.wsp"
    mem_data = grafana_ret(path, from_time, until_time, True)
    time_stamp, grafana_value = mem_data.get_data()
    grafana_value = scale(grafana_value, 1024*1024*1024) 
    filename = node+"_memory_usage.png"
    maximum, average = plotting(time_stamp, grafana_value, filename, node + " average memory usage", "memory used (GB)")
    reports[node]["memory"] = {"avg": average, "max": maximum}

def get_disk_io(node, from_time, until_time):
    path = node+"/SCG/disk/sda/disk_octets/"
    from_time -= 60
    disk_data = grafana_ret(path+"read.wsp", from_time, until_time, True)
    time_stamp, grafana_value = disk_data.get_data() 
    time_stamp = time_stamp[1:]
    grafana_value = none_negative_deriv(grafana_value)
    grafana_value = scale(grafana_value, 60*1024)
    maximum, average = plotting(time_stamp, grafana_value, node+"_disk_read.png", node + " average disk read rate", "disk read rate (KB)")
    reports[node]["disk_read"] = {"avg": average, "max": maximum}

    disk_data = grafana_ret(path+"write.wsp", from_time, until_time, True)
    time_stamp, grafana_value = disk_data.get_data()
    time_stamp = time_stamp[1:]
    grafana_value = none_negative_deriv(grafana_value)
    grafana_value = scale(grafana_value, 60*1024*1024)
    maximum, average = plotting(time_stamp, grafana_value, node+"_disk_write.png", node + " average disk write rate", "disk write rate (MB)")
    reports[node]["disk_write"] = {"avg": average, "max": maximum}

def get_interface_io(node, from_time, until_time):
    path = node+"/SCG/interface/"
    interfaces = ["br0", "br1", "br2"]
    for interface in interfaces:
       reports[node][interface] = {}
       path_temp = path+interface
       from_time -= 60

       rx_data = grafana_ret(path_temp+"/if_octets/rx.wsp", from_time, until_time, True)
       time_stamp, grafana_value = rx_data.get_data()
       time_stamp = time_stamp[1:]
       grafana_value = none_negative_deriv(grafana_value)
       grafana_value = scale(grafana_value, 8*1024)
       maximum, average = plotting(time_stamp, grafana_value, node+"_"+interface+"_rx.png", node + " average rx rate", "rx rate (KB)")
       reports[node][interface]["rx"] = {"avg": average, "max": maximum}

       tx_data = grafana_ret(path_temp+"/if_octets/tx.wsp", from_time, until_time, True)
       time_stamp, grafana_value = tx_data.get_data()
       time_stamp = time_stamp[1:]
       grafana_value = none_negative_deriv(grafana_value)
       grafana_value = scale(grafana_value, 8*1024)
       
       maximum, average = plotting(time_stamp, grafana_value, node+"_"+interface+"_tx.png", node + " average tx rate", "tx rate (KB)")
       reports[node][interface]["tx"] = {"avg": average, "max": maximum}
        
def get_file_system_usage(node, from_time, until_time):
    path = node+"/exec/data/size/gauge/cassandra_wsg_size.wsp"
    wsg_size_data = grafana_ret(path, from_time, until_time, True)
    time_stamp, grafana_value = wsg_size_data.get_data()
    grafana_value = scale(grafana_value, 1024*1024)
    maximum, average = plotting(time_stamp, grafana_value, node+"_"+"cassandra_wsg_size.png", node + " average size", "cassandra wsg size (MB)")
    reports[node]["cassandra_wsg_size"] = {"avg": average, "max": maximum}

    path = node+"/exec/data/size/gauge/elasticsearch_indices_size.wsp"
    wsg_size_data = grafana_ret(path, from_time, until_time, True)
    time_stamp, grafana_value = wsg_size_data.get_data()
    grafana_value = scale(grafana_value, 1024*1024*1024)
    maximum, average = plotting(time_stamp, grafana_value, node+"_"+"elasticsearch_indices_size.png", node + " average size", "elasticsearch indices size (GB)")
    reports[node]["elasticsearch_indices_size"] = {"avg": average, "max": maximum}

    path = node+"/exec/data/size/gauge/data_folder_usage_size.wsp"
    wsg_size_data = grafana_ret(path, from_time, until_time, True)
    time_stamp, grafana_value = wsg_size_data.get_data()
    grafana_value = scale(grafana_value, 1024*1024*1024)
    maximum, average = plotting(time_stamp, grafana_value, node+"_"+"data_folder_usage_size.png", node + " average size", "data folder usage size (GB)")
    reports[node]["data_folder_usage_size"] = {"avg": average, "max": maximum}

def get_jmx_heap(node, from_time, until_time):
    jmx_list = ["jmx-cassandra", "jmx-configurer", "jmx-eventReader", "jmx-idm", "jmx-mqttClient", "jmx-scguniversalexporter", "jmx-tomcat" ,"jmx-captiveportal", "jmx-communicator", "jmx-elasticsearch", "jmx-greyhound", "jmx-monitor", "jmx-northbound", "jmx-scheduler"]
    wsg_list = ["Heap_Memory_Usage_committed.wsp", "Heap_Memory_Usage_max.wsp", "Heap_Memory_Usage_init.wsp", "Heap_Memory_Usage_used.wsp"]
    marker_list = [">", "<", "^", "v"]
    for jmx in jmx_list:
        path = node+"/"+jmx+"/GenericJMX/Memory/gauge/"
        grafana_list = []
        maximum_list = []
        ave_list = []
        for wsg in wsg_list:
            path_heap = path+wsg
            heap_data = grafana_ret(path_heap, from_time, until_time, True)
            time_stamp, grafana_value = heap_data.get_data()
            grafana_value = scale(grafana_value, 1024*1024*1024)
            grafana_list.append(grafana_value)

        maximum, average = plotting_multiple(time_stamp, grafana_list, node+"_"+jmx+".png", node + " average size", "jmx heap size (GB)", [i.split(".")[0] for i in wsg_list], marker_list, node=node)
        maximum_list.append(maximum)
        ave_list.append(average)
    reports[node]["jmx_heap_size"] = {"avg": ave_list, "max": maximum_list}

def get_cpu(node, from_time, until_time):
    path = node+"/SCG/cpu/"
    sources = ["idle", "interrupt", "nice", "softirq", "steal", "system", "user", "wait"]
    values = {}
    for source in sources:
        from_time -= 60
        mem_data = grafana_ret(path+"0/cpu/"+source+".wsp", from_time, until_time, False)
        time_stamp, grafana_value = mem_data.get_data()
        grafana_value = none_negative_deriv(grafana_value)
        grafana_value = scale(grafana_value, 60)
        for i in range(1, 24):
            mem_data = grafana_ret(path+str(i)+"/cpu/"+source+".wsp", from_time, until_time, False)
            time_stamp, grafana_value_temp = mem_data.get_data()
            grafana_value_temp = none_negative_deriv(grafana_value_temp)
            grafana_value_temp = scale(grafana_value_temp, 60)
            grafana_value = [float(x)+float(y) for x, y in zip(grafana_value, grafana_value_temp)] 
        values[source] = dict(zip(time_stamp, grafana_value))
    results = []
    time_stamp = values["idle"].keys()
    time_stamp.sort()

    for time in time_stamp:
        total = 0.0
        for source in values.keys():
            if time in values[source]:
                total += values[source][time]
        if total != 0:
            results.append(round(((total-values["idle"][time])/total)*100, 2))
        else:
            results.append(0.0)
    time_stamp = map(lambda x: x+60, time_stamp)
    maximum, average = plotting(time_stamp, results, node+"_cpu.png", node + " average cpu usage", "cpu usag (%)")
    reports[node]["cpu"] = {"avg": average, "max": maximum}

def plot_nodes(nodes, from_time, until_time):
    global reports
    for node in nodes:
        reports[node] = {}
        get_memory(node, from_time, until_time)
        get_disk_io(node, from_time, until_time)
        get_cpu(node, from_time, until_time)
        get_interface_io(node, from_time, until_time)
        get_file_system_usage(node ,from_time, until_time) 
        get_jmx_heap(node ,from_time, until_time) 

def open_file( name ) :
    return file( '%s.rtf' % name, 'w' )
    
if __name__ == "__main__":
    global dir_name
    global image_files
    try:
        import whisper
    except ImportError:
        raise SystemExit('[ERROR] Please make sure whisper is installed properly')
    
    _DROP_FUNCTIONS = {
        'zeroes': lambda x: x != 0,
        'nulls': lambda x: x is not None,
        'empty': lambda x: x != 0 and x is not None
    }
    
    # Ignore SIGPIPE
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    
    option_parser = optparse.OptionParser() 
    option_parser.add_option('--json', default=False, action='store_true',
      help="Output results in JSON form")
    option_parser.add_option('--pretty', default=False, action='store_true',
      help="Show human-readable timestamps instead of unix times")
    option_parser.add_option('--drop',
                             choices=list(_DROP_FUNCTIONS.keys()),
                             action='store',
                             help="Specify 'nulls' to drop all null values. \
    Specify 'zeroes' to drop all zero values. \
    Specify 'empty' to drop both null and zero values")
    
    (options, args) = option_parser.parse_args()
    opt_selected = False
    while opt_selected == False:
        option = raw_input("Please select how you want to detetmine the time range:\n1. Enter start and end time.\n2. Enter the duration from past to now.\n")
        try:
            if option == "1" or option == "2":   
                opt_selected = True
        except:
            pass
    
    if option == "1":
        local_tz = pytz.timezone("Asia/Taipei")
        start = raw_input("please enter the start time: yyyy mm dd hh mm\n")
        start = datetime.datetime.strptime(start, "%Y %m %d %H %M")
        start_local = local_tz.localize(start)
        from_time = start_local.astimezone(pytz.utc)
        until = raw_input("please enter the end time: yyyy mm dd hh mm\n")
        until = datetime.datetime.strptime(until, "%Y %m %d %H %M")
        until_local = local_tz.localize(until)
        until_time = until_local.astimezone(pytz.utc)
        from_time = int(time.mktime(start_local.timetuple()))
        until_time = int(time.mktime(until_local.timetuple()))
    else:   
        now = int(time.time())
        _from = raw_input("Please enter the duration from now in minutes:\n")
        from_time = now - (60 * int(_from))
        until_time = now

    print "start_time:" ,datetime.datetime.fromtimestamp(int(from_time))    
    print "end_time:" ,datetime.datetime.fromtimestamp(int(until_time))    
    
    dir_name = "report_image_"+start_local.strftime("%Y_%m_%d_%H:%M:%S")+"_to_"+until_local.strftime("%Y_%m_%d_%H:%M:%S")
    
    nodes = []
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
        nodes.append(dirnames)
    nodes[0] = [x for x in nodes[0] if "node" in x]
    print "nodes: ", nodes[0]
    plot_nodes(nodes[0], from_time, until_time) 

    csv_writer = csv.writer(open(dir_name+"/summary.csv", "w"), lineterminator='\n')
    csv_writer.writerow(["start time (UTC)", datetime.datetime.fromtimestamp(int(from_time)).strftime("%d_%m_%Y_%H:%M:%S")])
    csv_writer.writerow(["end time (UTC)", datetime.datetime.fromtimestamp(int(until_time)).strftime("%d_%m_%Y_%H:%M:%S")])
    csv_writer.writerow([" ", "cpu (%)", " ", "memory (GB)", " ", "disk write(MB/s)", " ", "disk read (KB/s)"])
    csv_writer.writerow([" ", "avg", "max", "avg", "max", "avg", "max", "avg", "max"])
    for node in sorted(reports.keys()):
        csv_writer.writerow([node, reports[node]["cpu"]["avg"], reports[node]["cpu"]["max"], reports[node]["memory"]["avg"], reports[node]["memory"]["max"], reports[node]["disk_write"]["avg"], reports[node]["disk_write"]["max"], reports[node]["disk_read"]["avg"], reports[node]["disk_read"]["max"]])

    pdf = FPDF()
    imagelist = image_files 
    # imagelist is the list with all image filenames
    for image in imagelist:
        pdf.add_page(orientation = 'L')
        pdf.image(image, 0,0,300,200)
    pdf.output(dir_name+"/reports.pdf", "F")

