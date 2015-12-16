# SURFnet - Open Onderwijs API - Docker image
This project builds a Docker image containing a provisioned and runnning installation of [JBoss Apiman](http://www.apiman.io/) and [JBoss Keycloak](http://keycloak.jboss.org/). Apiman en Keycloak are configured to delegate authentication to SURconext and expose the available API's of In Holland.

## Prerequisite - Install Docker
[https://docs.docker.com/installation/](https://docs.docker.com/installation/)

## Build Image
The Docker image must be build before you can use it:  
`./build.sh <admin-password> <external-base-url>`

For example:
`./build.sh admin123! https://apiman.openonderwijsapi.nl:7443`

## Usage
Use the Docker Scripts from the **SURFnet - Open Onderwijs API - Docker scripts** project or use the docker commands directly. 

For example.

To run the docker container in interactive mode with HTTP (8080), HTTPS (8443) and management HTTP (9990) enabled:  

`docker run -ti -p 8080:8080 -p 8443:8443 -p 9990:9990 docker-registry.finalist.nl:5000/surfnet/ooapi-poc:1.0`

To run the docker container as a deamon with only HTTPS (8443) enabled:

`docker run -d -p 8443:8443 docker-registry.finalist.nl:5000/surfnet/ooapi-poc:1.0`

The docker images comes preloaded with an unsigned SSL certificate.

The master realm of JBoss Keycloak is configured with the default user **admin** and password **admin123!**  

Use https://<host>:8443/auth/admin/ to login to the JBoss Keycloak admin console and change the default password!

The apiman realm of JBoss Keycloak is configured with the default user **admin** and the password that you supplied during using the <admin-password> parameter.  
 
Use https://<host>:8443/apimanui/ to login to JBoss Apiman.

Use https://<host>:8443/js-console/ to open the demo application. See the *SURFnet - Open Onderwijs API - Demo application* project  for further details.

Use https://<host>:8443/spssodescriptor/realms/{realm}/identity-provider/{identity-provider} to retrieve the SAML SP SSO Descriptor of an identity provider within a realm. See the *SAML - Service Provider SSO Descriptor Proxy*  project for further details.

### Replace the preloaded keystore 
Create a keystore with ***secret*** as the keystore / private key passowrd.

Start the docker container as follows assuming your keystore is located in /my-keystore.jks:
`docker run -d -p 8443:8443 -v /my-keystore.jks:/opt/jboss/wildfly/standalone/configuration/apiman.jks docker-registry.finalist.nl:5000/surfnet/ooapi-poc:1.0`


## Limitations
* The Docker build should be environment agnostic. Currently this not possible when services are added that depend on environment specific settings. Due to limitation in JBoss Apiman v1.1.9.Final this cannot be resolved at runtime using property placeholders. As of JBoss Apiman v1.2.0.Final property placeholders will be supported enabling the runtime configuration of services. This is addressed in [APIMAN-831](https://issues.jboss.org/browse/APIMAN-831) and [APIMAN-832](https://issues.jboss.org/browse/APIMAN-832).
* The keystore password and private key password are hardcoded set at ***secret***. We should use environment properties in the future so we can submit them when starting up the docker container.