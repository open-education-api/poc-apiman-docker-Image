import sys
import base64
import json
import time
import pprint
import restclient

class ApiMan(object):
    "Base class for executing REST calls on Apiman and handling JSON (error) response"

    def __init__(self, baseUrl, realm, accessToken):
        self.baseUrl = baseUrl
        self.realm = realm
        self.client = restclient.RestClient(baseUrl, realm, accessToken)
            
    def getCurrentUserInfo(self):
        return self.client.get('/apiman/currentuser/info')

    def createRole(self, name, description, permissions):
        payload = {'name' : name, 'description': description, 'permissions' : permissions}
        self.client.post('/apiman/roles/',payload)
        
    def updateRolePermissions(self, name, permissions):
        payload = {'permissions' : permissions}
        self.client.put('/apiman/roles/' + name, payload)
        
    def searchServices(self, searchCriteria, onSuccess = lambda x:x.json()):
        return self.client.post('/apiman/search/services',searchCriteria, onSuccess)

    def searchApplications(self, searchCriteria, onSuccess = lambda x:x.json()):
        return self.client.post('/apiman/search/applications',searchCriteria, onSuccess)

    def searchOrganizations(self, searchCriteria, onSuccess = lambda x:x.json()):
        return self.client.post('/apiman/search/organizations',searchCriteria, onSuccess)
    
    def installPlugin(self, groupId, artifactId, version ):
        payload = { 'groupId' : groupId, 'artifactId' : artifactId, 'version' : version}
        self.client.post('/apiman/plugins',payload)

    def getPlugins(self):
        return self.client.get('/apiman/plugins/')
    
    def getPlugin(self, pluginId):
        return self.client.get('/apiman/plugins/{}'.format(pluginId))
        
    def getPluginPolicyDefinitions(self, pluginId):
        return self.client.get('/apiman/plugins/{}/policyDefs/'.format(pluginId))
        
    def getPolicyDefinitionForm(self, pluginId, policyDefId):
        return self.client.get('/apiman/plugins/{}/policyDefs/{}/form/'.format(pluginId,policyDefId))
        
    def getPolicyDefinition(self, policyDefId):
        return self.client.get('/apiman/policyDefs/{}'.format(policyDefId))
    
    def getStatus(self):
        return self.client.get('/apiman/system/status')
    
    def getVersion(self):
        return self.getStatus()['version']
    
    # Print the properties belonging to a plugin policy definition form
    # The properties can be used when adding a policy to a service, plan or application
    def printPluginPolicyDefinitionFormsProperties(self):
        pp = pprint.PrettyPrinter(indent=4)
        for plugin in self.getPlugins():
            pluginId = plugin['id']
            policyDefs = self.getPluginPolicyDefinitions(pluginId)
            for policyDef in policyDefs:
                policyDefId = policyDef['id']
                pp.pprint(self.getPolicyDefinitionForm(pluginId,policyDefId))
                
    def printServicePolicyConfiguration(self, organizationId, serviceId, versionId):
        pp = pprint.PrettyPrinter(indent=4)        
        policies = self.client.get('/apiman/organizations/{}/services/{}/versions/{}/policies/'.format(organizationId,serviceId,versionId))
        for policy in policies:
            fullPolicy = self.client.get('/apiman/organizations/{}/services/{}/versions/{}/policies/{}'.format(organizationId,serviceId,versionId,policy['id']))
            pp.pprint(fullPolicy)
        
class Entity(object):
    "Base class for an apiman entity"
    
    def __init__(self,apiman, entityId, description):
        self.apiman = apiman
        self.client = apiman.client
        self.entityId = entityId
        self.description = description
        if (self.get() == None):
            self._create()
        else:
            print 'Skipping creation of existing entity {}'.format(entityId)
            
    def _create(self):
        payload = {'name': self.entityId,  'description' : self.description}
        self.client.post(self.baseUrl, payload)
            
    def get(self):
        return self.client.get(self.url)

class VersionedEntity(Entity):
    "Base class for an apiman versioned entity"

    def __init__(self, organization, entityId, description, version, urlId, publishType):
        self.organizationId = organization.entityId
        self.version = version
        self.publishType = publishType
        self.baseUrl = '/apiman/organizations/{}/{}'.format(organization.entityId,urlId)
        self.url = "{}/{}/versions/{}".format(self.baseUrl,entityId,version)
        self.policyUrl = "{}/{}/versions/{}/policies".format(self.baseUrl,entityId,version)
        super(VersionedEntity,self).__init__(organization.apiman, entityId, description)

    def _create(self):
        payload = {'name': self.entityId,  'description' : self.description, "initialVersion" : self.version}
        self.client.post(self.baseUrl, payload)

    def get(self):
        return self.client.get(self.url)

    def addPolicy(self, definitionId, configuration):
        payload = { 'definitionId' : definitionId , 'configuration' : json.JSONEncoder().encode(configuration)}
        self.client.post(self.policyUrl, payload)

    def publish(self):
        payload = { 'type' : self.publishType, 'entityId' : self.entityId, 'organizationId' : self.organizationId, 'entityVersion' : self.version}
        self.client.post('/apiman/actions/', payload)

class Organization(Entity):

    def __init__(self, apiman, name, description):
        self.baseUrl = '/apiman/organizations'
        self.url = '/apiman/organizations/' + name
        super(Organization,self).__init__(apiman,name,description)
    
    def assignUserInRoles(self,userName, roles):
        payload = {'userId': userName,  'roleIds' : roles}
        self.client.post(self.url + '/roles', payload)
        
    def createPlan(self, plan, description, version):
        return Plan(self,plan,description,version)
        
    def createService(self, service, description, version):
        return Service(self,service, description, version)
        
    def createApplication(self, application, description, version):
        return Application(self, application, description, version)

class Plan(VersionedEntity):
    def __init__(self, organization, plan, description, version):
        super(Plan,self).__init__(organization,plan,description,version,'plans','lockPlan')

class Service(VersionedEntity):

    def __init__(self, organization, serviceId, description, version):
        super(Service,self).__init__(organization,serviceId,description,version,'services','publishService')

    def configureEndpoint(self, endpointType, endpoint, publicService):
        payload = { 'endpointType' : endpointType, 'publicService' : publicService , 'endpoint' : endpoint}
        self.client.put(self.url, payload)
    
    def setSwaggerJsonDefinition(self, file):
    	definitionUrl = '{}/definition/'.format(self.url)
    	self.client.putFileContent(definitionUrl,file)
    
    def enableBasicAuthentication(self, username, password, requireSSL = True):
    	payload = { 'endpointProperties' : { 'authorization.type' : 'basic', 'basic-auth.username' : username, 'basic-auth.password' : password, 'basic-auth.requireSSL' : requireSSL}}
    	self.client.put(self.url, payload)

    def setPlans(self, plans):
        payload = { 'plans' : map(lambda x: {'planId' : x.entityId , 'version' : x.version} ,plans)}
        self.client.put(self.url, payload)
        
class Application(VersionedEntity):
    
    def __init__(self, organization, application, description, version):
        super(Application,self).__init__(organization,application,description,version,'applications','registerApplication')
        self.contractUrl = '{}/{}/versions/{}/contracts'.format(self.baseUrl,application,version)
        
    def createContract(self, service, plan):
        payload = {'serviceId' : service.entityId, 'planId' : plan.entityId, 'serviceVersion' : service.version, 'serviceOrgId' : self.organizationId}
        self.client.post(self.contractUrl, payload)