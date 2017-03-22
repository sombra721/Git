#!/bin/bash

source data_gen_util.sh
source apsim.cfg
source constant.cfg

if [ -z "$SZIP" ]; then
    echo "Please input the SZ IP address to the configuration file."
    exit 1
fi

if [ -z "$FWVER" ]; then
    echo "Please input the AP Firmware version to the configuration file."
    exit 1
fi

# log file location
set_log_level() {
    case ${LOG_LEVEL:=1} in
        0)
          WSGCLIENT_LOG_FILE="/dev/null"
          HOSTAPD_LOG_FILE="/dev/null"
          COLLECTD_LOG_FILE="/dev/null"
          SSH_TUNNEL_LOG_FILE="/dev/null"
          MDPROXY_LOG_FILE="/dev/null"
          MSGDIST_LOG_FILE="/dev/null"
          SM_LOG_FILE="/dev/null"
          MD_LOG_FLAG=0
          ;;
        1)
          WSGCLIENT_LOG_FILE="$SIMTARGET/log/wsgclient.log"
          HOSTAPD_LOG_FILE="$SIMTARGET/log/hostapd.log"
          COLLECTD_LOG_FILE="$SIMTARGET/log/collectd.log"
          SSH_TUNNEL_LOG_FILE="$SIMTARGET/log/ssh_tunnel.log"
          MDPROXY_LOG_FILE="$SIMTARGET/log/mdproxy.log"
          MSGDIST_LOG_FILE="$SIMTARGET/log/MsgDist.log"
          SM_LOG_FILE="$SIMTARGET/log/sessionMgr.log"
          MD_LOG_FLAG=1
          ;;
        *)
          WSGCLIENT_LOG_FILE="$SIMTARGET/log/wsgclient.log"
          HOSTAPD_LOG_FILE="$SIMTARGET/log/hostapd.log"
          COLLECTD_LOG_FILE="$SIMTARGET/log/collectd.log"
          SSH_TUNNEL_LOG_FILE="$SIMTARGET/log/ssh_tunnel.log"
          MDPROXY_LOG_FILE="$SIMTARGET/log/md.log"
          MSGDIST_LOG_FILE="$SIMTARGET/log/MsgDist.log"
          SM_LOG_FILE="$SIMTARGET/log/sessionMgr.log"
          MD_LOG_FLAG=1
          ;;
    esac
}

stop_sshtunnel () {
    pkill -9 -F $SSH_TUNNEL_PID_FILE &>> $SSH_TUNNEL_LOG_FILE
    rm -f $SSH_TUNNEL_PID_FILE

    if [ -f ./tmp/wsg-server.now ]; then
        mv ./tmp/wsg-server.{now,old}
    fi
}

