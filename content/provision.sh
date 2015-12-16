#!/bin/bash -x

#Faill fast in case of error
set -e

JBOSS_CLI=$JBOSS_HOME/bin/jboss-cli.sh

function wait_for_deployment() {
  until `$JBOSS_CLI -c "/deployment=$1:read-attribute(name=status)" &> /dev/null`; do
    sleep 5
  done
}

function start_wildfly() {

	echo "Startup Wildfly"
	#Startup WildFly in the background so it is available for API calls.
	export LAUNCH_JBOSS_IN_BACKGROUND=true
	$JBOSS_HOME/bin/standalone.sh -c standalone-apiman.xml &
}

#echo "=> Change the default keystore before we boot"
#sed -i 's|apiman.jks|apiman-openonderwijsapi-nl.jks|' /opt/wildfly/standalone/configuration/standalone-apiman.xml

#Add admin user for the management console
#Should be disabled in production!
$JBOSS_HOME/bin/add-user.sh -s -u admin -r ManagementRealm -p $ADMIN_PASSWORD

start_wildfly

#Ensure all artifacts are deployed before we continue
wait_for_deployment main-auth-server.war
wait_for_deployment apiman-gateway-api.war
wait_for_deployment apiman-es.war
wait_for_deployment apiman-ds.xml
wait_for_deployment apiman-gateway.war
wait_for_deployment apimanui.war

echo "=> Provision Apiman and Keycloak"
/opt/jboss/provision/python/provision.py

echo "=> Provisioning Wildfly and then shut it down"
echo "set BASE_URL=$BASE_URL" >> $JBOSS_HOME/bin/.jbossclirc
echo "set ADMIN_PASSWORD=$ADMIN_PASSWORD" >> $JBOSS_HOME/bin/.jbossclirc
$JBOSS_HOME/bin/jboss-cli.sh -c --file=`dirname "$0"`/commands.cli

echo "=> Shutting down WildFly."
$JBOSS_CLI -c ":shutdown"

echo "=> Need to startup Wildfly again after applying changes via CLI"
start_wildfly

#Ensure all artifacts are deployed before we continue
wait_for_deployment main-auth-server.war
wait_for_deployment apiman-gateway-api.war
wait_for_deployment apiman-es.war
wait_for_deployment apiman-ds.xml
wait_for_deployment apiman-gateway.war
wait_for_deployment apimanui.war
wait_for_deployment keycloak-saml-spssodescriptor-1.0.0-SNAPSHOT.war
wait_for_deployment js-console.war