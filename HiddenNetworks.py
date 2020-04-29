# Hidden Networks
# Python 3
# Eleven Paths / Telefonica
# IdeasLocas CDO
# Ver 0.9 Beta

import sys
import os
import socket
import json
import csv
import wmi
import subprocess

import networkx as nx
import re

import matplotlib
matplotlib.use("Qt4Agg")
import matplotlib.patches as patches

import matplotlib.pyplot as plt

from google_images_download import google_images_download
from datetime import datetime
from smb.SMBConnection import SMBConnection
import time
from fpdf import FPDF

from PyQt4 import QtCore, QtGui, uic
from winreg import *

form_class = uic.loadUiType("HiddenGUI.ui")[0]

dispositivos = []
localdatamatrix = []
mapping = {"HKLM": HKEY_LOCAL_MACHINE, "HKCU": HKEY_CURRENT_USER, "HKU": HKEY_USERS}

# Data from project file
projectopen=False
projectname=''
projectpath=''
projectfilename=''
datafilecsv=''
datafilejson=''
datafilecomputerlist=''

# Bing Images Donwload by:
# https://github.com/ostrolucky/Bulk-Bing-Image-downloader

# Local methods to read info from registry
# http://thejaswihr.blogspot.com.es/2008/10/python-windows-registry-access.html

def readSubKeys(hkey, regPath):
    if not pathExists(hkey, regPath):
        return -1
    reg = OpenKey(mapping[hkey], regPath)
    subKeys = []
    noOfSubkeys = QueryInfoKey(reg)[0]
    for i in range(0, noOfSubkeys):
        subKeys.append(EnumKey(reg, i))
    CloseKey(reg)
    return subKeys

def readValues(hkey, regPath):
    if not pathExists(hkey, regPath):
        return -1
    reg = OpenKey(mapping[hkey], regPath)
    values = {}
    noOfValues = QueryInfoKey(reg)[1]
    for i in range(0, noOfValues):
        values[EnumValue(reg, i)[0]] = EnumValue(reg, i)[1]
    CloseKey(reg)
    return values

def convert_ipv4(ip):
    return tuple(int(n) for n in ip.split('.'))

def check_ipv4_in(addr, start, end):
    return convert_ipv4(start) < convert_ipv4(addr) < convert_ipv4(end)

def pathExists(hkey, regPath):
    try:
        reg = OpenKey(mapping[hkey], regPath)
    except WindowsError:
        return False
    CloseKey(reg)
    return True

def usbfirstconnectlocal(usbserial):
    # Retrieve a string with date and time of the USB firs plug
    # Data located at C:\Windows\inf\setupapi.dev.log
    array_dates=[]
    array_time=[]
    a=0
    devlogfile = open("C:\Windows\inf\setupapi.dev.log", "r")

    for line in devlogfile:
        if re.search(usbserial, line):
            line=next(devlogfile)
            # Split text string to retrieve date and time
            for word in line.split():
                if word.find(':')!=-1: # time
                    array_time.append(word)
                else:
                    array_dates.append(word)

            array_dates.remove('>>>')
            array_dates.remove('Section')
            array_dates.remove('start')

    # lower date
    mindate=min(array_dates)
    mintime= min(array_time)
    devlogfile.close()
    return (mindate,mintime)


def usbfirstconnectremote(usbserial,remotecompname,remoteuser, remotepassword):
    array_dates = []
    array_time = []
    a = 0
    data_folder="C$"
    conn=SMBConnection(remoteuser, remotepassword, "hn", remotecompname,use_ntlm_v2 = True,domain='testdomain')
    conn.connect(remotecompname,139)

    with open('tempohn.tmp','wb') as devlogfile:
        conn.retrieveFile(data_folder, '\Windows\inf\setupapi.dev.log', devlogfile)

        print("CONECTADO")
    print("USBSERIAL:", usbserial)

    devlogfile = open("tempohn.tmp", 'r')

    for line in devlogfile:
        if re.search(usbserial, line):
            line=next(devlogfile)
            # Split text strings to retrive date and time
            for word in line.split():
                if word.find(':')!=-1: # time
                    array_time.append(word)
                    #print(array_time)
                else:
                    array_dates.append(word)

            array_dates.remove('>>>')
            array_dates.remove('Section')
            array_dates.remove('start')

    mindate = min(array_dates)
    mintime = min(array_time)

    devlogfile.close()
    return (mindate, mintime)

