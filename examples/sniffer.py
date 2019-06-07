import ipaddress

from winpcapy import WinPcapUtils, WinPcapDevices
from formats.net import EthernetFormat

eth = EthernetFormat()
filter = ipaddress.IPv4Address('192.168.159.1')


def packet_callback(win_pcap, param, header, pkt_data):
    packet = eth.parse_bytes(pkt_data)
    if hasattr(packet, 'ip'):
        #print('%s -> %s  %s' % (packet.ip.source, packet.ip.dest, packet.ip.protocol))
        if hasattr(packet, 'ip') and hasattr(packet.ip, 'udp'):
        #if packet.ip.source == filter or packet.ip.dest == filter:
            print('%s:%d -> %s:%d = %s' % (packet.ip.source, packet.ip.udp.src_port, packet.ip.dest, packet.ip.udp.dst_port, packet.ip.udp.data))


WinPcapUtils.capture_on_device_name(r'\Device\NPF_{25F8ABD7-A88C-4410-A0BF-808E1813D0DA}', packet_callback)
