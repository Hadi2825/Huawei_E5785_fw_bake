#!/bin/sh

get_metrics() {
    /app/oled_hijack/web_hook_client device signal 1 1
    /app/oled_hijack/web_hook_client monitoring status 1 1
    /app/oled_hijack/web_hook_client monitoring statusex 1 1
}

handle_xml_line() {
    LINE="$1"
    LINE="${LINE#<}"
    LINE="${LINE/<\/*/}"

    PARAM="${LINE/>*/}"
    VALUE="${LINE/*>/}"
    VALUE="${VALUE//[!0-9-]/}"

    if [ -z "$PARAM" -o -z "$VALUE" ]; then
        return
    fi

    case "$PARAM" in
        pci|sc|cell_id|rsrq|rsrp|rssi|sinr|rscp|ecio|mode|ulbandwidth|dlbandwidth|txpower|tdd|\
        ul_mcs|dl_mcs|rrc_status|rac|lac|tac|band|plmn|ims|connectionstatus|signalicon|\
        servicestatus|simstatus|simlockstatus|roamingstatus|networktype|networktypeex|wifistatus|\
        currentwifiuser|wificonnectionstatus|wifisignal|handover|multissidstatus|bridgestatus|\
        unreadmessage|onlineupdatestatus|datalimit|totaldownload|totalupload|usbtethering|\
        cradleusbstatus|wifiusbstatus|tempprotectstatus|messageisfull|BatteryStatus|BatteryLevel\
        |BatteryPercent|TotalWifiUser|currenttotalwifiuser|cellroam|usbup)
            echo "# HELP huawei_$PARAM The $PARAM"
            echo "# TYPE huawei_$PARAM counter"
            echo "huawei_$PARAM $VALUE"
        ;;
       earfcn|nei_cellid|ConnectionStatus|WifiConnectionStatus|SignalStrength|SignalIcon|\
       CurrentNetworkType|CurrentServiceDomain|RoamingStatus|simlockStatus|PrimaryDns|SecondaryDns|\
       PrimaryIPv6Dns|SecondaryIPv6Dns|CurrentWifiUser|SimStatus|WifiStatus|CurrentNetworkTypeEx|\
       wifiindooronly|wififrequence|flymode|WanPolicy|maxsignal|ServiceStatus|classify|networkname|\
       wlanssid|cradlenetlinestatus|cradleconnectionmode|cradleconnectstatus|currentdownloadrate|\
       currentuploadrate|monththreshold)
            # do nothing
       ;;
        *)
            #echo "unknown param='$PARAM' val='$VALUE' line='$LINE'"
        ;;
    esac
}

handle_net_stat_line() {
    LINE="$1"

    INTERFACE=""
    STAT_IDX=-1
    for VALUE in $LINE; do
        STAT_IDX="$((STAT_IDX+1))"
        STAT_STR=""
        case "$STAT_IDX" in
            0) INTERFACE="${VALUE//[!a-zA-Z0-9_]/}"; continue ;;
            1) STAT_STR="receive_bytes";;
            2) STAT_STR="receive_packets";;
            9) STAT_STR="transmit_bytes";;
            10) STAT_STR="transmit_packets";;
            *) continue;;
        esac

        case "$INTERFACE" in
            WiFi*|br*|eth*|lo|rmnet*|usb*|wl*) ;;
            *) break;
        esac

        echo "# HELP huawei_${STAT_STR}_${INTERFACE} The ${STAT_STR} on ${INTERFACE}"
        echo "# TYPE huawei_${STAT_STR}_${INTERFACE} counter"
        echo "huawei_${STAT_STR}_${INTERFACE} $VALUE"
    done
}

echo "Content-Type: text/plain"
echo ""

get_metrics | while IFS= read -r LINE; do
    handle_xml_line "$LINE"
done

cat /proc/net/dev | while IFS= read -r LINE; do
    handle_net_stat_line "$LINE"
done
