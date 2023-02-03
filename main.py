#Программа  DLvov (показывает ВМ на удаленных хостах)
# python main.py 10.6.16.44 root 'pass' --backup dl-vm2
# python main.py 10.6.16.44 root 'pass' --net
# python main.py 10.6.16.44 root 'pass'

import prlsdkapi
import sys
import os

consts = prlsdkapi.prlsdk.consts

def status(s):
    if s == prlsdkapi.consts.VMS_COMPACTING:
        return "COMPACTING"
    elif s == prlsdkapi.consts.VMS_CONTINUING:
        return "CONTINUING"
    elif s == prlsdkapi.consts.VMS_DELETING_STATE:
        return "DELETING_STA"
    elif s == prlsdkapi.consts.VMS_MIGRATING:
        return "MIGRATING"
    elif s == prlsdkapi.consts.VMS_MOUNTED:
         return "MOUNTE"
    elif s == prlsdkapi.consts.VMS_PAUSED:
        return "PAUSED"
    elif s == prlsdkapi.consts.VMS_PAUSING:
        return "PAUSING"
    elif s == prlsdkapi.consts.VMS_RECONNECTING:
        return "RECONNECTING"
    elif s == prlsdkapi.consts.VMS_RESETTING:
        return "RESETTING"
    elif s == prlsdkapi.consts.VMS_RESTORING:
        return "RESTORING"
    elif s == prlsdkapi.consts.VMS_RESUMING:
        return "RESUMING"
    elif s == prlsdkapi.consts.VMS_RUNNING:
        return "RUNNING"
    elif s == prlsdkapi.consts.VMS_SNAPSHOTING:
        return "SNAPSHOTING"
    elif s == prlsdkapi.consts.VMS_STARTING:
        return "STARTING"
    elif s == prlsdkapi.consts.VMS_STOPPED:
        return "STOPPED"
    elif s == prlsdkapi.consts.VMS_STOPPING:
        return "STOPPING"
    elif s == prlsdkapi.consts.VMS_SUSPENDED:
        return "SUSPENDED"
    elif s == prlsdkapi.consts.VMS_SUSPENDING:
        return "SUSPENDING"
    elif s == prlsdkapi.consts.VMS_SUSPENDING_SYNC:
        return "SUSPENDING_SYNC"
    elif s == prlsdkapi.consts.VMS_UNKNOWN:
        return "UNKNOWN"

def create_backup(serv,host,vm_name):
#server,serverip,sys.argv[5])
    try:
	vms = serv.get_vm_list_ex(prlsdkapi.consts.PVTF_VM )
	founid=0
	for res in [ r for r in vms.wait() ]:
        	rescfg = res.get_config()
	#	print(res.get_name()+" "+vm_name)
		if str(res.get_name()) == str(vm_name):
			found=1
			break
	if found == 1:
    		print("Create backup for: ", str(rescfg.get_uuid()))
        	backupJob = serv.create_vm_backup(rescfg.get_uuid(), host, 0, "", "Create from python script", consts.PBT_INCREMENTAL, 0, True)
			#			sVmUuid, sTargetHost, nTargetPort, sTargetSessionId, strDescription, backup_flags, reserved_flags, force_operation
        	res = backupJob.wait()
        	print("The VM has been successfully backed up with backup id %s" % res.get_param_by_index(1).get_backup_uuid())
    except IndexError:
        print ("Something went wrong during the backup creation")
def login_server(server,host,login,password):
    if host == "localhost" or host == "127.0.0.1":
        try:
            result = server.login_local().wait()
        except prlsdkapi.PrlSDKError, e:
            print("Login error {}:", e)
            print("Code is: ",str(e.error_code))
            exit(1)
    else:
        try:
            server.login(host,login,password,'',0,0,consts.PSL_NORMAL_SECURITY).wait()
        except prlsdkapi.PrlSDKError, e:
            print("Login error {}:", e)
            print("Code is: ", str(e.error_code))
            exit(1)
    return server
def get_host_info(serv):
    print("Host configuration info:")
    print("========================")
    try:
        res = serv.get_srv_config().wait()
    except prlsdkapi.PrlSDKError, e:
        print("Error {}",e)
    serv_conf = res.get_param()
    print("CPU count= ",str(serv_conf.get_cpu_count()))
    print("CPU model= "+ str(serv_conf.get_cpu_model()))
    print("RAM size = "+ str(serv_conf.get_host_ram_size()))
    print("Network adapter:")
    for i in range(serv_conf.get_net_adapters_count()):
        hw_net_adapter = serv_conf.get_net_adapter(i)
        adapter_type = hw_net_adapter.get_net_adapter_type()
        if adapter_type == consts.PHI_REAL_NET_ADAPTER:
            st = " Physical adapter "
        elif adapter_type == consts.PHI_VIRTUAL_NET_ADAPTER:
            st = " Virtual adapter "
        if hw_net_adapter.is_enabled():
            status = "enables"
        else:
            status = "disabled"
        print(str(i+1)+". "+" "+str(hw_net_adapter.get_name())+""+str(adapter_type)+" "+ str(status) +" "+ st )
#timeout=60*1000
if len(sys.argv) < 4:
    print "Usage:  python program.py '<server>' '<user>' '<password>'"
    exit()
serverip=sys.argv[1]
user=sys.argv[2]
passwd=sys.argv[3]
print("Sdk init...")
prlsdkapi.init_server_sdk()
#get_host_info(server)
print("Connect to dispatcher")
server = prlsdkapi.Server()
#server.login_local().wait(msecs=timeout)
server = login_server(server,serverip,user,passwd)

if len(sys.argv) == 5 and str(sys.argv[4]) == "--net":
    get_host_info(server)
    prlsdkapi.deinit_sdk()
    exit(0)
if len(sys.argv) == 6 and str(sys.argv[4]) == "--backup":
    create_backup(server,serverip,sys.argv[5])
    prlsdkapi.deinit_sdk()
    exit(0)
print("__________")
vms = server.get_vm_list_ex(prlsdkapi.consts.PVTF_VM + prlsdkapi.consts.PVTF_CT)
for res in [ r for r in vms.wait() ]:

    try:
        rescfg = res.get_config()
    except Exception:
        print ("Unable to get config, skip resource")
        continue

    try:
        print("UUID: {}| Name: {:<50}| State: {:>12}".format(str( rescfg.get_uuid()),str(res.get_name()) ,status(res.get_vm_info().get_state())))
    except Exception:
        print ("Exception on VM ")
server.logoff()
prlsdkapi.deinit_sdk()