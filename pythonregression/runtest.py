#!/usr/bin/python
import cinderclient.v1
from novaclient import client
from subprocess import (PIPE, Popen)
import time
import datetime
import random
USER='admin'
PASS='xxxxxxyzyyz'
TENANT='openstack'
AUTH_URL = 'https://keystone-server:5000/v2.0/' #Set the Keystone URL
NUMOFREGRESSIONS=10 #Set this value to a higher value, if needed.
IMAGEID='3342ca82-d287-4eba-af53-3a634f9ae6b4' #Set this to the image id which needs to be used for the tests
IMAGEMINSIZE=20
NETID='da6bb088-6683-41f0-884f-1fc5a0f0cacf' #Set ths to the net-id you wanted the instances to launch 
KEYNAME='phani'
nics = [{"net-id": NETID}]
VERSION=2
#avail_zones = ["AMS4","AMS5"]
volume_types = ["Economy","FirstClass","BusinessClass"]
avail_zones = ["ZONE1","ZONE2"]

cinder_client = cinderclient.v1.client.Client(USER, PASS, TENANT, AUTH_URL, service_type="volume",insecure=True)
nova_client = client.Client(VERSION,USER, PASS, TENANT, AUTH_URL,insecure=True)


def get_rand_zone():
		return random.sample(avail_zones,1)[0]				

def get_rand_vol_type():
		return random.sample(volume_types,1)[0]				

def invoke(command):
    '''
    Invoke command as a new system process and return its output.
    '''
    return Popen(command, stdout=PIPE, shell=True).stdout.read()


def get_volumes():
        volumes=cinder_client.volumes.list()
        return volumes

def get_nova_instances():
        instances=nova_client.servers.list()
        return instances

def volume_id(volume):
        return volume.id

def volume_status(volume):
        return volume.status

def nova_status(instance):
        return instance.status

def sleep_while_nova_status_active():
        instances = get_nova_instances()
        flag=0
        for instance in instances:
                if(nova_status(instance) <> 'ACTIVE'):
                        flag=1
        return flag

def sleep_while_cinder_status_available():
        cinder_vols = get_volumes()
        flag=0
        for vol in cinder_vols:
                if(volume_status(vol) <> 'available'):
                        flag=1
        return flag

def sleep_while_deleting_all_vols():
        return len(get_volumes())

def sleep_while_deleting_all_instances():
        return len(get_nova_instances())

def create_volumes():
        print "Creating Volumes of Qty :"+str(NUMOFREGRESSIONS)
        for i in range(1,NUMOFREGRESSIONS+1):
                name="test-vol-"+str(i)
                cinder_client.volumes.create(display_name=name, size=i,availability_zone=get_rand_zone())

def create_volumes_image():
        print "Creating VOlumes with image"
        for i in range(1,NUMOFREGRESSIONS+1):
                name="cinder-vol-image-"+str(i)
                cinder_client.volumes.create(display_name=name,imageRef=IMAGEID,size=IMAGEMINSIZE+i,availability_zone=get_rand_zone())


def delete_all_volumes():
        cinder_vols = get_volumes()
        for vol in cinder_vols:
                vol.delete()

def delete_all_instances():
        instances = get_nova_instances()
        for instance in instances:
                instance.delete()

def cinder_test1():
        print "Test 1. Simple Volume Creation and Deletion."
        create_volumes()
        print "Waiting for all volumes to be created.. If the process is struck here, please check the horizon interface. SOmething Wrong."
        while(sleep_while_cinder_status_available()):
                time.sleep(2)
        print "All the volumes created and available. Now going ahead and deleting them. Please Check The Horizon interface if Struck here"
        delete_all_volumes()
        while(sleep_while_deleting_all_vols()>0):
                time.sleep(2)
        print "Deleted All volumes"


def cinder_test2():
        print "Test 2. Volume Creation from Image and Deletion."
        create_volumes_image()
        print "Waiting for all volumes to be created.. If the process is struck here, please check the horizon interface. SOmething Wrong."
        while(sleep_while_cinder_status_available()):
                time.sleep(2)
        print "All the volumes created and available. Now going ahead and deleting them. Please Check The Horizon interface if Struck here"
        delete_all_volumes()
        while(sleep_while_deleting_all_vols()>0):
                time.sleep(2)
        print "Deleted All volumes"

def nova_boot_ephemeral():
        for i in range(1,NUMOFREGRESSIONS+1):
                dname="ephemeral-"+str(i)
                nova_client.servers.create(dname,IMAGEID,2,nics=nics,availability_zone=get_rand_zone())

