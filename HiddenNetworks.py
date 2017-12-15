# Hidden Networks
# Python
# Eleven Paths / Telefonica
# Ver 0.1 Beta

import sys
import os
import socket
import json
import csv
import wmi
import matplotlib.pyplot as plt
import networkx as nx

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QMessageBox
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


#Local methods to read info from registry
#http://thejaswihr.blogspot.com.es/2008/10/python-windows-registry-access.html

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


def pathExists(hkey, regPath):
    try:
        reg = OpenKey(mapping[hkey], regPath)
    except WindowsError:
        return False
    CloseKey(reg)
    return True


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


   def AboutButton_clicked(self):
       msg = QtGui.QMessageBox()
       msg.setText("Eleven Paths \n Hidden Networks \n Ver 0.1b" )
       ret = msg.exec()
       return


   def DrawButtonSingleCSV_clicked(self):
       G = nx.Graph()
       usbiptocompare = []
       usbidtocompare = []
       usbnametocompare = []
       usbcnamecompare = []
       usbidcheck = []
       usbipcheck = []
       usbnamecheck = []
       usbcnamecheck = []
       a = 0
       b = 0
       c = 0
       singlecsvfile = QtGui.QFileDialog.getOpenFileName(self, 'Open single CSV File to plot')

       with open(singlecsvfile) as f:
           first_line=f.readline()

       datacsvfile=[]
       with open(singlecsvfile) as f:
           for row in csv.DictReader(f):
               datacsvfile.append(row)
       #datosjson=json.load(datacsvfile)

       csvhdheader="computer_name,computer_ip,usbdevice_name,usbdevice_id"

       if first_line.rstrip() != csvhdheader:
           msg = QtGui.QMessageBox()
           msg.setText("Error, file is not HD CSV")
           ret = msg.exec()

       datosjsondump=json.dumps(datacsvfile)
       datosjson=json.loads(datosjsondump)


       for item in datosjson:
           usbidtocompare.append(item.get("usbdevice_id"))
           usbiptocompare.append(item.get("computer_ip"))
           usbnametocompare.append(item.get("usbdevice_name"))
           usbcnamecompare.append(item.get("computer_name"))
       # Remove duplicates
       for i in usbidtocompare:
           if i not in usbidcheck:
               usbidcheck.append(i)
               usbipcheck.append(usbiptocompare[b])
               # usbipcheck.append(usbiptocompare[b])
               usbnamecheck.append(usbnametocompare[b])
               usbcnamecheck.append(usbcnamecompare[b])
               b = b + 1
           else:
               b = b + 1
       d = 0
       for idusb in usbidcheck:
           preusbipcomp = usbipcheck[d]
           preusbcomputername = usbcnamecheck[d]
           for item in datosjson:
               usbidcomp = item.get("usbdevice_id")
               usbipcomp = item.get("computer_ip")
               computername = item.get("computer_name")
               if usbidcomp == idusb:
                   listaprueba=[preusbipcomp,preusbcomputername]
                   nuevonodo='\n'.join(listaprueba)
                   listaprueba2=[usbipcomp, computername]
                   nuevonodo2='\n'.join(listaprueba2)
                   G.add_edge(nuevonodo, nuevonodo2)
                   #G.add_edge(preusbipcomp, usbipcomp)
                   # print(G.edges)
                   preusbipcomp = usbipcomp
                   preusbcomputername = computername
           d = d + 1

           # Graph plot
           pos = nx.shell_layout(G)
           options = {'node_size': 1500, 'node_color': 'c'}
           nx.draw(G, pos, edge_color='0.88', with_labels=True, **options)
           plt.gcf().canvas.set_window_title(usbnametocompare[c])
           plt.show()
           c = c + 1
           # G = nx.Graph()
           G = nx.Graph()



   def DrawButton_clicked(self):
       if self.projectopen:
           G=nx.Graph()
           usbiptocompare=[]
           usbidtocompare=[]
           usbnametocompare=[]
           usbcnamecompare=[]
           usbidcheck=[]
           usbipcheck=[]
           usbnamecheck=[]
           usbcnamecheck=[]
           a=0
           b=0
           c=0
           # ConvertCSV to JSON
           with open(self.classdatafilecsv) as f:
               reader = csv.DictReader(f)
               rows = list(reader)
           with open(self.classdatafilejson, 'w') as f:
               json.dump(rows, f)

           filejson = open(self.classdatafilejson, 'a')
           with open(self.classdatafilejson) as data_file:
               datosjson=json.load(data_file)

           #Retrieve usb devices id and ip
           for item in datosjson:
               usbidtocompare.append(item.get("usbdevice_id"))
               usbiptocompare.append(item.get("computer_ip"))
               usbnametocompare.append(item.get("usbdevice_name"))
               usbcnamecompare.append(item.get("computer_name"))

           #Remove duplicates
           for i in usbidtocompare:
               if i not in usbidcheck:
                  usbidcheck.append(i)
                  usbipcheck.append(usbiptocompare[b])
                  usbnamecheck.append(usbnametocompare[b])
                  usbcnamecheck.append(usbcnamecompare[b])
                  b=b+1

               else:
                  b=b+1

           d=0
           #Nodes
           for idusb in usbidcheck:
               preusbipcomp = usbipcheck[d]
               preusbcomputername = usbcnamecheck[d]

               for item in datosjson:
                   usbidcomp = item.get("usbdevice_id")
                   usbipcomp = item.get("computer_ip")
                   computername = item.get("computer_name")
                   if usbidcomp == idusb:

                       listaprueba = [preusbipcomp, preusbcomputername]
                       nuevonodo = '\n'.join(listaprueba)

                       listaprueba2 = [usbipcomp, computername]
                       nuevonodo2 = '\n'.join(listaprueba2)
                       G.add_edge(nuevonodo, nuevonodo2)
                       # G.add_edge(preusbipcomp, usbipcomp)
                       # print(G.edges)
                       preusbipcomp = usbipcomp
                       preusbcomputername = computername


               d=d+1

               #Graph plot
               pos = nx.shell_layout(G)
               options = {'node_size': 1500, 'node_color': 'c'}
               nx.draw(G, pos, edge_color='0.88',with_labels=True, **options)
               plt.gcf().canvas.set_window_title(usbnamecheck[c])
               plt.show()
               c = c + 1
               G=nx.Graph()
       else:
           msg=QtGui.QMessageBox()
           msg.setText("Please, open a Project first")
           ret=msg.exec()



   def LoadComputerListButton_clicked(self):
       opencomputerlistfilename = QtGui.QFileDialog.getOpenFileName(self, 'Open Computer List File')
       self.datafilecomputerlist=opencomputerlistfilename
       #print(self.datafilecomputerlist)
       self.ComputerFileListShow.setText(self.datafilecomputerlist)



   def GetRemoteRegistryWinRMButton_clicked(self):
       # Computer name or IP and username and password
       username=self.LoginUserInput.text()
       password=self.PasswordUserInput.text()
       computerlist = self.datafilecomputerlist

       if computerlist:
           with open(computerlist) as fp:
               #computers=fp.readlines()
               computers=fp.read().splitlines()
               #computers=[x.strip() for x in computers]
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
                           #print("Connection established")
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
                                   TempAllUSBData = computername, ip, usbdevicename, usbcontainerid
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
           onlyfilename=os.path.basename(os.path.normpath(newprojectfilename))
           datafilecsv = newprojectfilename + '/' + onlyfilename + '.csv'
           datafilejson = newprojectfilename + '/' + onlyfilename + '.json'
           projectfilename = onlyfilename+'.hn'
           filecsv = open(datafilecsv, 'w')
           # CSV file headers
           csvheader="computer_name","computer_ip","usbdevice_name","usbdevice_id"
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
               # Retrieving registry variables
               for i in range(numdispositivos):
                   registro2 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s" % dispositivos[i]
                   dispositivos2 = (readSubKeys(rama, registro2))
                   # Search id in file # C:\Windows\inf\setupapi.dev.log to find creation date
                   registro3 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\%s\%s" % (dispositivos[i], dispositivos2[0])
                   ValoresRamaUSB = (readValues(rama, registro3))
                   usbdevicename=ValoresRamaUSB['FriendlyName']
                   usbcontainerID=ValoresRamaUSB['ContainerID']
                   self.listWidgetLocalComputer.addItem(usbdevicename)
                   # csv
                   TempAllUSBData=computername,ipaddress,usbdevicename,usbcontainerID
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
