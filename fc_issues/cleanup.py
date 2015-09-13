#!/usr/bin/python

import commands,time

def delete_mpaths(drive):
	status, output = commands.getstatusoutput("multipath -ll "+drive)
	lines=output.split("\n")
	if (len(lines) > 2):
		for line in lines[3:]:
			linearr = line.split()
			if(linearr[5]== "faulty"):
				status, output = commands.getstatusoutput('for i in /sys/class/scsi_host/host*/scan; do echo "- - -" > $i; done')
				status, output = commands.getstatusoutput('echo 1 > /sys/block/'+linearr[2]+'/device/delete')
				print linearr[2]

while(1):
	status, output = commands.getstatusoutput("multipathd show maps status")
	lines=output.split("\n")
	mpathlines=lines[1:]
	for line in mpathlines:
		mpathline = line.split()
		delete_mpaths(mpathline[0])
		if(int(mpathline[3])==0):
			print "Failed Paths or no failback paths, So deleting "+mpathline[0]
			status,output = commands.getstatusoutput("multipath -f "+mpathline[0])
	status, output = commands.getstatusoutput("multipath -W")
	print "Sleeping..."
	time.sleep(2)
