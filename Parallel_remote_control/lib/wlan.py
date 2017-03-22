import requests
import json
import sys
requests.packages.urllib3.disable_warnings()

class wlan_api(object):
	def __init__(self, ip, port, username, pwd, prefixs="/api/public", api_ver='', wlan_id):
		self.ip = ip
		self.port = port
		self.uname = username
		self.pwd = pwd
		self.prefixs = prefixs
                self.wlan_id = wlan_id

		if len(api_ver) > 0:
			self.api_ver = api_ver
		else:
			self.api_ver = 'v5_0'

		self.headers = {'Content-Type': 'application/json'}
		self.baseurl = 'https://%s:%s%s/%s/' % (self.ip, self.port, self.prefixs, self.api_ver)

	def GET(self, resource, condition=''):
		if condition:
			url =self.baseurl + resource + '?' + condition
		else:
			url =self.baseurl + resource
		#print self.saved_cookies
		res = requests.get(url, headers=self.headers, verify=False, cookies=self.saved_cookies)
		return res

#        def GetWlanList(self, zid):
#                res =self.GET(('rkszones/%s/wlans/%s' % zid, self.wlan_id),condition='listSize=10000')
#
#		raw_data =json.loads(res.text)
#                return raw_data 
