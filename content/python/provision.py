#!/usr/bin/env python

import apiman
import keycloak
import sys
import json
import os

#Define constants 

# baseUrl is used for provisioning Apiman/Keycloak via REST calls. Both 
# Apiman and the Python REST client run within Docker during the Docker build, 
# so using http://localhost:8080 is the most stable solution
baseUrl = os.getenv('BASE_URL','http://localhost:8080')

# Should be factored out as soon as https://issues.jboss.org/browse/APIMAN-831 is resolved
external_url = os.getenv('EXTERNAL_URL', 'https://apiman.openonderwijsapi.nl:7443')

realm = 'apiman'
secret = 'password'

#Base dir for reading files from the same directory as this script
curDir = os.path.dirname(os.path.abspath(__file__))

keycloak = keycloak.Keycloak(baseUrl, realm, secret, 'admin', 'admin123!')
keycloak.getRealm().resetPassword('admin',os.environ['ADMIN_PASSWORD'])
token = keycloak.accessToken

admin = apiman.ApiMan(baseUrl, realm, token)

#Install additional plugins
version = admin.getVersion()
admin.installPlugin('io.apiman.plugins', 'apiman-plugins-keycloak-oauth-policy', version)
admin.installPlugin('io.apiman.plugins', 'apiman-plugins-simple-header-policy', version)

#Get the certificate from the Apiman realm in Keycloak.
certificate = keycloak.getRealm().getCertificate()

#Create new organization and assign users to it
org = apiman.Organization(admin, 'SURFnet','SURFnet')

inhollandtest = org.createService('InHollandTest','In Holland - Test - Open Onderwijs Api Service', '1.0')
inhollandtest.configureEndpoint('rest','https://inhollandtest.azure-api.net/',True)
inhollandtest.enableBasicAuthentication('demo','d3m0')
inhollandtest.setSwaggerJsonDefinition(curDir+'/swagger/inhollandtest.json')
inhollandtest.addPolicy('keycloak-oauth-policy', { 
    'realm' : external_url + '/auth/realms/apiman', 
    'realmCertificateString' : certificate,
    'stripTokens' : True,
    'delegateKerberosTicket' : False,
    'forwardRoles' : { 'active' : False },
    'forwardAuthInfo' : [{
        'field' : 'username', 
        'headers' : 'userid'}]})
#Subscription key for connecting to the Azure Unlimited Subscription
inhollandtest.addPolicy('simple-header-policy', {
    'addHeaders': [{ 
        'applyTo' : 'Request', 
        'headerName' : 'Ocp-Apim-Subscription-Key', 
        'headerValue' : 'f797be1840d144b9a9851a9f3cfea591', 
        'valueType' : 'String'}]})

inhollandtest.publish()

inhollandtestNoAuth = org.createService('InHollandTestNoAuth','In Holland - Test without authentication - Open Onderwijs Api Service', '1.0')
inhollandtestNoAuth.configureEndpoint('rest','https://inhollandtest.azure-api.net/',True)
inhollandtestNoAuth.setSwaggerJsonDefinition(curDir+'/swagger/inhollandtestnoauth.json')
#Subscription key for connecting to the Azure Starter Subscription
inhollandtestNoAuth.addPolicy('keycloak-oauth-policy', { 
    'realm' : external_url + '/auth/realms/apiman', 
    'realmCertificateString' : certificate, 
    'stripTokens' : True,
    'delegateKerberosTicket' : False,
    'forwardRoles' : { 'active' : False },
    'forwardAuthInfo' : [{
        'field' : 'username', 
        'headers' : 'userid'}]})
inhollandtestNoAuth.addPolicy('simple-header-policy', {
    'addHeaders': [{ 
        'applyTo' : 'Request', 
        'headerName' : 'Ocp-Apim-Subscription-Key', 
        'headerValue' : '97dcf5d9e8a444a4a421fb5856a6c49a', 
        'valueType' : 'String'}]})
inhollandtestNoAuth.publish()

#Create SAML Identity Broker
keycloak.getIdentityProvider().createSamlIdentityProvider('SURFconext', False, 'https://engine.connect.surfconext.nl/authentication/idp/single-sign-on','urn:oasis:names:tc:SAML:2.0:nameid-format:persistent')

#Map SAML Attributes onto Keycloak Attributes
mapper = keycloak.getIdentityProviderMapper('SURFconext')
mapper.createSamlAttributeImporterMapper('mail', 'urn:mace:dir:attribute-def:mail', None, 'mail')
mapper.createSamlAttributeImporterMapper('eduPersonPrincipalName', 'urn:mace:dir:attribute-def:eduPersonPrincipalName', None, 'eduPersonPrincipalName')
mapper.createSamlAttributeImporterMapper('uid', 'urn:oid:0.9.2342.19200300.100.1.1', None, 'uid')
mapper.createSamlAttributeImporterMapper('displayName', 'urn:mace:dir:attribute-def:displayName', None, 'displayName')


#Create a public client in the Apiman realm for the js-console
keycloak.getClient().createPublicClient('js-console',['/js-console/*'])

#Expose the Keycloak attributes originating from Surfconext into the tokens of the js-console client
protoMapper = keycloak.getClientProtocolMapper('js-console')
protoMapper.createOpenIdConnectUserAttributeMapper('uid to username','uid', 'username')
protoMapper.createOpenIdConnectUserAttributeMapper('IdP mail to email','mail', 'email')
protoMapper.createOpenIdConnectUserAttributeMapper('eduPersonPrincipalName to preferred_username','eduPersonPrincipalName', 'preferred_username')