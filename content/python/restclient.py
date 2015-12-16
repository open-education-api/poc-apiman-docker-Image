import sys
import requests
import base64
import json
import time
import pprint

class RestClient(object):
    "Base class for executing REST calls on endpoints secured by OAuth2 and handling JSON (error) response"

    def __init__(self, baseUrl, realm, accessToken):
        self.baseUrl = baseUrl
        self.accessToken = accessToken
        self.encoder = json.JSONEncoder()

    def post(self, url, payload, onSuccess = None):
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.accessToken}
        r = requests.post(self.baseUrl + url, headers=headers, data=self.encoder.encode(payload), timeout=30)
        return handleResponse(r,onSuccess)

    def putFileContent(self, url, file, onSuccess = None):
        """Upload the content of a file. Assuming a Content-Type of application/json."""
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.accessToken}
        r = requests.put(self.baseUrl + url, headers=headers, data=open(file).read(), timeout=30)
        return handleResponse(r,onSuccess)

    def put(self, url, payload, onSuccess = None):
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.accessToken}
        r = requests.put(self.baseUrl + url, headers=headers, data=self.encoder.encode(payload), timeout=30)
        return handleResponse(r,onSuccess)
        
    #By default: On a succesfull response a JSON response is expected which is automatically converted to a dictionary
    def get(self, url, payload = None, onSuccess = lambda x : x.json()):
        r = requests.get(self.baseUrl + url, headers={'Authorization': 'Bearer ' + self.accessToken}, timeout=30)
        return handleResponse(r,onSuccess)
            
def handleResponse(r, onSuccess = None):
	print 'Executed: {} {}'.format(r.status_code,r.url)
	if (r.status_code >= 400):
		try:
			json = r.json()
			errorType = json['type'] if 'type' in json else None
			errorCode = json['errorCode'] if 'errorCode' in json else None
			errorMessage = json['message'] if 'message' in json else None
			print 'statusCode: {}\ntype: {}\nerrorCode: {}\nmessage: {}'.format(r.status_code,errorType,errorCode,errorMessage)
		except:
			print r.text
	elif onSuccess is not None:
		return onSuccess(r)
