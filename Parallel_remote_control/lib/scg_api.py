import requests
import json
import sys
from log import log
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class scg_api(object):
	def __init__(self, ip, port, username, pwd, prefix="/api/public", api_ver=''):
		self.ip = ip
		self.port = port
		self.uname = username
		self.pwd = pwd
		self.prefixs = prefix

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

	def POST(self, resource, payload, condition='', dump=True):
                if condition:
                        url =self.baseurl + resource + '?' + condition
                else:
                        url =self.baseurl + resource
                if dump:
                    data = json.dumps(payload)
                else:
                    data = payload	
#                print "Post url: \n", url
#                print "Post payload: \n", data
		res = requests.post(url, headers=self.headers, verify=False, cookies=self.saved_cookies, data=data)
		#res = requests.post(url, headers=self.headers, verify=False, cookies=self.saved_cookies, data=json.dumps(payload))
		#print res.status_code
		if '"success":true' in res.text or res.status_code==201 or res.status_code==200:
			return res.text
                else:
                        print "error occurs: \n", res.text

        def PATCH(self, resource, payload, condition='', dump=True):
                if condition:
                        url =self.baseurl + resource + '?' + condition
                else:
                        url =self.baseurl + resource
                if dump:
                    data = json.dumps(payload)
                else:
                    data = payload
 #               print "Patch url: \n", url
 #               print "Patch payload: \n", data
                res = requests.patch(url, headers=self.headers, verify=False, cookies=self.saved_cookies, data=data)
                return res.text

	def DELETE(self, resource, payload='', condition=''):
                if condition:
                        url =self.baseurl + resource + '?' + condition
                else:
                        url =self.baseurl + resource

                #print self.saved_cookies
                res = requests.delete(url, headers=self.headers, verify=False, cookies=self.saved_cookies, data=json.dumps(payload))
                return res


	def PLogin(self):
		url =self.baseurl + 'session'
		payload = {"username" : self.uname, "password" : self.pwd}
		#payload = {"username" : "admin", "password" : "admin#123"}
		res = requests.post(url, headers=self.headers, data=json.dumps(payload), verify=False)
		#print res
		if 'controllerVersion' in res.text:
			self.saved_cookies=requests.utils.dict_from_cookiejar(res.cookies)
			return res.text
		else:
			sys.exit()		
        def PLogoff(self):
                url = self.baseurl+'session'
                res = request.delete(url)              

	def GetZoneList(self,did='8b2081d5-9662-40d9-a3db-2a3cf4dde3f7'):
		res =self.GET('rkszones',condition=('domainId=%s&listSize=10000' % did))

		raw_data =json.loads(res.text)		
                raw_data['list'].sort(key=lambda d:d['name'])
		return raw_data['list']

        def GetAPrulesList(self,did='8b2081d5-9662-40d9-a3db-2a3cf4dde3f7'):
                res =self.GET('apRules',condition=('domainId=%s&listSize=10000' % did))

                raw_data =json.loads(res.text)
                raw_data['list'].sort(key=lambda d:d['priority'])
                return raw_data['list']

        def GetWlanList(self,zdata):
                res =self.GET(('rkszones/%s/wlans' % zdata['id']),condition='listSize=10000')

		raw_data =json.loads(res.text)
		raw_data['list'].sort(key=lambda d:d['name'])
                
                wlan_list = []
                for wlan in raw_data['list']:
                    res =self.GET(('rkszones/%s/wlans/%s' % (zdata['id'], wlan['id'])),condition='listSize=10000')
                    wlan_raw_data =json.loads(res.text)
                    #wlan_raw_data['list'].sort(key=lambda d:d['name'])
                    wlan_list.append({"wlan_ssid": wlan_raw_data['ssid'], "auth_type": wlan_raw_data['type']})
#                print raw_data
                return wlan_list

        def GetWlanGroupList(self,zid):
                res =self.GET(('rkszones/%s/wlangroups' % zid),condition='domainId=%s&listSize=10000')

                raw_data =json.loads(res.text)
                raw_data['list'].sort(key=lambda d:d['name'])
                return raw_data['list']

        def GetAPList(self,sort='id',did='8b2081d5-9662-40d9-a3db-2a3cf4dde3f7',zid=''):
		if len(zid) > 0:
			res =self.GET('aps',condition=('zoneId=%s&listSize=10000' % zid))
		else:
			res =self.GET('aps',condition=('domainId=%s&listSize=30000' % did))

                raw_data =json.loads(res.text)

		if sort == 'mac':
	                raw_data['list'].sort(key=lambda d:d['mac'])
		elif sort == 'name':
			raw_data['list'].sort(key=lambda d:d['name'])
		else:
			raw_data['list'].sort(key=lambda d:d['mac'])

                return raw_data['list']


class scgCluster(object):
    def __init__(self,api_session):
        self.api_session=api_session
        self.zoneIdList=[]
        self.apIdList=[]
        self.wlanIdList=[]
        self.apstats=[]

    def get_wlan_list(self):
        zlists =self.api_session.GetZoneList()
        wlan_list = {}
        for zdata in zlists:
            if zdata['name'] != "Staging Zone":
                wlists = self.api_session.GetWlanList(zdata)
                wlan_list[zdata['name']] = wlists
        return wlan_list

