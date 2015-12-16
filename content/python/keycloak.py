import sys
import requests
import base64
import json
import time
import pprint
import restclient

class Keycloak(object):
    "Base class for executing REST calls on Keycloak and handling JSON (error) response"

    def __init__(self, baseUrl, realm, secret, userName, password):
        self.baseUrl = baseUrl
        self.realm = realm
        self.secret = secret
        self.accessToken = self.__getAccessToken(userName,password)
    	self.client = restclient.RestClient(baseUrl, realm, self.accessToken)
        self.encoder = json.JSONEncoder()

    def __getAccessToken(self, userName, password):
        "Get access token from Keycloak"
        authUrl = '{}/auth/realms/{}/protocol/openid-connect/token'.format(self.baseUrl,self.realm)
        authorization = 'Basic ' + base64.b64encode(self.realm + ':' + self.secret)
        headers = {'Authorization': authorization}
        payload = {'username': userName, 'password': password ,'grant_type':'password'}
        r = requests.post(authUrl,data=payload, headers=headers)
        return restclient.handleResponse(r,lambda x: x.json()['access_token'])
            
    def getRealm(self):
        return Realm(self)
        
    def getClient(self):
    	return Client(self)
        
    def getIdentityProvider(self):
        return IdentityProvider(self)

    def getIdentityProviderMapper(self, providerId):
        return IdentityProviderMapper(self, providerId)
        
    def getClientProtocolMapper(self, clientId):
    	return ClientProtocolMapper(self, clientId)
        
class Realm(object):
    "A Keycloak realm"

    def __init__(self, keycloak):
        self.keycloak = keycloak
        self.client = keycloak.client
        self.realmUrl = '/auth/admin/realms/' + keycloak.realm
        
    def createUser(self, userName, password,firstName, lastName, email):
        payload = {'username': userName, 'firstName' : firstName, 'lastName' : lastName, 'email' : email, 'enabled' : True, 'emailVerified' : True}
        self.client.post(self.realmUrl + '/users', payload)
        self.resetPassword(userName,password)
        
    def resetPassword(self, userName, password):
        payload = {'type' : 'password', 'value' : password, 'temporary' : False  }
        self.client.put(self.realmUrl + '/users/' + userName + '/reset-password', payload)
    
    def setAccessToken(self, accessTokenLifespan):
    	payload = {'accessTokenLifespan' : accessTokenLifespan}
    	self.client.put(self.realmUrl,payload)
    
    def getUser(self, userName):
        return self.client.get(self.realmUrl + '/users/' + userName)

    def getCertificate(self):
        return self.client.get(self.realmUrl, onSuccess = lambda x: x.json()['certificate'])

class IdentityProvider(object):
    """A Keycloak Identity Provider"""
    
    def __init__(self, keycloak):
        self.keycloak = keycloak
        self.client = keycloak.client
        self.url = '/auth/admin/realms/{}/identity-provider/instances'.format(keycloak.realm)
        
    def getAll(self):
        return self.client.get(self.url)
        
    def get(self, alias):
        return self.client.get(self.url + '/' + alias)
        
    def export(self, alias):
    	return self.client.get('{}/{}/export'.format(self.url,alias),onSuccess = lambda x : x.text)

    def create(self, alias, providerId, updateProfileFirstLogin, config):
        """Create an Identity Provider. The configuration is provider dependend."""
        payload = { 'alias' : alias, 'providerId' : providerId, 'updateProfileFirstLogin': updateProfileFirstLogin, 'config' : config }
        self.client.post(self.url, payload)
        
    def createSamlIdentityProvider(self, alias, updateProfileFirstLogin, singleSignOnServiceUrl, nameIDPolicyFormat):
        """Create a SAML 2.0 Identity Provider."""        
        config = {'singleSignOnServiceUrl' : singleSignOnServiceUrl, 'nameIDPolicyFormat' : nameIDPolicyFormat }
        self.create(alias,'saml', updateProfileFirstLogin, config)        
    
