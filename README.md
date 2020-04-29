# **HiddenNetworks-Python**
**v0.9** May 2020

<img src="https://github.com/ElevenPaths/HiddenNetworks-Python/blob/master/README_data/HiddenNetworks_Graph_USB.png" width="900">

**Hidden Networks** is a new concept test (based on the [paper](https://github.com/ElevenPaths/HiddenNetworks-Python/blob/master/whitepaper/HiddenNetworks_Paper.pdf) of the same name), that is programmed using Python 3.4. It facilitates the task of analysing local and remote machines (within a domain, using WMI) in searching for traces of connections by USB devices. With the information that is collected, this concept test draws a network that shows the path or jumps between such USB devices and the computers to which they have been connected. In this way, an alternative network is depicted. The same application will generate networks (one for each device) and all of the collected information is stored in two files (.CSV and .JSON) for subsequent analysis and exportation. 

<img src="https://github.com/ElevenPaths/HiddenNetworks-Python/blob/master/README_data/HiddenNetworks_NewFrontend.png" width="900">

**Functionality**: There are three main operations. The first is to extract information from a local machine from a list of computers on a network (domain) or directly draw the network from a previously generated CSV file. The main step before performing any of these operations (except the option of drawing a unique CSV) is to create or open a new project.

**Extract information from the local machine (“Get local registry info”)**. Information on the USB devices that are inserted       into the machine which is executing the application can be viewed or stored (if we select the option “Save output to CSV       file”) in the export files CSV and JSON. Finally, we can visualize the output network by selecting the option “Plot           Project”. 

**Extract information from machines on the network or Active Directory (“Retrieve remote info”)**. The step preceding this operation is to create a text file with the IP addresses of the computers to be audited or their FQDN. Once that list has been created, it must be loaded by selecting “Load list of computers”. Once the list has been loaded, the administrator’s username and password must be entered (the domain is not necessary; by default, the domain of the machine from which the application is being executed will be used). The state of execution and the extracted data will be shown in the window “Output”. This data will also be stored in the project’s CSV and JSON files. Finally, we can view the resulting network by selecting the option “Plot Project”.

**Draw the network with a CSV file (“Plot single CSV”)**. Through this option, the network generated through the application beforehand can be drawn directly.

<img src="https://github.com/ElevenPaths/HiddenNetworks-Python/blob/master/README_data/HiddenNetworks_GraphDetail.png" width="900">

**Reports**. PDF reports with all the information embeded about the USB drive and the graph generated.

**USB brand and model (visual)**. An image of the usb device is shown using the [bbid](https://github.com/ostrolucky/Bulk-Bing-Image-downloader) tool to search for it on the Internet. 


Thanks!

by IdeasLocas CDO Team.
