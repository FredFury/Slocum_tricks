import os
import sys
import urllib.request
import paramiko
import datetime
import numpy
import simplejson
import codecs
import json
import csv
from netCDF4 import Dataset


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

#send file to FTP server
def update(sg):
    print("updating git...")
    print("Syncing "+sg+".json")
    cmd  = "git commit -m 'updated location' " + sg +".json"
    cmd2  = "git commit -m 'updated location csv' " + sg +".csv"
    cmd3  = "git commit -m 'updated cmdfile' " + sg +"cmdfile"
    cmd4  = "git commit -m 'updated targets' " + sg +"targets"
    print(cmd)
    os.system(cmd)
    print(cmd2)
    os.system(cmd2)
    print(cmd3)
    os.system(cmd3)
    print(cmd4)
    os.system(cmd4)
    os.system("git push")

def removeDupes(file):
#Removes duplicate rows from csv
    rows = csv.reader(open(file, "r"))
    newrows = []
    for row in rows:
        if row not in newrows:
            newrows.append(row)
    writer = csv.writer(open(file, "w"))
    writer.writerows(newrows)

def convertDecimalDegrees(coord):
	lenghtOfDegrees = len(coord)-6
	degrees = float(coord[:lenghtOfDegrees])
	number1 = coord.split(".")[0][-2:]
	number2 = coord.split(".")[1]
	decimalMinutes = number1 + "." + number2
	decimalMinutes = float(decimalMinutes)
	decimalOfDegree = decimalMinutes/60
	if degrees < 0:
		decimalOfDegree = decimalOfDegree * -1.0
	#print degrees,decimalOfDegree
	dd = degrees + decimalOfDegree
	return dd

