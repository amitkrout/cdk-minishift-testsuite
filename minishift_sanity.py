from avocado import Test
from avocado.utils import process
import os, re, pexpect, platform, sys
from avocado import VERSION
import logging
import time
import imp
import glob

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
        self.Is_Downstream = self.params.get('Is_Downstream')
        self.RHN_Username = self.params.get('RHN_USERNAME')
        self.RHN_Password = self.params.get('RHN_PASSWORD')
        sys.path.append(self.params.get('minishift_PATH'))
        sys.path.append(self.params.get('Provisioning_OpenShift'))
        self.log.info("Is downstream: ", self.Is_Downstream)

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
    
    def test_ms_setup_cdk(self):
        '''
        Testing if setup-cdk command is able to setup CDK properly:
        RHEL iso and OCP binary are in place.
        '''
        self.log.info(self.Is_Downstream)
        if self.Is_Downstream == False:
            self.log.info("Upstream testing is checked: skipping test for setup-cdk command")
            return
        cmd = "minishift setup-cdk"
        self.log.info("Running command: " + cmd)
        child = pexpect.spawn(cmd)
        index = child.expect(["CDK 3 setup complete.", pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        self.log.info("Console output: \n" + child.before + child.after)
        if not index==0:
            self.fail("CDK setup failed")
        self.log.info("Checking if rhel.iso exists")
        exists = os.path.isfile( os.environ['HOME'] + "/.minishift/cache/iso/minishift-rhel.iso" )
        if not exists:
            self.fail("minishift-rhel.iso is not present")
        self.log.info("Checking if oc binary exists")
        oc_binaries = glob.glob( os.environ['HOME'] + "/.minishift/cache/oc/v3.*")
        if not oc_binaries:
            self.fail("oc binary v3.* not found")
        self.log.info("OCP binaries for v3.x found:")
        for binary in oc_binaries:
            self.log.info(binary)
        self.log.info("Checking if config.json exists")
        exists = os.path.isfile( os.environ['HOME'] + "/.minishift/config/config.json" )
        if not exists:
            self.fail("config.json binary is not present")
        self.log.info("CDK Installation successful")

    def test_ms_start(self):
        time.sleep(10)
        if self.iso_url:
            cmd = "minishift start --iso-url " + self.iso_url + " --username " + self.RHN_Username + " --password " + self.RHN_Password
            self.log.info("iso_url specified, starting minishift with --iso-url flag: " + self.iso_url)
            self.log.info(" - running command: " + cmd)
        else:
            cmd = "minishift start " + " --username " + self.RHN_Username + " --password " + self.RHN_Password
            self.log.info("iso_url not specified, starting minishift without --iso-url flag")
            self.log.info(" - running command: " + cmd)
        child = pexpect.spawn(cmd)
        index = child.expect(["The server is accessible via web console at:", pexpect.EOF, pexpect.TIMEOUT], timeout=600)
        self.log.info("Console output: \n" + child.before + child.after)
        time.sleep(10)
        if index==0:
            self.log.info("Minishift start finished, OpenShift is started")
        else:
            self.fail("Minishift start failed")

    def test_ms_ssh(self):
        child = pexpect.spawn("minishift ssh")
	child.sendline("whoami")
	index = child.expect(["docker", pexpect.EOF, pexpect.TIMEOUT], timeout=10)
	self.log.info("Console output: \n" + child.before + child.after)
        if index==0:
            self.log.info("Minishift ssh was successful")
        else:
            self.fail("Minishift ssh failed")
	
    def test_ms_console(self):
        ''' Testing if url of web console returned by minishift is accessible '''
        cmd = "minishift console --url"
        self.log.info("Running command: " + cmd)
        child = pexpect.spawn(cmd)
        console_url = child.read()[:-2]
        self.log.info("Returned url of console: " + console_url)
        cmd = "curl " + console_url + "/console/ --insecure"
        self.log.info("Running command: " + cmd)
        child = pexpect.spawn(cmd)
        index = child.expect(['<title>OpenShift Web Console</title>', '"status": "Failure"', pexpect.TIMEOUT], timeout=10)
        self.log.info("Console output: \n" + child.before + child.after)
        if index == 0:
            self.log.info("Command returned valid page - has <title>OpenShift Web Console</title>")
        else:
            self.fail("Command did not returned valid page")

    def test_ms_ip(self):
        ''' Testing if ip command gives right ip and host to guest ping is ok '''
        cmd = "minishift ip"
        self.log.info("Running command: " + cmd)
        child = pexpect.spawn(cmd)
        machine_ip = child.read()[:-2]
        self.log.info("Returned host ip: " + machine_ip)
        cmd = "ping -c 5 " + machine_ip
        child = pexpect.spawn(cmd)
        index = child.expect (["5 received", "received", pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        self.log.info("Console output: \n" + child.before + child.after)
        if index==0:
            self.log.info("Ping successful")
        else:
            self.fail("Ping failed")

    def test_dns_from_guest(self):
        ''' Testing dns connection from guest to outside network '''
        self.log.info("Checking dns from guest to outside network")
        cmd = "minishift ssh"
        child = pexpect.spawn(cmd)
        child.sendline("ping -c 5 twitter.com")
        index = child.expect (["0 received", "received", pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        self.log.info("Console output: \n" + child.before + child.after)
        if index==1:
            self.log.info("Guest ping to twitter.com was successful")
        else:
            self.fail("Guest ping to twitter.com failed")

    def test_dns_from_host(self):
        ''' Testing dns connection from guest to outside network '''
        self.log.info("Checking dns from guest to outside network")
        cmd = "ping -c 5 twitter.com"
        child = pexpect.spawn(cmd)
        index = child.expect (["0 received", "received", pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        self.log.info("Console output: \n" + child.before + child.after)
        if index==1:
            self.log.info("Host ping to twitter.com was successful")
        else:
            self.fail("Host ping to twitter.com failed")

            
    def atest_python_project(self):
        new_project(self, self.params.get('openshift_python_PROJECT'), self.params.get('openshift_python_REGISTRY'), self.params.get('service_python_NAME'))
        
    def atest_ruby_project(self):
        clean_failed_app(self, self.params.get('openshift_python_PROJECT'))
        new_project(self, self.params.get('openshift_ruby_PROJECT'), self.params.get('openshift_ruby_REGISTRY'), self.params.get('service_ruby_NAME'))
    
    def atest_perl_project(self):
        clean_failed_app(self, self.params.get('openshift_ruby_PROJECT'))
        new_project(self, self.params.get('openshift_perl_PROJECT'), self.params.get('openshift_perl_REGISTRY'), self.params.get('service_perl_NAME'))
    
    def atest_nodejs_project(self):
        clean_failed_app(self, self.params.get('openshift_perl_PROJECT'))
        new_project(self, self.params.get('openshift_nodejs_PROJECT'), self.params.get('openshift_nodejs_REGISTRY'), self.params.get('service_nodejs_NAME'))
    
    def atest_php_project(self):
        clean_failed_app(self, self.params.get('openshift_nodejs_PROJECT'))
        new_project(self, self.params.get('openshift_php_PROJECT'), self.params.get('openshift_php_template'), self.params.get('service_php_NAME'), template = True)
    
    def atest_nodejs_mongodb_template(self):
        clean_failed_app(self, self.params.get('openshift_php_PROJECT'))
        new_project(self, self.params.get('openshift_nodejsmongodb_PROJECT'), self.params.get('openshift_nodejsmongodb_TEMPLATE'), self.params.get('service_nodejsmongodb_NAME'), template = True, dbservicename = "mongodb")
    
    def atest_logout(self):
        clean_failed_app(self, self.params.get('openshift_nodejsmongodb_PROJECT'))
        output = minishift.oc_logout(self)
        logout_str = "Logged " +"\"" +self.params.get('openshift_USERNAME') +"\"" +" out on " +"\"https://"
        self.assertIn(logout_str, output, "Failed to log out")

    def test_ms_stop(self):
        time.sleep(10)
        cmd = "minishift stop"
        self.log.info("Stopping minishift...")
        child = pexpect.spawn(cmd)
        index = child.expect(["Cluster stopped.", pexpect.EOF, pexpect.TIMEOUT], timeout=60)
        self.log.info("Console output: \n" + child.before + child.after)
        time.sleep(10)
        if index==0:
            self.log.info("Cluster stopped.")
        else:
            self.fail("Error while stopping the cluster.")
            
    def test_repetetive_use(self):
        self.log.info("Testing repetetive use of minishifrt (start-stop-start...)")
        for x in range(5):
            self.test_ms_start()
            self.test_ms_stop()
            self.log.info("Start-stop of machine OK - run number: " + str(x))

    def test_ms_delete_existing(self):
        self.log.info("Trying to delete existing machine...")
        cmd = "minishift delete"
        child = pexpect.spawn(cmd)
        index = child.expect(["Minishift VM deleted", "Host does not exist", pexpect.EOF, pexpect.TIMEOUT],timeout=60)
        self.log.info("Console output: \n" + child.before + child.after)
        if index==0:
            self.log.info("Minishift VM deleted.")
        else:
            self.fail("Delete attempt failed.")
