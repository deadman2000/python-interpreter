import datetime

from formats.net import EthernetFormat
from structure import *


# https://www.tcpdump.org/manpages/pcap-savefile.5.html
# https://wiki.wireshark.org/Development/LibpcapFileFormat
# http://www.tcpdump.org/linktypes.html
# TODO Other network types support

class PCapPacket(DataBlock):
    byteorder = ByteOrder.BE
    fields = [
        NumberField('datetime', 4).convert(datetime.datetime.fromtimestamp),
        NumberField('msecs', 4),
        NumberField('size', 4),
        NumberField('orig_size', 4),
        EthernetFormat('data').set_size(lambda p: p.size)  # TODO: Implement orig_size support?
    ]


class PCapFormat(DataBlock):
    byteorder = ByteOrder.BE
    fields = [
        NumberField('magic', 4).convert(hex),
        NumberField('ver_maj', 2),
        NumberField('ver_min', 2),
        NumberField('time_zone_offset', 4),
        NumberField('time_stamp_accuracy', 4),
        NumberField('snapshot_length', 4),
        NumberField('header_type', 4),
        ArrayField('packets',
                   element=PCapPacket())
    ]
