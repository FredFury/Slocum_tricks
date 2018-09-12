import os
import urllib.request
import ftplib 

#send file to FTP server
def update():
    print("updating git...")
    os.system("git commit -m 'updated location' slocum.csv")
    os.system("git push")


#convert to DD.DDD
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

urllib.request.urlretrieve('ftp://dockserveruser:dockserveruser@dockserver.socco.org.za/gliders/socco_461/surface.dat', 'surface.dat')
file = open ( 'surface.dat',"r" )
lineList = file.readlines()
file.close()
lastLine = lineList[-1]
time =  lastLine.split(" ; ")[5].strip( '\n' )
lat = lastLine.split(" ; ")[2]
lon = lastLine.split(" ; ")[3]
mission = lastLine.split(" ; ")[4]

#print lat,lon
ddlat = convertDecimalDegrees(lat)
ddlon = convertDecimalDegrees(lon)
#print ddlat,ddlon

with open("/root/gliders/slocum.csv", "a") as output:
    line = "%s,%s,%s,%s\n" %(time,ddlat,ddlon,mission)
    output.write(line)

update()
#session = ftplib.FTP('aegir.co.za','aegirtje','uA40qTWs2Brc')
#file = open('slocum.csv','rb')                  # file to send
#session.storbinary('STOR /public_html/glider/slocum.csv', file)     # send the file
#file.close()                                    # close file and FTP
#session.quit()

