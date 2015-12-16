FROM jboss/apiman-wildfly:1.1.9.Final

MAINTAINER Ton Swieb <ton@finalist.nl>

#Install required python packages, the Pythion installation manager and install required python dependencies
USER root
RUN yum -y install python epel-release 
RUN yum -y install python-pip && yum clean all 
RUN pip install requests
USER jboss

#Set the local URL to use for accessing JBoss Apiman via REST DSL for provisioning
ENV BASE_URL http://127.0.0.1:8080

# Set the external URL to use for accessing Jboss Apiman/Keycloak
# TODO: As soon as JBoss Apiman supports it, this should be move to the runtime
# This breaks the Docker philosophy of having an environment agnostic image
# See: https://issues.jboss.org/browse/APIMAN-831
ARG EXTERNAL_URL

# TODO: Find a way to remove this from the Docker build and move it to the runtime
ARG ADMIN_PASSWORD 

#Copy the content required for provisioning
COPY content /opt/jboss/provision/

#Execute the provision script
RUN /opt/jboss/provision/provision.sh

# Enable the management console for development purposes.
# Disable in production by commenting the line below!
CMD ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0", "-c", "standalone-apiman.xml","-bmanagement","0.0.0.0"]