class IdentityProviderMapper(object):
    """A Keycloak Identity Provider Mapper"""

    def __init__(self, keycloak, providerId):
        self.keycloak = keycloak
        self.client = keycloak.client
        self.providerId = providerId
        self.url = '/auth/admin/realms/{}/identity-provider/instances/{}/mappers'.format(keycloak.realm, providerId)

    def getAll(self):
        return self.client.get(self.url)
        
    def get(self, mapperId):
        return self.client.get(self.url + '/' + mapperId)

    def create(self, name, identityProviderMapper, config):
    	""" Add an identity provider mapper.
    	
    	name : A human readable name identifying this mapper
    	identityProviderMapper:	The type of mapper.
    	config: The configuration of this mapper. The configuration to supply depends on the choosen identityProviderMapper.
    	"""
        payload = { 'name' : name, 'identityProviderAlias' : self.providerId ,'identityProviderMapper' : identityProviderMapper, 'config' : config }
        self.client.post(self.url, payload)

    def createSamlAttributeImporterMapper(self, name, attributeName, friendlyName, userAttributeName):
    	""" Add an identity provider mapper of the mapper type SAML Attribute Importer.
    	
    	name: A human readable name identifying this mapper
    	attributeName: The name of the SAML attribute we want to map to Keycloak
    	friendlyName: The friendly name of the SAML attribute we want to map to Keycloak
    	userAttributeName: The name of the Keycloak attribute we want to map to from SAML
    	"""
        config = {'attribute.name' : attributeName, 'attribute.friendly.name' : friendlyName, 'user.attribute' : userAttributeName }
        self.create(name,'saml-user-attribute-idp-mapper', config)

class Client(object):

    def __init__(self, keycloak):
        self.keycloak = keycloak
        self.client = keycloak.client
        self.url = '/auth/admin/realms/{}/clients'.format(keycloak.realm)

    def getAll(self):
        return self.client.get(self.url)

    def get(self, clientId):
        return self.client.get(self.url + '/' + clientId)
        
    def createPublicClient(self, clientId, redirectUris):
        payload = {'clientId': clientId, 'enabled' : True, 'publicClient' : True, 'enabled' : True, 'redirectUris' : redirectUris}
        self.client.post(self.url, payload)

class ClientProtocolMapper(object):

    def __init__(self, keycloak, clientId):
        self.keycloak = keycloak
        self.client = keycloak.client
        self.clientId = clientId
        self.url = '/auth/admin/realms/{}/clients/{}/protocol-mappers/models'.format(keycloak.realm, clientId)

    def getAll(self):
        return self.client.get(self.url)
        
    def get(self, mapperId):
        return self.client.get(self.url + '/' + mapperId)

    def create(self, name, protocol, protocolMapper, consentRequired, consentText, config):
    	""" Add a protocol mapper for a client.
    	
    	name : A human readable name identifying this mapper
    	protocol: The authentiction protocol
    	protocolMapper:	The type of mapper.
		consentRequired : Must the user give consent for supplying this data to the client
		consentText : The text to display identifying this mapping when asking for user consent	
    	config: The configuration of this mapper. The configuration to supply depends on the choosen protocolMapper.
    	"""
        payload = { 'name' : name, 'protocol' : protocol , 'protocolMapper' : protocolMapper, 'consentRequired' : consentRequired, 'consentText' : consentText, 'config' : config }
        self.client.post(self.url, payload)

    def createOpenIdConnectUserAttributeMapper(self, name, userAttributeName, claimName, claimType='String', showInAccessToken=True, showInIdToken=True):
    	""" Add an openid-connect mapper to the Client.
    	
    	Maps an attribute from the User model to the User claim.
    	name: A human readable name identifying this mapper
    	claimName: The name to use in the claim.
    	claimType: The data type of the claim: String, long, int, boolean
    	showInAccessToken: Add the claim to the Access Token
    	showInIdToken: Add the claim to the ID Token
    	userAttributeName: The name of the attribute from the User model we want to map into the claim
    	"""
        config = {'claim.name' : claimName, 'Claim JSON Type' : claimType, 'access.token.claim' : showInAccessToken, 'id.token.claim' : showInIdToken, 'user.attribute' : userAttributeName }
        self.create(name,'openid-connect','oidc-usermodel-attribute-mapper',False, None, config)