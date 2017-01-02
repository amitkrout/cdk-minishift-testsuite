from avocado import Test
from avocado.utils import process
import os, re, pexpect, platform, sys
from avocado import VERSION
import logging
import time
import imp

def new_project(self, projectname, registry, servicename, tempalte = False, dbservicename = "default"):
    
    output = minishift.add_new_project(self, projectname)
    self.assertIn(projectname, output, "Failed to create " +projectname)
    
    if not tempalte:
        output = minishift.add_new_app(self, registry)
        lst = registry.split("/")
        repo = lst[len(lst) - 1]
        parten = re.search(r"^(?=.*?\b\\*\b)(?=.*?\bfailed\b)(?=.*?\b%s\b).*$" %repo, output)
        if parten:
            self.assertIn(parten, output, registry +" deployment failed")
    else:
        output = minishift.add_new_template(self, registry)
        parten = re.search(r"^(?=.*?\b\\*\b)(?=.*?\bfailed\b)(?=.*?\b%s\b).*$" %registry, output)
        if parten:
            self.assertIn(parten, output, registry +" deployment failed")
        if "default" not in dbservicename:
            parten = re.search(r"^(?=.*?\bdeploys\b)(?=.*?\b%s\b)(?=.*?\bopenshift/%s\b).*$" %(dbservicename, dbservicename), output)
            if parten:
                self.assertIn(parten, output, dbservicename +" deployment failed")
    if not tempalte:    
        output = minishift.oc_port_expose(self, servicename)
        self.assertIn("exposed", output, "Service failed to expose " +projectname)
    else:
        pass
                                
    output = minishift.routing_cdk(self, servicename, projectname)
    self.assertIn("HTTP/1.1 200 OK", output, "Service " +servicename +"-" +projectname +" fail to expose to outside")
                                    
    output = minishift.oc_get_pod(self)
    self.assertIn("Running", output, "Failed to run pod")
                                        
    output = minishift.oc_delete(self, projectname)
    self.assertIn("deleted", output, "Failed to delete " +projectname)
    
def clean_failed_app(self, projectname):
    output = minishift.oc_delete(self, projectname)
    if output == "FAIL":
        self.log.info("No failed " +projectname +" found")
    else:
        self.log.info("Failed " +projectname +" deleted")