# ap_watchdog takes resposiblity for ssh tunnel and calls it when ssh tunnel
# disappeared.  wsgclient also calls it when it founds that connection (e.g.,
# heartbeat, http requests...) failed.
start_sshtunnel(){
    stop_sshtunnel
    LOCAL_HOST="localhost"
    OPENSSH_PRIVATE_KEY="./writable/data/user-certs/key.pem"
    chmod 600 $OPENSSH_PRIVATE_KEY

    if [ ! -z $1 ]; then
        ip=$1
    elif [ -f ./tmp/wsg-server.now ]; then
        ip=$(cat ./tmp/wsg-server.now)
    elif [ -f ./tmp/wsg-server ]; then
        ip=$(cat ./tmp/wsg-server)
    fi


    # Start
    echo "Start executing ssh:$SSN" >> $SSH_TUNNEL_LOG_FILE
    echo "Sim-$SSN:$DATETIME" >> $SSH_TUNNEL_LOG_FILE

    echo "$CUR_DIR/ssh $SSHNOHOSTCHK $IPV6 -N -i $OPENSSH_PRIVATE_KEY" \
        "-L $rcliport:$LOCAL_HOST:8083" \
        "-L $commport:$LOCAL_HOST:80" \
        "-L $eventport:$LOCAL_HOST:514" \
        "-L $((6001+$sshport)):$LOCAL_HOST:9081" \
        "-L $((12101+$sshport)):$LOCAL_HOST:11211" \
        "-L $((3201+$sshport)):$LOCAL_HOST:1884" \
        "-L $msl_ssh_port:$LOCAL_HOST:9191 sshtunnel@$ip" \
        > .ssh_cmd

    # The $CUR_DIR/ssh is a link, check it at runtime to make sure what version
    # is being used
    $CUR_DIR/ssh $SSHNOHOSTCHK $IPV6 -N -i $OPENSSH_PRIVATE_KEY \
        -L $rcliport:$LOCAL_HOST:8083 \
        -L $commport:$LOCAL_HOST:80 \
        -L $eventport:$LOCAL_HOST:514 \
        -L $((6001+$sshport)):$LOCAL_HOST:9081 \
        -L $((12101+$sshport)):$LOCAL_HOST:11211 \
        -L $((3201+$sshport)):$LOCAL_HOST:1884 \
        -L $msl_ssh_port:$LOCAL_HOST:9191 sshtunnel@$ip \
        -o "ExitOnForWardFailure=yes" \
        &>> $SSH_TUNNEL_LOG_FILE &
    echo $! > "$SSH_TUNNEL_PID_FILE"

    #echo $ip > tmp/wsg-server
    if [ -f ./tmp/wsg-server.now ]; then
        mv ./tmp/wsg-server{.now,}
    fi

    ./shmrpm -p wsgclientsim/current_sshtunnel_ip=$ip
    echo "ssh executed, pid: $!" >> $SSH_TUNNEL_LOG_FILE
}

start_md(){
    #Follow md_tunnel.py's steps
    pkill -9 -F $MDPROXY_PID_FILE &>> $MDPROXY_LOG_FILE
    pkill -9 -F $MSGDIST_PID_FILE &>> $MSGDIST_LOG_FILE
    rm -f $MDPROXY_PID_FILE $MSGDIST_PID_FILE /tmp/sm_md"$ssn_num" /tmp/wsgclient_md"$ssn_num"

    mdproxyport=$(($radiusport+20000))
    mdcfgfile="rks_mfw_ap.conf"

    $MAIN_PATH/bin/MsgDist ap_md \
        -debug \
        -cfgFile $SIMTARGET/md/"$mdcfgfile" \
        -localMac "$DEV_MAC" \
        >> $MSGDIST_LOG_FILE &
    echo $! > $MSGDIST_PID_FILE

    $MAIN_PATH/bin/mdproxy \
        -s "udp:$radiusport:1812:scg_radius" \
        -s "udp:$accountport:1813:scg_radius" \
        -s "udp:$mdproxyport:$mdproxyport:scg_sessmgr" \
        -cfgFile $SIMTARGET/md/$mdcfgfile \
        >> $MDPROXY_LOG_FILE &
    echo $! > $MDPROXY_PID_FILE
}

start_sessionmgr(){
    rm -f md/sessionMgr.log
    rm -f md/sessionMgr.ipc.socket
    ln -s ../tmp/sessionMgr.ipc.socket md/sessionMgr.ipc.socket
    $MAIN_PATH/bin/sessionMgr -s -f $SM_LOG_FILE -m 0xfff8 >> $SM_LOG_FILE & echo $! > $SESSIONMGR_PID_FILE
}

start_hostapd() {
    mkdir -p $SIMTARGET/var/run
    $MAIN_PATH/bin/hostapd_sim -m $DEV_MAC -d 4 >> $HOSTAPD_LOG_FILE 2>&1 &
    echo $! > "$HOSTAPD_PID_FILE"
}

