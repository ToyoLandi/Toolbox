# Create Registry Secret to Pull Images from "registry.aquasec.com"
oc create secret docker-registry aqua-registry --docker-server=registry.aquasec.com --docker-username=collin.spears@aquasec.com --docker-password=0dinNfri3nds! --docker-email=collin.spears@aquasec.com> -n aqua

# Apply modified Enforcer Manifest using the below commands, in order.
oc apply -f "C:\Users\Collin Spears\Documents\_openshift\manifest\custom\aqua-enforcer-netshoot\aqua_sa.yaml"

#TEMP SCC POLICY FOR OPENSHIFT
oc adm policy add-scc-to-user anyuid -z aqua-sa -n aqua --as=system:admin

# Deploy Aqua Enforcer 
oc apply -f "C:\Users\Collin Spears\Documents\_openshift\manifest\custom\aqua-enforcer-netshoot\003_aqua_enforcer_secrets.yaml"
oc apply -f "C:\Users\Collin Spears\Documents\_openshift\manifest\custom\aqua-enforcer-netshoot\002_aqua_enforcer_configMap.yaml"
oc apply -f "C:\Users\Collin Spears\Documents\_openshift\manifest\custom\aqua-enforcer-netshoot\004_aqua_enforcer_daemonset.yaml"