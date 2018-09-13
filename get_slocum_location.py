import os
import urllib.request
import ftplib
from xml.etree import ElementTree as ET
import urllib
import time
import glob
import json
from geojson import Point
from geojson import LineString
import os

#send file to FTP server
def update():
    print ("updating slocum.geojson to git...")
    os.system("git commit -m 'updated location' slocum.geojson")
    os.system("git push origin master")

#convert to DD.DDD
def convertISO2DecimalDegrees(coord):
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

def retrieve(address,output):
    print ("Retrieving files...")
    try:
        urllib.request.urlretrieve(address, output)
        urllib.request.urlcleanup()
    except:
        print ("error in ftp retrieval, waiting 25 seconds")
        time.sleep(25)
        urllib.urlretrieve(address, output)
        urllib.urlcleanup()


def findData(data_file,log_file):
    print ("scraping data...")
    data = open (data_file,'r')
    glider_name = ""
    time = log_file.split(".")[0].split("_")[-1]
    mission = ""
    lat = ""
    lon = ""
    battery_charge = ""
    battery_voltage = ""
    wp_lat = ""
    wp_lon = ""
    coulomb_amphr_total = ""
    leakdetect = ""
    leakdetect_forward = ""
    #log_file = ""

    for line in data:
        if line[:13] =="Vehicle Name:":
            glider_name = line.split(": ")[1].rstrip()
        if line[:11] == "MissionName":
            mission = line.split(":")[1].split(" ")[0]
        if line[:13] == "GPS Location:":
            lat= line.split(" ")[2].rstrip()
            lon= line.split("N")[1].split("E")[0].strip()
        #if line[:13] == "   m_lat(lat)":
        #    lat = line.split("(lat) ")[1].rstrip()
        #if line[:13] == "   m_lon(lon)":
        #    lon = line.split("(lon) ")[1].rstrip()
        if line[:46] == "   sensor:m_lithium_battery_relative_charge(%)":
            battery_charge = line.split("=")[1].split("  ")[0]
        if line[:24] == "   sensor:c_wpt_lat(lat)":
            wp_lat = line.split("=")[1].split("  ")[0]
        if line[:24] == "   sensor:c_wpt_lon(lon)":
            wp_lon = line.split("=")[1].split("  ")[0]
        if line[:40] == "   sensor:m_coulomb_amphr_total(amp-hrs)":
            coulomb_amphr_total = line.split("=")[1].split("  ")[0]
        if line[:37] == "   sensor:m_leakdetect_voltage(volts)":
            leakdetect = line.split("=")[1].split("  ")[0]
        if line[:45] == "   sensor:m_leakdetect_voltage_forward(volts)":
            leakdetect_forward = line.split("=")[1].split("  ")[0]
        if line[:26] == "   sensor:m_battery(volts)":
            battery_voltage = line.split("=")[1].split("  ")[0]
        if line[:24] == "   sensor:m_vacuum(inHg)":
            vacuum = line.split("=")[1].split("  ")[0]

    log_file_end = log_file+"\n"
    # Generate CSV
    row = ",".join((glider_name,mission,time,lat,lon,battery_voltage,battery_charge,wp_lat,wp_lon,coulomb_amphr_total,leakdetect,leakdetect_forward,log_file_end))
    print (row)
    csv = open("slocum.csv",'a')
    csv.write(row)
    csv.close()
    # Generate some GEOJSON data
    # Create GEOJSON point of current glider location:
    pointMarker = Point((convertISO2DecimalDegrees(lon),convertISO2DecimalDegrees(lat)))
    with open('slocum.geojson', 'w') as f:
        json.dump(pointMarker,f)
    #update('slocum.geojson')


def checkifrecent():
    output = "slocum.dat"
    address = "ftp://dockserveruser:dockserveruser@dockserver.socco.org.za/gliders/socco_461/logs/"

    # find the last line, change to a file you have
    list_file_reader = open ( 'list',"r" )
    for line in list_file_reader:
        file_= line.split(',')[11]
        if file_ != "log_file":
            #address = address+file_
            #retrieve(address,output):
            #findData(,file_)

            print (file_)

def retroactive():
    output = "slocum.dat"
    address = "ftp://dockserveruser:dockserveruser@dockserver.socco.org.za/gliders/socco_461/logs/"

    # find the last line, change to a file you have
    list_file_reader = open ( 'list',"r" )
    for line in list_file_reader:
        file_= line.split(' ')[-1:][0].rstrip()
        #print line
        if file_[-4:] == ".log":
            address_file = address+file_
            #print address
            retrieve(address_file,output)
            findData(output,file_)

def retroactive_local():
    # constructs a CSV with historic logs
    filez = glob.glob("/logs/*.log")
    # find the last line, change to a file you have
    list_file_reader = open ( 'list',"r" )
    for line in filez:
        findData(line,line)

def lookfor():
    #use this to look for lines in a dir of logs
    filez = glob.glob("batt_swap/*.log")
    for file_ in filez:
        logz = open ( file_,"r" )
        for line in logz:
            if line[:27] == "put m_coulomb_amphr_total 0":
                print ("found in: " + file_)
                print (line)

def main():
    print ("Starting up...")
    #let's build the ftp address here:
    auth_file = "/root/slocum_auth"
    f = open(auth_file, "r")
    username = f.readline()
    password = f.readline()

    host = "dockserver.socco.org.za"
    path = "/gliders/socco_461/logs/"
    list_file = "list"
    address = 'ftp://%s:%s@%s%s' % (username,password,host,path)
    #print "Getting file listing from: " + address + list_file

    # Retrieve a list of files
    retrieve(address,list_file) ##

    # read a text file as a list of lines
    # find the last line, change to a file you have
    list_file_reader = open ( 'list',"r" )
    lineList = list_file_reader.readlines()
    last_file = lineList[-1].split(' ')[-1:][0].rstrip()
    print(last_file)
    output = "slocum.dat"
    #address = 'ftp://%s:%s@%s%s%s' % (usr,psswrd,host,path,last_file)
    #print address, output

    findData(output,last_file) ## scrape a log and append the data to a CSV
    #update()
    ##checkifrecent()

    #retroactive_local() ## build csv from a local dir
    ##lookfor() ## look for a certian line in a local dir

main()