init_wlan(){
    #HACK! Setup Wlans persistent keys using jardrpm commands. HACK!
    firstWlan=0
    lastWlan=0
    enableWlan=0
    #wlansPerRadio=7
    ./shmrpm -p wlan-extend-maxwlans=27
    ./shmrpm -p extended-64ssid=1
    wlansPerRadio=31

    wifiCnt=`./shmrpm -g wlan-wifi-cnt | awk -F"=" '{print $2}'`
    if [ -z "$wifiCnt" ];then
        wifiCnt=1
    fi

    for r in `seq 1 $wifiCnt`
    do
        n=$(($r-1))
        wlanNum=`./shmrpm -g wlan-extend-maxwlans | awk -F"=" '{print $2}'`
        lastWlan=$(($firstWlan+$wlanNum-1))
        for wl in `seq $firstWlan $lastWlan`
        do
            ./shmrpm -p wlans/wlan$wl/wlan-isallowed=allow
            ./shmrpm -p wlans/wlan$wl/wlan-created-defined=1
            ./shmrpm -p wlans/wlan$wl/wlan-if-flags=0
            if [ $wl -gt $wlansPerRadio ];then
                ./shmrpm -p wlans/wlan$wl/wlan-if-parent=1
            else
                ./shmrpm -p wlans/wlan$wl/wlan-if-parent=0
            fi
            ./shmrpm -p wlans/wlan$wl/wlan-service=13
            ./shmrpm -p wlans/wlan$wl/wlan-ssid=Wireless"$wl"
            if [ $wl -lt $enableWlan ];then
                ./shmrpm -p wlans/wlan$wl/wlan-state=up
            else
                ./shmrpm -p wlans/wlan$wl/wlan-state=down
            fi
            ./shmrpm -p wlans/wlan$wl/wlan-type=ap
            ./shmrpm -p wlans/wlan$wl/wlan-userdef-name=Wireless"$wl"
            ./shmrpm -p wlans/wlan$wl/wlan-userdef-text=Wireless"$wl"
            ./shmrpm -p wlans/wlan$wl/wlan-rtsthr=256
            ./shmrpm -p wlans/wlan$wl/wlan-dtim-period=1
            ./shmrpm -p ifs/wlan$wl/port-type=0
            ./shmrpm -p ifs/wlan$wl/vlans=1
            ./shmrpm -p ifs/wlan$wl/tun-tos=' '
            ./shmrpm -p ifs/wlan$wl/tun-tos-plist=' '
        done
        ./shmrpm -p wifi$n/wlan-txpower=max

        ./shmrpm -p wifi$n/wlan-maxwlans2=27

        firstWlan=$(($firstWlan+32))
        enableWlan=$(($enableWlan+32))
    done

    #Configure WSGC-SIM default values
    ./shmrpm -p device-name="Sim-$SSN"

    rr=`echo $URL|grep ':'`
    if [ -z "$rr" ]; then
        ./shmrpm -p l3/br0/0/ipmode=1
    else
        ./shmrpm -p l3/br0/0/ipmode=2
    fi

    ./shmrpm -p wsgclientsim/scgIpAddr="$SZIP"

    #HACK!!Disable tunnel at startup.
    ./shmrpm -p tunnelmgr/tunnelmgr-tunnel-enable=0
}

