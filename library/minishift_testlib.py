from avocado.utils import process
import imp
import logging
import re
import time

log = logging.getLogger("Openshift.Debug")

def wait_for_output(cmd, timeout = 180):
    output = "FAIL"
    for i in range(timeout):
        time.sleep(1)
        try:
            output = process.system_output(cmd)
            return output
        except:
            pass
    return output

def wait_for_text_in_output(cmd, text = '', timeout = 180):
    output = "FAIL"
    for i in range(timeout):
        time.sleep(1)
        try:
            output = process.system_output(cmd)
            if text in output:
                return output
        except:
            pass
    return output

def oc_login(self, uname, password):
    strcmd = "oc login --username=" +uname +" --password=" +password +" --insecure-skip-tls-verify"
    self.log.info ("Executing : " +strcmd)
    output = wait_for_output(strcmd)
    return output

def add_new_project(self, project_name):
    strcmd = "oc new-project " +project_name 
    self.log.info ("Executing : " +strcmd)
    output = wait_for_output(strcmd)
    return output

def add_new_app(self, registry):
    strcmd = "oc new-app " +registry
    lst = registry.split("/")
    repo = lst[len(lst) - 1]
    self.log.info ("Executing : " +strcmd)
    lst = []
    output = wait_for_output(strcmd)
    if output == "FAIL":
        return output
    for lines in output.splitlines():
        if repo in lines:
            lst.append(lines)
                
    lst = lst[len(lst) - 1].split("'") 
    strcmd1 = lst[1]
    self.log.info ("Executing : " +strcmd1) 
                       
    output = wait_for_output(strcmd1, timeout = 600)
    if output == "FAIL":
        return output
    strcmd2 = "oc status -v"
    self.log.info ("Executing : " +strcmd2)
    output = wait_for_output(strcmd2)
    return output

def oc_port_expose(self, service_name):
    strcmd = "oc expose service " +service_name
    output = wait_for_output(strcmd)
    return output

def oc_get_service(self):
    strcmd = "oc get service"
    output = wait_for_output(strcmd)
    return output

def oc_get_pod(self):
    strcmd = "oc get pod"
    output = wait_for_output(strcmd)
    return output

def routing_cdk(self, service_name, openshift_project_name):
    strcmd = "oc get route"
    output = wait_for_output(strcmd)
    if output == "FAIL":
        return output
    for lines in output.split():
        if service_name +"-" +openshift_project_name in lines:
            strcmd = "curl -I http://" +lines
            output = wait_for_text_in_output(strcmd, text = "HTTP/1.1 200 OK")
    return output

def oc_delete(self, project_name):
    strcmd = "oc delete project " +project_name
    time.sleep(15)
    output = "FAIL"
    try:
        output = process.system_output(strcmd)
    except:
        return output
    return output

def oc_logout(self):
    strcmd = "oc logout"
    self.log.info ("Executing : " +strcmd)
    output = wait_for_output(strcmd)
    return output

def add_new_template(self, template):
    strcmd = "oc new-app --template=" +template
    self.log.info ("Executing : " +strcmd)
        
    lst = []
    output = wait_for_output(strcmd)
    if output == "FAIL":
        return output
    for lines in output.splitlines():
        if template in lines:
            lst.append(lines)
                
    lst = lst[len(lst) - 1].split("'") 
    strcmd1 = lst[1]
    self.log.info ("Executing : " +strcmd1) 
    output = wait_for_output(strcmd1)
    if output == "FAIL":
        return output
    
    strcmd2 = "oc status -v"
    self.log.info ("Executing : " +strcmd2)
    output = wait_for_output(strcmd2)
    return output

