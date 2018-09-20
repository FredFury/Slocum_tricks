#!/usr/bin/env
# This script generates power plots for the slocum gliders

import io
import numpy
import urllib.request
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def getData():
    dataUrl = "https://raw.githubusercontent.com/FredFury/Slocum_tricks/master/slocum.csv"
    response = urllib.request.urlopen(dataUrl)
    csv = io.TextIOWrapper(response)
    dataTime = []
    dataVoltage = []
    dataCharge = []
    for row in csv:
        # Time
        # 20180918T185132
        dataTime.append(datetime.strptime(row.split(",")[2],"%Y%m%dT%H%M%S"))
        dataVoltage.append(float(row.split(",")[5]))
        dataCharge.append(float(row.split(",")[6]))
    return dataTime, dataVoltage, dataCharge

def plotData(dataT,dataVoltage,dataCharge):
    #print(dataT[0],dataVoltage[0])
    #print(dataT[-1],dataVoltage[-1])


    #Volage plot
    ###############################################
    ax = plt.axes()


    # Set up the X-axis
    plt.xticks(fontsize=6)
    plt.xlabel("TIME")

    #  Set up the Y-axis
    plt.ylim(top = 15, bottom = 9)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
    plt.ylabel("VOLTAGE")

    titleInfo = 'VOLTAGE OVER TIME'
    subTitle = "Last reading: " + str(round(dataVoltage[-1],2)) + "V"
    plt.suptitle(titleInfo,fontsize=18)
    plt.title(subTitle,fontsize=10)
    plt.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.plot(dataT,dataVoltage)
    # Add trendline
    #endDate =datetime.strptime("20181023T000000","%Y%m%dT%H%M%S")


    #plt.show()
    plt.savefig("/var/www/html/images/voltage.png")
    plt.clf()
    plt.cla()
    plt.close()

    #Charge plot
    ###############################################
    ax = plt.axes()
    # Set up the X-axis
    plt.xticks(fontsize=6)
    plt.xlabel("TIME")
    #  Set up the Y-axis
    plt.ylim(top = 100, bottom = 0)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
    plt.ylabel("CHARGE")
    titleInfo = 'CHARGE OVER TIME'
    subTitle = "Last reading: " + str(round(dataCharge[-1],2)) + "%"
    plt.suptitle(titleInfo,fontsize=18)
    plt.title(subTitle,fontsize=10)
    plt.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.plot(dataT,dataCharge,color='red')
    #plt.show()
    plt.savefig("/var/www/html/images/charge.png")

def main():
   # try:
   dataT,dataVoltage,dataCharge = getData()
   plotData(dataT,dataVoltage,dataCharge)

if __name__ == "__main__":
    main()