set_factory(){
    LOCAL_HOST="127.0.0.1"

    # XXX: .dev_mac file should be generated before shmrpm commands.
    echo "$DEV_MAC" > ./.dev_mac

    #Write customer and model
    echo "$CUSTOMER" > ./v54bsp/customer
    echo "$MODEL" > ./v54bsp/model
    if [ ! -f "./etc/version" ]; then
        echo -n "$FWVER" > ./v54bsp/fwver
        echo -n "$FWVER" > ./etc/version
    fi


    if [ ! -h "$SIMTARGET/usr/sbin/wsgclient" ]; then
        mkdir -p $SIMTARGET/usr/sbin
        ln -s $MAIN_PATH/bin/wsgclient $SIMTARGET/usr/sbin/wsgclient
    fi
    if [ ! -h "wsgclient" ]; then
        ln -s ./bin/wsgclient wsgclient
    fi
    if [ ! -h "ssh" ]; then
        ln -s $(which ssh) ssh
    fi

    #Create necessary flags for factory reset
    echo "1" > "$SIMTARGET"/.bootstrap
    echo "1      tcp    ap_md         scg_md      0    [$LOCAL_HOST]:$msl_ssh_port   bi-directional" >  ./md/rks_mfw_ap.conf
    echo "2      uds    ap_sessmgr    ap_md       0    /tmp/sm_md$SSN                bi-directional" >> ./md/rks_mfw_ap.conf
    echo "3      tcp    md_proxy      ap_md       0    [$LOCAL_HOST]:$scg_msl_port   bi-directional" >> ./md/rks_mfw_ap.conf
    echo "4      uds    ap_wsgclient  ap_md       0    /tmp/wsgclient_md$SSN         bi-directional" >> ./md/rks_mfw_ap.conf
    echo "5      tcp    logclient     ap_md       0    [$LOCAL_HOST]:$scg_log_port   bi-directional" >> ./md/rks_mfw_ap.conf
    echo "6      uds    ap_nbrd       ap_md       0    /tmp/nbrd_md$SSN              bi-directional" >> ./md/rks_mfw_ap.conf
    echo "7      uds_co ap_collectd   ap_md       0    /tmp/collectd_md$SSN          bi-directional" >> ./md/rks_mfw_ap.conf

    if [ -f "./etc/version" ]; then
        ./shmrpm -p wsgclientsim/fw-ver="$(cat ./etc/version)"
    else
        ./shmrpm -p wsgclientsim/fw-ver="$FWVER"
    fi
    ./shmrpm -p wsgclientsim/dev-mac="$DEV_MAC"
    gen_dev_ip START_AP_IP devip_str
    ./shmrpm -p wsgclientsim/dev-ip="$devip_str"

    #Set up factory default
    echo "1" > .bootstrap

    #Remove the persistent keys
    rm -rf writable/data/persist-stg

    #Update URL
    ./shmrpm -p wsgclient/wsgServerList=$URL

    #Update zone id
    ./shmrpm -p wsgclient/zone-id=1

    #Update cluster name
    ./shmrpm -p wsgclient/cluster-name="jardcluster"

    # heartbeat-interval
    ./shmrpm -p wsgclient/heartbeat-interval=30

    #Enable Data Collect
    ./shmrpm -p dc_period_duration=15
    ./shmrpm -p dc_enab_disab=1

    ./shmrpm -p wsgclient/aggregate-stats-enable=1
    ./shmrpm -p ipt/provisioning-tag=

    #Remove state files
    rm -rf tmp/wsgclient/*
    ./shmrpm -p wsgclient/managed=0
    if [ "$WITHWISPR" = "0" ];then
        ./shmrpm -p wsgclientsim/wispr=0
    else
        ./shmrpm -p wsgclientsim/wispr=1
    fi

    # init collectd settings
    if [ "$COLLECTD_AI" != "0" ];then
        ./shmrpm -p collectd/routine_ai=$COLLECTD_AI
    fi
    if [ "$COLLECTD_RI" != "0" ];then
        ./shmrpm -p collectd/routine_ri=$COLLECTD_RI
    fi

    ./shmrpm -p wlan-wifi-cnt=2
    ./shmrpm -p wifi0/wlan-maxwlans2=27
    ./shmrpm -p wifi0/wlan-extend-maxwlans=27
    ./shmrpm -p wifi0/wlan-mode=11g
    ./shmrpm -p wifi1/wlan-maxwlans2=27
    ./shmrpm -p wifi1/wlan-extend-maxwlans=27
    ./shmrpm -p wifi1/wlan-mode=11na
    ./shmrpm -p all_powerful_login_name=super
    ./shmrpm -p all_powerful_login_password=sp-admin
    ./shmrpm -p home_user_login_name=
    ./shmrpm -p home_user_login_password=password
    ./shmrpm -p wlan-wsta-max-rks=512

    # ./shmrpm -p wsgclientsim/current_sshtunnel_ip=$SZIP # deprecated?
    ./shmrpm -p l3/br0/0/ipmode=1
    ./shmrpm -p wsgclient/status-interval=30
    ./shmrpm -p wsgclient/config-interval=30

    init_wlan
}

start_wsgclient(){
    # Clean wsgclient config ID
    rm -r ./writable/data/wsgclient/* 2> /dev/null
    # Reset wsgclient's rpm key: 'registered'
    local mac_str=$(cat .dev_mac | tr '[:upper:]' '[:lower:]')
    rm -f /dev/shm/sim/$mac_str/rpm/wsgclient/registered


    echo "$(date) ./sysinit.sh start_wsgclient" >> $WSGCLIENT_LOG_FILE
    $MAIN_PATH/bin/wsgclient -v >> $WSGCLIENT_LOG_FILE 2>&1 &
    echo $! > "$WSGCLIENT_PID_FILE"
}

start_collectd(){
    $MAIN_PATH/bin/collectd >> $COLLECTD_LOG_FILE 2>&1 &
    echo $! > "$COLLECTD_PID_FILE"
}

init(){
    echo "==Bring up the sim-AP[$SSN]=="
    set_factory
    start_md
    start_hostapd
    start_wsgclient
    start_sessionmgr
    start_collectd
}

boot () {
    if [ -f .dev_mac ]; then
        reboot
    else
        init
    fi
}

reboot () {
    local pid

    pid=$(cat $MSGDIST_PID_FILE 2> /dev/null)
    if grep $MSGDIST_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid
        rm $MSGDIST_PID_FILE
    fi
    pid=$(cat $MDPROXY_PID_FILE 2> /dev/null)
    if grep $MDPROXY_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid
        rm $MDPROXY_PID_FILE
    fi
    pid=$(cat $SSH_TUNNEL_PID_FILE 2> /dev/null)
    if grep $SSH_TUNNEL_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid
        rm $SSH_TUNNEL_PID_FILE
    fi
    pid=$(cat $COLLECTD_PID_FILE 2> /dev/null)
    if grep $COLLECTD_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid
        rm $COLLECTD_PID_FILE
    fi
    pid=$(cat $SESSIONMGR_PID_FILE 2> /dev/null)
    if grep $SESSIONMGR_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid
        rm $SESSIONMGR_PID_FILE
    fi
    pid=$(cat $HOSTAPD_PID_FILE 2> /dev/null)
    if grep $HOSTAPD_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid  # XXX: msg queue and shm are not cleaned using SIGKILL
        rm $HOSTAPD_PID_FILE
    fi
    pid=$(cat $WSGCLIENT_PID_FILE 2> /dev/null)
    if grep $WSGCLIENT_CMD_PATTERN /proc/${pid}/cmdline &> /dev/null; then
        kill -9 $pid
        rm $WSGCLIENT_PID_FILE
    fi

    # XXX: It does not really work as expected as cleaning msg queues!
    # Brutally clean resources created by hostapd_sim
    local mac_str=$(cat .dev_mac | tr '[:upper:]' '[:lower:]')
    rm -r /dev/shm/sim/$mac_str/{$mac_str,ue} 2> /dev/null
    rm /dev/mqueue/$mac_str 2> /dev/null

    init;
}

# Script Entry point
set_log_level
CMD=$1
if [ -z "$CMD" ];then
    CMD=init
fi

case "$CMD" in
    init)
        init;;
    set_factory)
        set_factory;;
    start_sshtunnel)
        # if $2 exists, use it as destnation IP for ssh connection
        shift
        start_sshtunnel $*;;
    stop_sshtunnel)
        stop_sshtunnel;;
    start_wsgclient)
        start_wsgclient;;
    start_md)
        start_md;;
    start_sessionmgr)
        start_sessionmgr;;
    start_memcached)
        start_memcached;;
    start_collectd)
        start_collectd;;
    reboot)
        reboot;;
    boot)
        boot;;
    *)
        echo "Unknown command: $cmd. Exiting now..."
        exit 1;;
esac

exit 0

