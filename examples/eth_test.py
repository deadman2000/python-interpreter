from pprint import pprint

from formats.net import EthernetFormat

#ETHERNET_DATA = '0007b4004d015404a660dc5e08004500006c2dd34000800600000a0a4e0771939aee7dbc24f5415c87ede7cc36f45018010264f1000013426974546f7272656e742070726f746f636f6c00000000001800054fbdafe756fcb629ce19178de30a26af5b934ca62d7142343033302d4f72725a55767452446a4762'
ETHERNET_DATA = '005056c00008000c29be8ca60800480000486046400040069084c0a89f81c0a89f01860a00000001010400020000edbc0050c52be4dd00000000a00216d054950000020405b40402080a0015849b0000000001030307'

ethernet = EthernetFormat()
data = bytes.fromhex(ETHERNET_DATA)
#data = b'\x01\x00^\x7f\xff\xfa\x00PV\xc0\x00\x08\x08\x00E\x00\x00\xca1\xa2\x00\x00\x01\x117\xdd\xc0\xa8\x9f\x01\xef\xff\xff\xfa\xe2R\x07l\x00\xb6\xc2dM-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 1\r\nST: urn:dial-multiscreen-org:service:dial:1\r\nUSER-AGENT: Google Chrome/66.0.3359.139 Windows\r\n\r\n'
result = ethernet.parse_bytes(data)
pprint(result)