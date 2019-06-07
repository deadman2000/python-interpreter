import unittest
from ipaddress import IPv4Address
from formats.net import *

ETH_IP_TCP_DATA = b'\x00\x07\xb4\x00M\x01T\x04\xa6`\xdc^\x08\x00E\x00\x00l-\xd3@\x00\x80\x06\x00\x00\n\nN\x07q\x93\x9a\xee}\xbc$\xf5A\\\x87\xed\xe7\xcc6\xf4P\x18\x01\x02d\xf1\x00\x00\x13BitTorrent protocol\x00\x00\x00\x00\x00\x18\x00\x05O\xbd\xaf\xe7V\xfc\xb6)\xce\x19\x17\x8d\xe3\n&\xaf[\x93L\xa6-qB4030-OrrZUvtRDjGb'
ETH_IP_UDP_DATA = b'\x01\x00^\x7f\xff\xfa\x00PV\xc0\x00\x08\x08\x00E\x00\x00\xca1\xa2\x00\x00\x01\x117\xdd\xc0\xa8\x9f\x01\xef\xff\xff\xfa\xe2R\x07l\x00\xb6\xc2dM-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 1\r\nST: urn:dial-multiscreen-org:service:dial:1\r\nUSER-AGENT: Google Chrome/66.0.3359.139 Windows\r\n\r\n'


