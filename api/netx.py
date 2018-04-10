#!/usr/bin/env python3
import sys
import os
import socket, struct
import utils.auto_json as mkjson
import utils.auto_logger as l
import global_vars as gv

"""
Netx module provided by Mark Trout (python code ported from perl)
This code has been changed to :
	- contained as a class
	- 
"""


class Netx(object):


	"""
	 Modules for custom item routines for retail address space.
	 Includes supporting IPv4 Modules
	"""
	def __init__(self):
		offset=0x100
		self.offset={}
		self.offset['a'] = 0x000
		self.offset['b'] = self.offset['a'] + offset
		self.offset['c'] = self.offset['b'] + offset
		self.offset['d'] = self.offset['c'] + offset
		self.offset['e'] = 0x000
		self.offset['f'] = self.offset['e'] + offset
		self.offset['g'] = self.offset['f'] + offset
		self.offset['h'] = self.offset['g'] + offset
		self.valid_subnet_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
		self.item={}

	@classmethod
	def get_addr(self, host):
		try:
			res = socket.gethostbyname(host)
			return res
		except:
			from utils.auto_config import dryrun_netx_fake_ip, dryrun
			if dryrun :
				return dryrun_netx_fake_ip
			l.logger.error("Cannot reach store/device : {}".format(host))
			gv.fake_assert()

	@classmethod
	def get_name(self, addr):
		l.logger.debug(addr)
		return socket.gethostbyaddr(addr)[0]

	@classmethod
	def dotted_quad_to_num(self, ip):
		"convert decimal dotted quad string to long integer"
		return struct.unpack('!L',socket.inet_aton(ip))[0]

	@classmethod
	def num_to_dotted_quad(self, n):
		"convert long int to dotted quad string"
		return socket.inet_ntoa(struct.pack('!L',n))

	@classmethod
	def make_mask(self, n):
		"return a mask of n bits as a long integer"
		n = 32 - n
		return (2<<n-1)-1

	@classmethod
	def ip_to_net_and_host(self, ip, maskbits):
		"returns tuple (network, host) dotted-quad addresses given IP and mask size"
		# (by Greg Jorgensen)
		n = self.dotted_quad_to_num(ip)
		m = self.make_mask(maskbits)
		host = n & m
		net = n - host
		return self.num_to_dotted_quad(net)

	def get_three_octets(self, slot):
		if slot in ['a','b','c','d']:
			aux = self.item['upper']
		else:
			aux = self.item['lower']

		str = self.num_to_dotted_quad(self.dotted_quad_to_num(aux) + self.offset[slot])
		octets = str.split(".")
		str = "{}.{}.{}".format(octets[0], octets[1], octets[2])
		return str

	def make_netx(self, ip):
		"returns tuple(Upper,Lower,NetA,NetB,..NetH) for ip in 10.128.0.0/9"
		self.item = {}

		# test if address in upper or lower block
		base = self.ip_to_net_and_host(ip, 10)

		if str(base) < '10.192' :
			ipVal = self.dotted_quad_to_num(ip)
			ipVal += 0x400000
			ipNew = self.num_to_dotted_quad(ipVal)
			ip = ipNew

		base = self.ip_to_net_and_host(ip, 22)

		self.item['upper'] = base
		self.item['lower'] = self.num_to_dotted_quad(self.dotted_quad_to_num(self.item['upper']) - 0x400000)

		for slot in self.valid_subnet_list:
			self.item[slot] = self.get_three_octets(slot)

		return self.item

	def get_all(self, _netx=None, _name=None, _addr=None):
		if (_name is None and _addr is None):
			l.logger.error("name and addr are empty")
			return False
		if _name:
			addr = self.get_addr(_name)
			name = _name
		else:
			addr = _addr
			name = None   #FIXME self.get_name(addr)
		l.logger.debug(name)
		l.logger.debug(addr)

		# Now build the ranges/etc
		netX = self.make_netx(addr)

		pickNet = None
		if _netx :
			str = "CC = %s.5" % netX[_netx]
			l.logger.debug(str)
			pickNet = "CC = %s.5" % netX[_netx]

		l.logger.debug("item created.")
		return netX, pickNet


def _get(netx=None, name=None, addr=None):
	obj = Netx()
	obj.get_all(_netx, name, addr)


def get(name):
	obj = Netx()
	netx, picknet = obj.get_all(None, name, None)
	return netx, picknet


if __name__ == '__main__':
	cwd = os.getcwd()
	_netx = None
	_name = None
	_addr = None
	netx, picknet = get("mx9845a")
	str = mkjson.make_pretty((netx))
	l.logger.debug(str)
	#netXPicks = _get(item=None, name=None, addr="151.101.193.67")