class minishiftSanity(Test):
    
    def setUp(self):
        '''
        preconfiguring the test setup before running each test case
        Arg:
            self (object): Object of the current method
        '''
	global minishift
        minishift = imp.load_source('minishift', self.params.get('minishift_lib_MODULE'))
        self.log.info("###########################################################################################")
        self.log.info("Avocado version : %s" % VERSION)
        self.log.info("###########################################################################################")
        self.Hypervisor_Provider = self.params.get('Hypervisor_Provider')
        self.iso_url = self.params.get('iso_url')
        self.Provisioning_OpenShift = self.params.get('Provisioning_OpenShift')
        
    """    
    def test_ms_start(self):
        cmd = "minishift start --vm-driver " +self.Hypervisor_Provider +" --iso-url " +self.iso_url
        self.log.info("Starting minishift...")
        
        child = pexpect.spawn(cmd)
        
        index = child.expect(["The server is accessible via web console at:", pexpect.EOF, pexpect.TIMEOUT], timeout=300)
        self.log.info(child.before)
        for lines in child.before.splitlines():
            if "Provisioning OpenShift" in lines:
                partial_path = lines.split()
                path = partial_path[3].split("'")
                #global provision_path
                provision_path = path[1]
                self.log.info("Provisioning OpenShift path "+provision_path)
        if index==0:
            rc = child.expect(pexpect.EOF, timeout=300)
            self.assertEqual(0, rc)
            self.log.info(child.before)
        else:
            self.fail("Minishift start failed")
            provision_path = None
    
    """        
    def test_ms_start(self):
	if self.iso_url:
	    cmd = "minishift start --iso-url " + self.iso_url
            self.log.info("iso_url specified, starting minishift with --iso-url flag: " + self.iso_url)
	else:
            cmd = "minishift start"
            self.log.info("iso_url not specified, starting minishift without --iso-url flag")
        child = pexpect.spawn(cmd)
        index = child.expect(["The server is accessible via web console at:", pexpect.EOF, pexpect.TIMEOUT], timeout=120)
        if index==0:
            self.log.info("Minishift start finished, OpenShift is started")
        else:
            self.fail("Minishift start failed")
            
    def test_python_project(self):
        new_project(self, self.params.get('openshift_python_PROJECT'), self.params.get('openshift_python_REGISTRY'), self.params.get('service_python_NAME'))
        
    def test_ruby_project(self):
        clean_failed_app(self, self.params.get('openshift_python_PROJECT'))
        new_project(self, self.params.get('openshift_ruby_PROJECT'), self.params.get('openshift_ruby_REGISTRY'), self.params.get('service_ruby_NAME'))
    
    def test_perl_project(self):
        clean_failed_app(self, self.params.get('openshift_ruby_PROJECT'))
        new_project(self, self.params.get('openshift_perl_PROJECT'), self.params.get('openshift_perl_REGISTRY'), self.params.get('service_perl_NAME'))
    
    def test_nodejs_project(self):
        clean_failed_app(self, self.params.get('openshift_perl_PROJECT'))
        new_project(self, self.params.get('openshift_nodejs_PROJECT'), self.params.get('openshift_nodejs_REGISTRY'), self.params.get('service_nodejs_NAME'))
    
    def test_php_project(self):
        clean_failed_app(self, self.params.get('openshift_nodejs_PROJECT'))
        new_project(self, self.params.get('openshift_php_PROJECT'), self.params.get('openshift_php_template'), self.params.get('service_php_NAME'), tempalte = True)
    
    def test_nodejs_mongodb_template(self):
        clean_failed_app(self, self.params.get('openshift_php_PROJECT'))
        new_project(self, self.params.get('openshift_nodejsmongodb_PROJECT'), self.params.get('openshift_nodejsmongodb_TEMPLATE'), self.params.get('service_nodejsmongodb_NAME'), tempalte = True, dbservicename = "mongodb")
    
    def test_logout(self):
        clean_failed_app(self, self.params.get('openshift_nodejsmongodb_PROJECT'))
        output = minishift.oc_logout(self)
        logout_str = "Logged " +"\"" +self.params.get('openshift_USERNAME') +"\"" +" out on " +"\"https://"
        self.assertIn(logout_str, output, "Failed to log out")
            
    def test_ms_ssh(self):
        child = pexpect.spawn("minishift ssh")
	child.sendline("whoami")
	index = child.expect(["docker", pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        if index==0:
            self.log.info("Minishift ssh was successful")
        else:
            self.fail("Minishift ssh failed")

    def test_ms_stop(self):
        cmd = "minishift stop"
        self.log.info("Stopping minishift...")
        child = pexpect.spawn(cmd)
        index = child.expect(["Machine stopped.", pexpect.EOF, pexpect.TIMEOUT], timeout=60)
        if index==0:
            self.log.info("Machine stopped.")
        else:
            self.fail("Error while stopping the machine")
            
    def test_ms_repetetive_use(self):
        self.log.info("Testing repetetive use of minishifrt (start-stop-start...)")
        for x in range(3):
            self.test_ms_start()
            self.test_ms_stop()
            self.log.info("Start-stop of machine OK - run number: " + str(x))
    
    def test_ms_delete_existing(self):
        self.log.info("Trying to delete existing machine...")
        #self.test_ms_stop()
        cmd = "minishift delete"
        child = pexpect.spawn(cmd)
        index = child.expect(["Machine deleted", "Host does not exist", pexpect.EOF, pexpect.TIMEOUT],timeout=60)
        if index==0:
            self.log.info("Machine deleted.")
        else:
            self.fail("Delete attempt failed.")