class TestPraserMethods(unittest.TestCase):
    maxDiff = None

    def test_bits_le(self):
        obj = BitParser(fields=[
            BitField('a', 1),
            BitField('b', 1),
            BitField('c', 1),
            BitField('d', 1),
            BitField('e', 1),
            BitField('f', 1),
            BitField('g', 1),
            BitField('h', 1),

            BitField('i', 1),
            BitField('j', 1),
            BitField('k', 1),
            BitField('l', 1),
            BitField('m', 1),
            BitField('n', 1),
            BitField('o', 1),
            BitField('p', 1),
        ]).parse_bytes(b'\x64\xc7')
        self.assertDictEqual(obj,
                             {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 1, 'g': 0, 'h': 0, 'i': 1, 'j': 1, 'k': 0,
                              'l': 0, 'm': 0, 'n': 1, 'o': 1, 'p': 1})

    def test_bits_be(self):
        obj = BitParser(fields=[
            BitField('a', 1),
            BitField('b', 1),
            BitField('c', 1),
            BitField('d', 1),
            BitField('e', 1),
            BitField('f', 1),
            BitField('g', 1),
            BitField('h', 1),

            BitField('i', 1),
            BitField('j', 1),
            BitField('k', 1),
            BitField('l', 1),
            BitField('m', 1),
            BitField('n', 1),
            BitField('o', 1),
            BitField('p', 1),
        ]).set_bigendian().parse_bytes(b'\x64\xc7')
        self.assertDictEqual(obj,
                             {'a': 0, 'b': 0, 'c': 1, 'd': 0, 'e': 0, 'f': 1, 'g': 1, 'h': 0, 'i': 1, 'j': 1, 'k': 1,
                              'l': 0, 'm': 0, 'n': 0, 'o': 1, 'p': 1})

    def test_optional(self):
        obj = DataBlock(fields=[
            NumberField('a', 1).optional(True),
            NumberField('b', 1).optional(False),
            NumberField('c', 1),
            NumberField('d', 1).optional(lambda o: o.c == 2),
            NumberField('e', 1).optional(lambda o: o.c == 48)
        ]).parse_bytes(b'\x01\x02\x03')
        self.assertDictEqual(obj, {'a': 1, 'c': 2, 'd': 3})

    def test_if(self):
        obj = DataBlock(fields=[
            NumberField('a', 1),
            IfField('b', (
                (lambda o: o.a == 1, StringField(count=2)),
                (lambda o: o.a == 2, NumberField(bytes_count=1))
            )),
            NumberField('c', 1)
        ]).parse_bytes(b'\x01\x31\x32\x02')
        self.assertDictEqual(obj, {'a': 1, 'b': '12', 'c': 2})

        obj = DataBlock(fields=[
            NumberField('a', 1),
            IfField('b', (
                (lambda o: o.a == 2, NumberField(bytes_count=1)),
                (lambda o: o.a == 1, DataBlock(fields=[
                    StringField('sa', 1),
                    StringField('sb', 1)
                ]))
            )),
            NumberField('c', 1)
        ]).parse_bytes(b'\x01\x31\x32\x02')
        self.assertDictEqual(obj, {'a': 1, 'b': {'sa': '1', 'sb': '2'}, 'c': 2})

    def test_case(self):
        obj = DataBlock(fields=[
            NumberField('a', 1),
            CaseField('b', lambda o: o.a, (
                (1, StringField(count=2)),
                (2, NumberField(bytes_count=1))
            )),
            NumberField('c', 1)
        ]).parse_bytes(b'\x01\x31\x32\x02')
        self.assertDictEqual(obj, {'a': 1, 'b': '12', 'c': 2})

        obj = DataBlock(fields=[
            NumberField('a', 1),
            CaseField('b', lambda o: o.a, (
                (2, NumberField(bytes_count=1)),
                (1, DataBlock(fields=[
                    StringField('sa', 1),
                    StringField('sb', 1)
                ]))
            )),
            NumberField('c', 1)
        ]).parse_bytes(b'\x01\x31\x32\x02')
        self.assertDictEqual(obj, {'a': 1, 'b': {'sa': '1', 'sb': '2'}, 'c': 2})

        obj = DataBlock(fields=[
            NumberField('a', 1),
            CaseField('b', lambda o: o.a, (
                (2, NumberField(bytes_count=1)),
                (3, DataBlock(fields=[
                    StringField('sa', 1),
                    StringField('sb', 1)
                ]))
            ), StringField(count=2)),
            NumberField('c', 1)
        ]).parse_bytes(b'\x01\x31\x32\x02')
        self.assertDictEqual(obj, {'a': 1, 'b': '12', 'c': 2})

    def test_eth_ip_tcp(self):
        ethernet = EthernetFormat()
        result = ethernet.parse_bytes(ETH_IP_TCP_DATA)
        example = {
            'dest': '0:7:b4:0:4d:1',
            'ip': {'dest': IPv4Address('113.147.154.238'),
                   'dscp': 0,
                   'ecn': 0,
                   'flags': 2,
                   'header_size': 5,
                   'id': 11731,
                   'offset': 0,
                   'options': '',
                   'protocol': IPProtocol.TCP,
                   'size': 108,
                   'source': IPv4Address('10.10.78.7'),
                   'sum': 0,
                   'tcp': {'ack_sn': 3888920308,
                           'checksum': 25841,
                           'data': b'\x13BitTorrent protocol\x00\x00\x00\x00'
                                   b'\x00\x18\x00\x05O\xbd\xaf\xe7V\xfc\xb6)'
                                   b'\xce\x19\x17\x8d\xe3\n&\xaf[\x93L\xa6-qB4030-OrrZUvtR'
                                   b'DjGb',
                           'dst_port': 9461,
                           'flags': 24,
                           'header_size': 5,
                           'options': '',
                           'res': 0,
                           'size': 258,
                           'sn': 1096583149,
                           'src_port': 32188,
                           'urg': 0},
                   'ttl': 128,
                   'version': 4},
            'padding': b'',
            'source': '54:4:a6:60:dc:5e',
            'type': EthernetDataType.IPv4
        }
        # pprint.pprint(result)
        self.assertDictEqual(result, example)

    def test_eth_ip_udp(self):
        ethernet = EthernetFormat()
        result = ethernet.parse_bytes(ETH_IP_UDP_DATA)
        example = {'dest': '1:0:5e:7f:ff:fa',
                   'ip': {'dest': IPv4Address('239.255.255.250'),
                          'dscp': 0,
                          'ecn': 0,
                          'flags': 0,
                          'header_size': 5,
                          'id': 12706,
                          'offset': 0,
                          'options': '',
                          'protocol': IPProtocol.UDP,
                          'size': 202,
                          'source': IPv4Address('192.168.159.1'),
                          'sum': 14301,
                          'ttl': 1,
                          'udp': {'checksum': 49764,
                                  'data': b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r'
                                          b'\nMAN: "ssdp:discover"\r\nMX: 1\r\nST: urn:dial-multi'
                                          b'screen-org:service:dial:1\r\nUSER-AGENT: Google Ch'
                                          b'rome/66.0.3359.139 Windows\r\n\r\n',
                                  'dst_port': 1900,
                                  'size': 182,
                                  'src_port': 57938},
                          'version': 4},
                   'padding': b'',
                   'source': '0:50:56:c0:0:8',
                   'type': EthernetDataType.IPv4
                   }
        # pprint.pprint(result)
        self.assertDictEqual(result, example)

    def test_model_validation(self):
        with self.assertRaises(FormatError):
            IfField(selector=(
                (lambda o: True, NumberField(bytes_count=1)),
            ))


if __name__ == '__main__':
    unittest.main()
