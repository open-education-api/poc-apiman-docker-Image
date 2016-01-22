# SURFnet - Open Onderwijs API - Docker image
This project builds a Docker image containing a provisioned and runnning installation of [JBoss Apiman](http://www.apiman.io/) and [JBoss Keycloak](http://keycloak.jboss.org/). Apiman en Keycloak are configured to delegate authentication to SURconext and expose the available API's of In Holland.

## Prerequisite - Install Docker
[https://docs.docker.com/installation/](https://docs.docker.com/installation/)


## Usage
To run the docker container in interactive mode with HTTP (8080), HTTPS (8443) and management HTTP (9990) enabled on the environment https://apiman.openonderwijsapi.nl at port 7443:  

`docker run -ti -p 8080:8080 -p 8443:8443 -p 9990:9990 surfnet/ooapi-apiman -Drealm_base_url=https://apiman.openonderwijsapi.nl:7443`

To run the docker container as a deamon with only HTTPS (8443) enabled on the environment https://apiman.openonderwijsapi.nl at port 7443:

`docker run -d -p 8443:8443 surfnet/ooapi-apiman -Drealm_base_url=https://apiman.openonderwijsapi.nl:7443`

The base url of the realm protecting the API must be supplied using the **realm_base_url** system property. A correctly configured realm base url is required to prevent verification issues with the OAuth token.

The docker images comes preloaded with an unsigned SSL certificate.

The master realm of JBoss Keycloak is configured with the default user **admin** and password **admin123!**  

Use https://<host>:8443/auth/admin/ to login to the JBoss Keycloak admin console and change the default password!

The apiman realm of JBoss Keycloak is configured with the default user **admin** and the password that you supplied during the build using the [admin-password] parameter or defaults to **admin123!**. 
 
Use https://<host>:8443/apimanui/ to login to JBoss Apiman.

Use https://<host>:8443/js-console/ to open the demo application. See the *SURFnet - Open Onderwijs API - Demo application* project  for further details.

Use https://<host>:8443/spssodescriptor/realms/{realm}/identity-provider/{identity-provider} to retrieve the SAML SP SSO Descriptor of an identity provider within a realm. See the *SAML - Service Provider SSO Descriptor Proxy*  project for further details.

### Replace the preloaded keystore 
Create a keystore with ***secret*** as the keystore / private key passowrd and an alias ***apimancert***

Start the docker container as follows assuming your keystore is located in /my-keystore.jks:
`docker run -d -p 8443:8443 -v /my-keystore.jks:/opt/jboss/wildfly/standalone/configuration/apiman.jks surfnet/ooapi-apiman -Dexternal_url=https://apiman.openonderwijsapi.nl:7443`


## Limitations
* The keystore password and private key password are hardcoded set at ***secret***. We should use environment properties in the future so we can submit them when starting up the docker container.

## Build Image
There is no need to build the Docker image yourself, because it is automatically build by Docker Hub.
But you can offcourse extend from this image or build it yourself using the build script.