def retrieveFile(sg):
    # Open a transport
    host = "seaglider.socco.org.za"
    port = 22
    transport = paramiko.Transport((host, port))
    auth_file = "/root/sg_auth"
    f = open(auth_file, "r")
    username = f.readline().strip("\n")
    password = f.readline().strip("\n")
    f.close()
    transport.connect(username = username, password = password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    path = '/home/'+sg+'/'
    fileList = sftp.listdir(path)
    #print(fileList) 
    files = []
    for filename in fileList:
        if filename.endswith('.nc') and filename.startswith('p'):
            files.append(filename)
            #targetFile = filename
            #break;
    files.sort()
    targetFile = files[-1]
    outputFile = sg+"data.nc"
    cmdfile = sg+"cmdfile"
    targetsfile = sg+"targets"
    sftp.get(path+targetFile,outputFile)
    sftp.get(path+"cmdfile",cmdfile)
    try: # There may not be a targets file
    	sftp.get(path+"targets",targetsfile)
    except:
        print("No targets file found")
    sftp.close()
    transport.close()

def read_NC(nc_f,sg):
    data = []
    #data['data'] = []
    dataDict = {}
    nc_fid = Dataset(nc_f, 'r')
    #Globals
    #########################
    dataDict["project"] = nc_fid.project
    dataDict["platform_id"] = nc_fid.platform_id
    dataDict["glider"] = int(nc_fid.glider)
    dataDict["lat"] = nc_fid.geospatial_lat_min
    dataDict["lon"] = nc_fid.geospatial_lon_min
    dataDict["instruments"] = nc_fid.instrument
    dataDict["dive_number"] = int(nc_fid.dive_number)
    dataDict["start_time"] = int(nc_fid.start_time)
    dataDict["mission_number"] = int(nc_fid.mission)
    start_time = int(nc_fid.start_time)
    stime =  datetime.datetime.fromtimestamp(start_time).strftime('%d-%m-%Y %H:%M:%S')
    dataDict["start_time_human"] = stime
    mission_number = int(nc_fid.mission)
    dive_number = int(nc_fid.dive_number)

    # cmdfile parameters
    #########################
    dataDict["d_tgt"] = int(nc_fid.variables["log_D_TGT"][:])
    dataDict["d_abort"] = int(nc_fid.variables["log_D_ABORT"][:])
    dataDict["altim_ping_depth"] = int(nc_fid.variables["log_ALTIM_PING_DEPTH"][:])
    dataDict["t_dive"] = int(nc_fid.variables["log_T_DIVE"][:])
    dataDict["t_abort"] = int(nc_fid.variables["log_T_ABORT"][:])
    dataDict["t_mission"] = int(nc_fid.variables["log_T_MISSION"][:])
    dataDict["c_vbd"] = int(nc_fid.variables["log_C_VBD"][:])
    dataDict["c_pitch"] = int(nc_fid.variables["log_C_PITCH"][:])
    dataDict["c_roll_climb"] = int(nc_fid.variables["log_C_ROLL_CLIMB"][:])
    dataDict["c_roll_dive"] = int(nc_fid.variables["log_C_ROLL_DIVE"][:])
    dataDict["sm_cc"] = int(nc_fid.variables["log_SM_CC"][:])
    dataDict["sim_pitch"] = int(nc_fid.variables["log_SIM_PITCH"][:])
    dataDict["max_buoy"] = int(nc_fid.variables["log_MAX_BUOY"][:])
    #print nc_fid.variables["gc_roll_retries"][:]
    dataDict["gc_roll_retries"] = sum(nc_fid.variables["gc_roll_retries"][:])
    dataDict["gc_roll_errors"] = sum(nc_fid.variables["gc_roll_errors"][:])
    dataDict["gc_pitch_retries"] = sum(nc_fid.variables["gc_pitch_retries"][:])
    dataDict["gc_pitch_errors"] = sum(nc_fid.variables["gc_pitch_errors"][:])
    dataDict["gc_vbd_retries"] = sum(nc_fid.variables["gc_vbd_retries"][:])
    dataDict["gc_vbd_errors"] = sum(nc_fid.variables["gc_vbd_errors"][:])

    # Datasets
    #########################
    # time_data =  nc_fid.variables["time"][:]
    # time_data = map(int, time_data)
    # dataDict["time_data"] = time_data
    # print(min(time_data))
    # print(max(time_data))
    # duration = (max(time_data) - min(time_data))/60
    # dataDict["duration"] = int(round(duration))
    # dataDict["buoyancy_data"]  = map(float, nc_fid.variables["buoyancy"][:])
    # dataDict["eng_rollCtl_data"] = map(float,nc_fid.variables["eng_rollCtl"][:])
    # dataDict["eng_pitchCtl_data"] = map(float, nc_fid.variables["eng_pitchCtl"][:])
    #
    # depth_data  =  nc_fid.variables["depth"][:]
    # depth_data = map(float, depth_data)
    # dataDict["depth_data"] = map(lambda x: -1*x, depth_data) #depth_data
    # dataDict["depth"] = int(round(max(depth_data)))

    json_file = "%s_%s_data.json" % (sg,mission_number)
    dataDict["file_name"] = json_file

    data.append(dataDict)
    print (data)
    outputfile = "/root/gliders/"+sg + ".json"
    #dumped = json.dumps(dataDi)
    with open(outputfile, 'w') as f:
    	json.dump(data,f, cls=MyEncoder)

    sgCSVpath = "/root/gliders/"+sg+".csv"
    with open(sgCSVpath, "a") as output:
        line = "%s,%s,%s,%s\n" %(dataDict["start_time_human"],dataDict["lat"],dataDict["lon"],dataDict["dive_number"])
        print("add csv line: " + line+ "\nTo: "+ sgCSVpath)
        output.write(line)
    #lazily remove duplicates from the CSV
    removeDupes(sgCSVpath)
    #with open(outputfile, 'w') as outfile:
    #        simplejson.dump(data, outfile, ignore_nan=True)
    #with open(outputfile, 'w') as file:
    #    file.write(simplejson.dumps(data))
    #with open(outputfile, 'w') as f:
    #    for item in data:
    #        f.write("%s\n" % item)

def main():
    arg = sys.argv[1]
    retrieveFile(arg)
    outputFile = arg+"data.nc"
    read_NC(outputFile,arg)
    update(arg)

main()