# Class definition
class MyWindowClass(QtGui.QMainWindow, form_class):

   def __init__(self, parent=None):
      QtGui.QMainWindow.__init__(self, parent)
      self.setupUi(self)
      self.NewProjectButton.clicked.connect(self.NewProjectButton_clicked)
      self.OpenProjectButton.clicked.connect(self.OpenProjectButton_clicked)
      self.GetLocalRegistryButton.clicked.connect(self.GetLocalRegistryButton_clicked)
      self.ExitButton.clicked.connect(self.ExitButton_clicked)
      self.LoadComputerListButton.clicked.connect(self.LoadComputerListButton_clicked)
      self.GetRemoteRegistryWinRMButton.clicked.connect(self.GetRemoteRegistryWinRMButton_clicked)
      self.DrawButton.clicked.connect(self.DrawButton_clicked)
      self.DrawButtonSingleCSV.clicked.connect(self.DrawButtonSingleCSV_clicked)
      self.AboutButton.clicked.connect(self.AboutButton_clicked)
      self.radioButtonSaveCSV.setChecked(False)

      self.projectopen = False
      self.classprojectname = ''
      self.classprojectpath = ''
      self.classprojectfilename = ''
      self.classdatafilecsv = ''
      self.classdatafilejson = ''
      self.datafilecomputerlist=''
      self.drawcsv = True

   def AboutButton_clicked(self):
       msg = QtGui.QMessageBox()
       msg.setText("Ideas Locas & Eleven Paths \n Hidden Networks \n March 2020 Ver 0.9b" )
       ret = msg.exec()
       return

   def DrawButtonSingleCSV_clicked(self):

       #G = nx.DiGraph()
       usbiptocompare = []
       usbidtocompare = []
       usbnametocompare = []
       usbcnamecompare = []
       usbidcheck = []
       usbipcheck = []
       usbnamecheck = []
       usbcnamecheck = []

       #dates
       usbdatecheck = []
       usbtimecheck = []
       usbfirstplugdatecompare = []
       usbfirstplugtimecompare = []

       a = 0
       b = 0
       c = 0

       if self.projectopen and self.drawcsv == False:
           singlecsvfile = self.classdatafilecsv
       else:
           singlecsvfile = QtGui.QFileDialog.getOpenFileName(self, 'Open single CSV File to plot')

       with open(singlecsvfile) as f:
           first_line=f.readline()

       self.drawcsv = True

       datacsvfile=[]
       with open(singlecsvfile) as f:
           for row in csv.DictReader(f):
               datacsvfile.append(row)

       self.listWidgetRemoteOutput.addItem("Processing data from CSV file ... please wait ...")
       self.listWidgetRemoteOutput.addItem("Click on usb picture to proceed to the next plot")

       QtGui.QApplication.processEvents()

       csvhdheader="computer_name,computer_ip,usbdevice_name,usbdevice_id,usb_firstplugdate,usb_firstplugtime"


       if first_line.rstrip() != csvhdheader:
           msg = QtGui.QMessageBox()
           msg.setText("Error, file is not HD CSV")
           ret = msg.exec()

       datosjsondump=json.dumps(datacsvfile)
       datosjsonraw=json.loads(datosjsondump)

       datosjson = sorted(datosjsonraw, key=lambda k: datetime.strptime(k['usb_firstplugdate'],"%Y/%m/%d"), reverse=False)

       for item in datosjson:
           usbidtocompare.append(item.get("usbdevice_id"))
           usbiptocompare.append(item.get("computer_ip"))
           usbnametocompare.append(item.get("usbdevice_name"))
           usbcnamecompare.append(item.get("computer_name"))
           usbfirstplugdatecompare.append(item.get("usb_firstplugdate"))
           usbfirstplugtimecompare.append(item.get("usb_firstplugtime"))

       # Remove duplicates
       for i in usbidtocompare:
           if i not in usbidcheck:
               usbidcheck.append(i)
               usbipcheck.append(usbiptocompare[b])
               usbnamecheck.append(usbnametocompare[b])
               usbcnamecheck.append(usbcnamecompare[b])
               #dates
               usbdatecheck.append(usbfirstplugdatecompare[b])
               usbtimecheck.append(usbfirstplugtimecompare[b])

               b = b + 1
           else:
               b = b + 1

       d = 0
       n = 0


       for idusb in usbidcheck:

           G = nx.DiGraph()
           testArrow = matplotlib.patches.ArrowStyle.Fancy(head_length=.4, head_width=.4, tail_width=.1)
           pathrepo = os.path.dirname(os.path.realpath(__file__)) + "\\reports\\"
           timestr = time.strftime("%Y%m%d-%H%M%S")

           preusbipcomp = usbipcheck[d]
           preusbcomputername = usbcnamecheck[d]
           #dates
           preusbdate = usbdatecheck[d]
           preusbtime = usbtimecheck[d]

           # PDF
           pdf = FPDF()
           pdf.add_page()
           pdf.set_font('Arial', 'B', 20)
           pdf.cell(110, 10, 'Hidden Networks USB Report', 1, 1)
           pdf.set_font('Arial', 'B', 15)
           pdf.cell(30, 10, 'USB Name: ' + usbnamecheck[c], 0, 1)
           pdf.cell(30, 10, 'USB id: ' + idusb, 0, 1)
           pdf.cell(30, 15, 'Tracking: ', 0, 1)

           for item in datosjson:
               usbidcomp = item.get("usbdevice_id")
               usbipcomp = item.get("computer_ip")
               computername = item.get("computer_name")
               #date
               usbdate = item.get("usb_firstplugdate")
               usbtime = item.get("usb_firstplugtime")

               if usbidcomp == idusb:
                   #PDF
                   pdf.set_font('Arial', '', 8)
                   pdf.cell(0, 5, 'Connected to: '+computername, 0, 2)
                   pdf.cell(0, 5, 'IP: ' + usbipcomp, 0, 2)
                   pdf.cell(0, 5, 'Date: '+usbdate+' Time: '+usbtime, 0, 2)
                   pdf.cell(0, 10, '--->', 0, 2)

                   listaprueba = [preusbipcomp, preusbcomputername, preusbdate, preusbtime]
                   nuevonodo='\n'.join(listaprueba)

                   listaprueba2=[usbipcomp, computername, usbdate, usbtime]
                   nuevonodo2='\n'.join(listaprueba2)
                   G.add_edge(nuevonodo, nuevonodo2)

                   preusbipcomp = usbipcomp
                   preusbcomputername = computername
                   preusbdate = usbdate
                   preusbtime = usbtime
           d = d + 1

           self.listWidgetRemoteOutput.addItem(usbnamecheck[c])
           QtGui.QApplication.processEvents()

           # Graph plot
           #pos = nx.shell_layout(G)
           pos = nx.circular_layout(G, center=(0, 0))

           #Nodes / computers
           num_nodes = G.number_of_nodes()
           list_nodes = list(G.nodes)

           color_map=[]
           a=0
           # Insolated or connected (IP)
           for node in G:
                if list_nodes[a][0]=='\n':
                   color_map.append('lightsalmon')
                else:
                   color_map.append('skyblue')
                a=a+1

           options = {
               'font_size': '7',
               'node_shape': 'o',
               'node_size': 3000,
               'width': 2,
               'arrowstyle': testArrow,
               'arrowsize': 12,
           }

           nx.draw(G, pos, alpha=0.7, node_color=color_map, edge_color='gray', arrows=True, with_labels=True, **options)
           plt.axis("off")
           plt.gcf().canvas.set_window_title(usbnamecheck[c])
           plt.savefig(pathrepo+idusb+timestr+'.png')

           #pdf.add_page()
           pdf.image(pathrepo+idusb+timestr+'.png', 80, 50 ,120)

           #plt.show(nx)

           # Shows  image in new window as subplot
           localrunpath=os.path.dirname(os.path.realpath(__file__))
           print(localrunpath)
           path = localrunpath+"\\images\\{0}".format(usbnamecheck[c])

           if not os.path.exists(path):
               os.makedirs(path)

           bbid_run="bbid.py -s \"{0}\" -o \"{1}\" --limit 3".format(usbnamecheck[c],path)

           try:
               os.system(bbid_run)
               print("Ejecutando ...")
               #subprocess.call([bbid_run])
               usb_image_path = os.listdir(path)[0]
               usb_image_full_path = path + "\\" + usb_image_path
           except:
               print("No Internet ERROR ...")
               usb_image_full_path = localrunpath + "\\" + "notfound.jpg"


           fig, (ax) = plt.subplots()
           #fig.canvas.set_window_title(usbnamecheck[c])

           ax.imshow(plt.imread(usb_image_full_path, ))

           ax.text(0.95, 0.01, idusb,
                   verticalalignment='bottom', horizontalalignment='right',
                   transform=ax.transAxes,
                   color='gray', fontsize=15)

           plt.axis("off")
           n=n+1


           win = plt.gcf().canvas.manager.window
           win.setWindowFlags(win.windowFlags() | QtCore.Qt.CustomizeWindowHint)
           win.setWindowFlags(win.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)

           # PDF
           pdf.image(usb_image_full_path, 90, 150 ,100)

           # Save PDF Report file
           pdf.output(pathrepo + idusb + timestr + '.pdf', 'F')

           plt.show()
           plt.waitforbuttonpress()
           plt.close('all')

           c = c + 1

       self.listWidgetRemoteOutput.addItem("Finished!")
       QtGui.QApplication.processEvents()


   def DrawButton_clicked(self):
       if self.projectopen:
           # ConvertCSV to JSON
           with open(self.classdatafilecsv) as f:
               reader = csv.DictReader(f)
               rows = list(reader)
           with open(self.classdatafilejson, 'w') as f:
               json.dump(rows, f)
           self.drawcsv=False
           self.DrawButtonSingleCSV_clicked()
       else:
           msg=QtGui.QMessageBox()
           msg.setText("Please, open a Project first")
           ret=msg.exec()

       self.listWidgetRemoteOutput.addItem("Finished!")
       QtGui.QApplication.processEvents()



   def LoadComputerListButton_clicked(self):
       opencomputerlistfilename = QtGui.QFileDialog.getOpenFileName(self, 'Open Computer List File')
       self.datafilecomputerlist=opencomputerlistfilename
       self.ComputerFileListShow.setText(self.datafilecomputerlist)



   def GetRemoteRegistryWinRMButton_clicked(self):
       # Computer name or IP and username and password
       username=self.LoginUserInput.text()
       password=self.PasswordUserInput.text()
       computerlist = self.datafilecomputerlist

       if computerlist:
           with open(computerlist) as fp:
               computers=fp.read().splitlines()

       else:
           msg = QtGui.QMessageBox()
           msg.setText("Please, choose a server list file")
           ret = msg.exec()
           return

       numcomputers=len(computers)

       self.listWidgetRemoteOutput.setUpdatesEnabled(True)
       for i in range(numcomputers):
           if computers is not None:
               ip=computers[i]
               self.listWidgetRemoteOutput.addItem("Retrieving data from %s , please wait ..." % ip)
               QtGui.QApplication.processEvents()
               if not username:
                   msg = QtGui.QMessageBox()
                   msg.setText("Please, type user credentials")
                   ret = msg.exec()
               else:
                   if self.projectopen:
                       filecsv = open(self.classdatafilecsv, 'a')
                       try:
                           c = wmi.WMI(ip, user=username, password=password).StdRegProv
                           self.listWidgetRemoteOutput.addItem("Connection established ...")
                           result, names = c.EnumKey(hDefKey=HKEY_LOCAL_MACHINE,sSubKeyName=r"SYSTEM\CurrentControlSet\Enum\USBSTOR")
                           numdevices=len(names)
                           # Check if IP or computername
                           try:
                               socket.inet_aton(ip)
                               tempcname=socket.gethostbyaddr(ip)
                               computername=tempcname[0]
                           except socket.error:
                               computername=ip
                           if numdevices is not 0:
                               filecsv = open(self.classdatafilecsv, 'a')
                               for i in range(numdevices):
                                   remotereg1=c.EnumKey(hDefKey=HKEY_LOCAL_MACHINE,sSubKeyName=r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s" % names[i])
                                   test1=remotereg1[1]
                                   finalbranch=test1.pop(0)

                                   result,friendly=c.GetStringValue(hDefKey=HKEY_LOCAL_MACHINE,sSubKeyName=r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s\%s" % (names[i], finalbranch),sValueName="FriendlyName")
                                   usbdevicename=friendly
                                   result2,usbid=c.GetStringValue(hDefKey=HKEY_LOCAL_MACHINE,sSubKeyName=r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s\%s" % (names[i], finalbranch),sValueName="ContainerID")
                                   usbcontainerid=usbid
                                   usbserial=finalbranch

                                   #Retrieve date and time first plug in remote computer
                                   mindatefirstplug, mintimefirstplug = usbfirstconnectremote(usbserial,computername,username,password)
                                   #print("FECHA MENOR DEVUELTA: ", mindatefirstplug)
                                   #print("HORA MENOR DEVUELTA: ", mintimefirstplug)

                                   TempAllUSBData = computername, ip, usbdevicename, usbserial,mindatefirstplug,mintimefirstplug
                                   AllUSBData = ','.join(TempAllUSBData)
                                   self.listWidgetRemoteOutput.addItem(AllUSBData)
                                   filecsv.write(AllUSBData)
                                   filecsv.write('\n')
                               filecsv.close()
                               QtGui.QApplication.processEvents()
                               # Convert to JSON
                               with open(self.classdatafilecsv) as f:
                                  reader = csv.DictReader(f)
                                  rows = list(reader)
                               with open(self.classdatafilejson, 'w') as f:
                                  json.dump(rows, f)
                           else:
                               msg = QtGui.QMessageBox()
                               msg.setText("No USB found at")
                               ret = msg.exec()
                       except wmi.x_wmi:
                           msg = QtGui.QMessageBox()
                           msg.setText("Wrong credentials")
                           ret = msg.exec()
                   else:
                       msg=QtGui.QMessageBox()
                       msg.setText("Please, open a Project first")
                       ret=msg.exec()
           else:
                msg = QtGui.QMessageBox()
                msg.setText("Please, choose a server list file")
                ret = msg.exec()
       self.listWidgetRemoteOutput.addItem("Finished!")
       QtGui.QApplication.processEvents()



   def NewProjectButton_clicked(self):
       pname, ok = QtGui.QInputDialog.getText(self, 'New Project', 'Enter project name:')
       newprojectfilename=QtGui.QFileDialog.getSaveFileName(self, 'Save File')

       file=open(newprojectfilename+'.hn','w')
       file.write('%HNF')
       file.write('\n')
       file.write(pname)
       file.write('\n')
       file.write(newprojectfilename)
       file.write('\n')
       file.write(newprojectfilename+'.hn')
       # CSV and JSON base files
       if not os.path.exists(newprojectfilename):
           os.makedirs(newprojectfilename)
           os.makedirs(newprojectfilename + '/' + 'reports' )
           onlyfilename=os.path.basename(os.path.normpath(newprojectfilename))
           datafilecsv = newprojectfilename + '/' + onlyfilename + '.csv'
           datafilejson = newprojectfilename + '/' + onlyfilename + '.json'
           projectfilename = onlyfilename+'.hn'
           filecsv = open(datafilecsv, 'w')
           # CSV file headers
           csvheader="computer_name","computer_ip","usbdevice_name","usbdevice_id","usb_firstplugdate","usb_firstplugtime"
           allcsvheader=','.join(csvheader)
           filecsv.write(allcsvheader)
           filecsv.write('\n')
           filejson = open(datafilejson,'w')
           filecsv.close()
           filejson.close()
          # Set new project active
           projectname = pname
           #projectpath = datafile[2]
           projectfilename = newprojectfilename
           datafilecsv = datafilecsv
           datafilejson = datafilejson
           self.ShowCurrentProject.setText(projectname)
           self.ProjectFileNameText.setText(projectfilename)
           self.ProjectCSVFileNameText.setText(datafilecsv)
           self.ProjectJSONFileNameText.setText(datafilejson)
           self.projectopen = True
           self.classprojectfilename=projectfilename
           #self.classprojectname=projectname
           self.classdatafilecsv=datafilecsv
           self.classdatafilejson=datafilejson
       file.write('\n')
       file.write(datafilecsv)
       file.write('\n')
       file.write(datafilejson)
       file.close()



   def OpenProjectButton_clicked(self):
       openprojectfilename=QtGui.QFileDialog.getOpenFileName(self, 'Open File')
       with open(openprojectfilename) as f:
           datafile=f.readlines()
       datafile=[x.strip() for x in datafile]
       isfileHN = datafile[0]

       if isfileHN =="%HNF":
           projectname = datafile[1]
           projectpath = datafile[2]
           projectfilename = datafile[3]
           datafilecsv = datafile[4]
           datafilejson = datafile[5]
           self.ShowCurrentProject.setText(projectname)
           self.ProjectFileNameText.setText(projectfilename)
           self.ProjectCSVFileNameText.setText(datafilecsv)
           self.ProjectJSONFileNameText.setText(datafilejson)
           self.projectopen = True
           self.classprojectfilename=projectfilename
           #self.classprojectname=projectname
           self.classdatafilecsv=datafilecsv
           self.classdatafilejson=datafilejson
       else:
           msg = QtGui.QMessageBox()
           msg.setText("File is not a Hidden Network Project File")
           ret = msg.exec()


   def GetLocalRegistryButton_clicked(self):
       if self.projectopen:
           rama = "HKLM"
           registro = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
           dispositivos = (readSubKeys(rama, registro))
           numdispositivos = len(dispositivos)
           QtGui.QApplication.processEvents()
           # Computer general data
           computername=socket.gethostname()
           ipaddress=socket.gethostbyname(computername)
           self.ComputerNameText.setText(computername)
           self.USBDetectedText.setText(str(numdispositivos))
           # Computer registry local data
           if numdispositivos is not 0 and self.radioButtonSaveCSV.isChecked() == True:
               filecsv = open(self.classdatafilecsv, 'a')
               devlogfile = open("C:\Windows\inf\setupapi.dev.log", "r")
               # Retrieving registry variables
               for i in range(numdispositivos):
                   registro2 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s" % dispositivos[i]
                   dispositivos2 = (readSubKeys(rama, registro2))
                   # Search id in file # C:\Windows\inf\setupapi.dev.log to find creation date
                   registro3 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s\%s" % (dispositivos[i], dispositivos2[0])
                   ValoresRamaUSB = (readValues(rama, registro3))
                   usbdevicename=ValoresRamaUSB['FriendlyName']
                   usbcontainerID=ValoresRamaUSB['ContainerID']
                   usbserialnumber=dispositivos2[0]
                   #print("SERIALN ",usbserialnumber)
                   mindatefirstplug,mintimefirstplug=usbfirstconnectlocal(usbserialnumber)
                   #print("FECHA MENOR DEVUELTA: ", mindatefirstplug)
                   #print("HORA MENOR DEVUELTA: ", mintimefirstplug)
                   self.listWidgetLocalComputer.addItem(usbdevicename)
                   # csv
                   TempAllUSBData=computername,ipaddress,usbdevicename,usbserialnumber,mindatefirstplug,mintimefirstplug
                   AllUSBData=','.join(TempAllUSBData)
                   filecsv.write(AllUSBData)
                   filecsv.write('\n')

               filecsv.close()
               # Convert to JSON
               with open(self.classdatafilecsv) as f:
                   reader=csv.DictReader(f)
                   rows=list(reader)
               with open(self.classdatafilejson,'w') as f:
                   json.dump(rows,f)
           elif numdispositivos is not 0 and self.radioButtonSaveCSV.isChecked() == False:
               for i in range(numdispositivos):
                   registro2 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s" % dispositivos[i]
                   dispositivos2 = (readSubKeys(rama, registro2))
                   registro3 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s\%s" % (dispositivos[i], dispositivos2[0])
                   ValoresRamaUSB = (readValues(rama, registro3))
                   usbdevicename=ValoresRamaUSB['FriendlyName']
                   self.listWidgetLocalComputer.addItem(usbdevicename)

           else:
               msg = QtGui.QMessageBox()
               msg.setText("No USB found")
               ret = msg.exec()
       else:
           msg=QtGui.QMessageBox()
           msg.setText("Please, open a Project first")
           ret=msg.exec()


   def ExitButton_clicked(self):
      sys.exit()

def main():
    # Main function
    app = QtGui.QApplication(sys.argv)
    MyWindow = MyWindowClass(None)
    MyWindow.setWindowTitle('Hidden Networks')
    MyWindow.setWindowIcon(QtGui.QIcon('HNLogo.png'))

    MyWindow.show()
    app.exec_()

if __name__== "__main__":
    main()
