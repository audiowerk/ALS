#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Name: luminosus ArtNet library
# Python ArtNet library to send and receive ArtNet data
# Author: Tim Henning

# Copyright 2011 Tim Henning
# Luminosus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Luminosus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import struct
import threading
import random
import time

class Test():
    def run(self):
        artnet = ArtNet()
        artnet.daemon = True
        artnet.start()
        time.sleep(2)
        print artnet.own_ip
        print artnet.get_nodes()

class ArtNet(threading.Thread):
    def __init__(self, address=(0, 0, 0), mode='default', sending_method='unicast'):
        threading.Thread.__init__(self)
        self.address = address
        self.mode = mode
        self.sending_method = sending_method
        self.universes = [[0] * 513] * 16
        self.own_ip = "192.168.178.20"
        self.ip_check_id = random.randint(1, 512)
        self.nodes = []
        self.build_header()
    
    def build_header(self, eternity_port=1):
        header = []
        # Name, 7byte + 0x00
        header.append("Art-Net\x00")
        # OpCode ArtDMX -> 0x5000, Low Byte first
        header.append(struct.pack('<H', 0x5000))
        # Protocol Version 14, High Byte first
        header.append(struct.pack('>H', 14))
        # Order -> nope -> 0x00
        header.append("\x00")
        # Eternity Port
        header.append(chr(eternity_port))
        # Address
        net, subnet, universe = self.address
        header.append(struct.pack('<H', net << 8 | subnet << 4 | universe))
        self.header = "".join(header)
    
    def run(self):
        if self.mode in ("default"):
            if self.open_socket() is True:
                self.set_own_ip()
                self.ArtPoll()
                self.server()
            else:
                return False

    def open_socket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(("", 6454))
            self.s.sendto("ping", ("<broadcast>", 60000))
            return True
        except:
            try:
                self.s.close()
            except:
                pass
            print "Missing network connection. ArtNet module closed."
            return False

    def ArtPoll(self):
        content = []
        # Name, 7byte + 0x00
        content.append("Art-Net\x00")
        # OpCode ArtPoll -> 0x2000, Low Byte first
        content.append(struct.pack('<H', 0x2000))
        # Protocol Version 14, High Byte first
        content.append(struct.pack('>H', 14))
        # TalkToMe
        content.append(struct.pack('>H', 0b00000000))
        content.append(chr(0xe0))
        content = "".join(content)
        #print self.lang['send_ArtPoll']
        self.s.sendto(content, ("<broadcast>", 6454))

    def set_own_ip(self):
        content = []
        # id8, 7byte + 0x00
        content.append("Art-Net\x00")
        # OpCode ArtDMX -> 0x5000, Low Byte first
        content.append(struct.pack('<H', 0x6464))
        # Protocol Version 14, High Byte first
        content.append(struct.pack('>H', 14))
        # luminosus ip check
        content.append("luminosus_ip_check_%s" % self.ip_check_id)
        content = ''.join(content)
        self.s.sendto(content, ('<broadcast>', 6454))

    def server(self):
        print "ArtNet node started."
        while True:
            data, addr = self.s.recvfrom(2048)
            id8 = data[:8]
            version = struct.unpack('>H', data[10:12])[0]
            if not id8 == 'Art-Net\x00' and version == 14:
                print self.lang['invalid_id']
                continue
            opcode = struct.unpack('<H', data[8:10])[0]
            if opcode == 0x5000:
                self.handle_ArtDMX(data, addr)
            elif opcode == 0x2000:
                self.handle_ArtPoll(data, addr)
            elif opcode == 0x2100:
                self.handle_ArtPollReply(data, addr)
            elif opcode == 0x6464:
                self.handle_ip_check(data, addr)
            elif opcode == 0x9999:
                if data[12:] == str("luminosus_kill_signal_%s" % self.ip_check_id):
                    print "stop server"
                    break
            else:
                print "Received unknown package. OpCode: %s" % opcode
        print "server stopped"

    def handle_ArtDMX(self, data, addr):
        if addr[0] == self.own_ip:
            return False
        p_subnet = ord(data[14]) >> 4
        p_universe = ord(data[14]) - (p_subnet << 4)
        p_net = ord(data[15])
        if p_net != self.address[2] or p_subnet != self.address[1]:
            return False
        data_length = struct.unpack('>H', data[16:18])[0]
        self.universes[p_universe][1:data_length +1] = [ord(i) for i in data[18:]]

    def handle_ArtPoll(self, data, addr):
        if addr[0] != self.own_ip and addr not in self.nodes:
            self.nodes.append(addr)
        self.ArtPollReply()
    
    def ArtPollReply(self):
        content = []
        # Name, 7byte + 0x00
        content.append("Art-Net\x00")
        # OpCode ArtPollReply -> 0x2100, Low Byte first
        content.append(struct.pack('<H', 0x2100))
        # Protocol Version 14, High Byte first
        content.append(struct.pack('>H', 14))
        # IP
        ip = [int(i) for i in self.own_ip.split('.')]
        content += [chr(i) for i in ip]
        # Port
        content.append(struct.pack('<H', 0x1936))
        # Firmware Version
        content.append(struct.pack('>H', 200))
        # Net and subnet of this node
        net = 0
        subnet = 0
        content.append(chr(net))
        content.append(chr(subnet))
        # OEM Code (E:Cue 1x DMX Out)
        content.append(struct.pack('>H', 0x0360))
        # UBEA Version -> Nope -> 0
        content.append(chr(0))
        # Status1
        content.append(struct.pack('>H', 0b11010000))
        # Manufacture ESTA Code
        content.append('LL')
        # Short Name
        content.append('luminosus-server2\x00')
        # Long Name
        content.append('luminosus-server2_ArtNet_Node' + '_' * 34 + '\x00')
        # stitch together
        content = ''.join(content)
        #print self.lang['send_ArtPollReply']
        self.s.sendto(content, ("<broadcast>", 6454))
    
    def handle_ArtPollReply(self, data, addr):
        if addr[0] != self.own_ip and addr not in self.nodes:
            self.nodes.append(addr)
    
    def handle_ip_check(self, data, addr):
        if data[12:] == str("luminosus_ip_check_%s" % self.ip_check_id):
            self.own_ip = addr[0]
            print "IP of this ArtNet Node: %s" % self.own_ip
            for addr in self.nodes[:]:
                if addr[0] == self.own_ip:
                    self.nodes.remove(addr)
                

    def set_sending_method(self, method):
        if method in ('broadcast', 'unicast'):
            self.sending_method = method
            return True
        else:
            return False

    def send_dmx_data(self, dmxdata):
        if self.sending_method == 'broadcast':
            self.ArtDMX_broadcast(dmxdata)
        else:
            self.ArtDMX_unicast(dmxdata)

    def ArtDMX_unicast(self, dmxdata):
        content = [self.header]
        # Length of DMX Data, High Byte First
        content.append(struct.pack('>H', len(dmxdata)))
        # DMX Data
        content += [chr(i) for i in dmxdata]
        # stitch together
        content = "".join(content)
        # send
        for addr in self.nodes:
            self.s.sendto(content, addr)

    def ArtDMX_broadcast(self, dmxdata):
        content = [self.header]
        # Length of DMX Data, High Byte First
        content.append(struct.pack('>H', len(dmxdata)))
        # DMX Data
        content += [chr(i) for i in dmxdata]
        # stitch together
        content = "".join(content)
        # send
        self.s.sendto(content, ('<broadcast>', 6454))

    def add_artnet_node(self, node_ip):
        if node_ip not in self.nodes:
            self.nodes.append((node_ip, 6454))
            return True
        else:
            return False

    def refresh_nodes(self):
        self.ArtPoll()
        return True
    
    def get_nodes(self):
        return self.nodes

    def set_address(self, address):
        universe, subnet, net = address
        if 0 <= universe <= 15 and 0 <= net <= 127 and 0 <= subnet <= 15:
            self.address = address
        self.build_header()
        return True

    def kill_server(self):
        content = []
        # id8, 7byte + 0x00
        content.append("Art-Net\x00")
        # OpCode ArtDMX -> 0x5000, Low Byte first
        content.append(struct.pack('<H', 0x9999))
        # Protocol Version 14, High Byte first
        content.append(struct.pack('>H', 14))
        # luminosus ip check
        content.append("luminosus_kill_signal_%s" % self.ip_check_id)
        content = ''.join(content)
        self.s.sendto(content, ('<broadcast>', 6454))

    def close(self):
        self.s.close()
        print "ArtNet node stopped."

if __name__ == "__main__":
    Test().run()