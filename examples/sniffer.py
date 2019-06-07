import ipaddress

from winpcapy import WinPcapUtils, WinPcapDevices
from interpreter.formats.net import EthernetFormat

devices = WinPcapDevices.list_devices()
for name in devices.keys():
    print(name, ':', devices[name])

eth = EthernetFormat()
filter = None
# filter = ipaddress.IPv4Address('192.168.1.40')

def packet_callback(win_pcap, param, header, pkt_data):
    try:
        packet = eth.parse_bytes(pkt_data)
        if hasattr(packet, 'ip'):
            # print('%s -> %s  %s' % (packet.ip.source, packet.ip.dest, packet.ip.protocol))
            if hasattr(packet, 'ip') and hasattr(packet.ip, 'udp'):
                if filter is None or packet.ip.source == filter or packet.ip.dest == filter:
                    print('%s:%d -> %s:%d = %s' % (packet.ip.source, packet.ip.udp.src_port, packet.ip.dest, packet.ip.udp.dst_port, packet.ip.udp.data))
    except:
        print('PARSE ERROR')
        print(pkt_data)


WinPcapUtils.capture_on_device_name(list(devices.keys())[0], packet_callback)