def nova_boot_attach_blankvol(volsize):
        for i in range(1,NUMOFREGRESSIONS+1):
                iname="instance-blankvol-"+str(i)
                bd_mapping = {'source_type': 'blank', 'size': str(i) }
                #nova_client.servers.create(iname,IMAGEID,2,nics=nics,block_device_mapping=bd_mapping)
                nova_cmd="nova --insecure --os-username "+USER+" --os-password '"+PASS+"' --os-tenant-name '"+TENANT+"' --os-auth-url '"+AUTH_URL+"' boot --flavor 2 --image "+ IMAGEID +" --availability-zone " +get_rand_zone()+ " --key-name "+KEYNAME+" --nic net-id="+NETID+" --block-device source=blank,dest=volume,size="+str(volsize+i)+",format=ext4,device=vdb,shutdown=remove "+iname
                invoke(nova_cmd)

def nova_boot_attach_imagevol(volsize):
        for i in range(1,NUMOFREGRESSIONS+1):
                iname="instance-imagevol-"+str(i)
                bd_mapping = {'source_type': 'blank', 'size': str(i) }
                #nova_client.servers.create(iname,IMAGEID,2,nics=nics,block_device_mapping=bd_mapping)
                nova_cmd="nova --insecure --os-username "+USER+" --os-password '"+PASS+"' --os-tenant-name '"+TENANT+"' --os-auth-url '"+AUTH_URL+"' boot --flavor 2 --availability-zone " +get_rand_zone()+ "  --key-name "+KEYNAME+" --nic net-id="+NETID+" --block-device source=image,id="+IMAGEID+",dest=volume,size="+str(volsize+i)+",shutdown=remove,bootindex=0 "+iname
                invoke(nova_cmd)

def nova_boot_attach_imagevol_attach_blank(volsize):
        for i in range(1,NUMOFREGRESSIONS+1):
                iname="instance-imagevol-"+str(i)
                bd_mapping = {'source_type': 'blank', 'size': str(i) }
                #nova_client.servers.create(iname,IMAGEID,2,nics=nics,block_device_mapping=bd_mapping)
                nova_cmd="nova --insecure --os-username "+USER+" --os-password '"+PASS+"' --os-tenant-name '"+TENANT+"' --os-auth-url '"+AUTH_URL+"' boot --flavor 2 --availability-zone " +get_rand_zone()+ "  --key-name " +KEYNAME+" --nic net-id="+NETID+" --block-device source=image,id="+IMAGEID+",dest=volume,size="+str(volsize+i)+",shutdown=remove,bootindex=0 "+" --block-device source=blank,dest=volume,size="+str(volsize+i)+",format=ext4,device=vdb,shutdown=remove "+iname
                invoke(nova_cmd)

def nova_test1():
        print "Test3. Nova Boot Instances with images - ephemeral"
        nova_boot_ephemeral()
        print "Waiting for all the instances to be made available"
        while(sleep_while_nova_status_active()):
                time.sleep(2)
        print "All the instances are create Now deleting them"
        delete_all_instances()
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Delete All Instances"
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Deleted All Instances"

def nova_test2():
        print "Test4. Nova Boot Instances with images - attached blankvol"
        nova_boot_attach_blankvol(20)
        print "Waiting for all the instances to be made available"
        while(sleep_while_nova_status_active()):
                time.sleep(2)
        print "All the instances are create Now deleting them"
        delete_all_instances()
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Delete All Instances"
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Deleted All Instances"
        while(sleep_while_deleting_all_vols()>0):
                time.sleep(2)
        print "Deleted All volumes"

def nova_test3():
        print "Test5. Nova Boot Instances with a volume from image"
        nova_boot_attach_imagevol(20)
        print "Waiting for all the instances to be made available"
        while(sleep_while_nova_status_active()):
                time.sleep(2)
        print "All the instances are create Now deleting them"
        delete_all_instances()
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Delete All Instances"
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Deleted All Instances"
        while(sleep_while_deleting_all_vols()>0):
                time.sleep(2)
        print "Deleted All volumes"

def nova_test4():
        print "Test6. Nova Boot Instances with a volume from image and attach blanvol"
        nova_boot_attach_imagevol_attach_blank(20)
        print "Waiting for all the instances to be made available"
        while(sleep_while_nova_status_active()):
                time.sleep(2)
        print "All the instances are create Now deleting them"
        delete_all_instances()
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Delete All Instances"
        while(sleep_while_deleting_all_instances()>0):
                time.sleep(2)
        print "Deleted All Instances"
        while(sleep_while_deleting_all_vols()>0):
                time.sleep(2)
        print "Deleted All volumes"
i=1
while(i>0):
        print "Run : "+str(i)
        print "Date and Time : "+str(datetime.datetime.now())
        #cinder_test1()
        print "Date and Time : "+str(datetime.datetime.now())
        #cinder_test2()
        print "Date and Time : "+str(datetime.datetime.now())
        #nova_test1()
        print "Date and Time : "+str(datetime.datetime.now())
        #nova_test2()
        print "Date and Time : "+str(datetime.datetime.now())
        #nova_test3()
        print "Date and Time : "+str(datetime.datetime.now())
	nova_test4()
        i=i+1

