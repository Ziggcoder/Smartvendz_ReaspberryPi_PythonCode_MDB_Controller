import serial,io
import time
import argparse,sys,os
import os
import requests
import netifaces as ni
from subprocess import check_output
import datetime

thisdict = {
  "0":"A1","1":"A2","2":"A3","3":"A4","4":"A5","5":"A6","6":"A7","7":"A8","8":"A9","9":"A10",
  "256":"B1","257":"B2","258":"B3","259":"B4","260":"B5","261":"B6","262":"B7","263":"B8","264":"B9","265":"B10",
  "512":"C1","513":"C2","514":"C3","515":"C4","516":"C5","517":"C6","518":"C7","519":"C8","520":"C9","521":"C10",
  "768":"D1","769":"D2","770":"D3","771":"D4","772":"D5","773":"D6","774":"D7","775":"D8","776":"D9","777":"D10",
  "1024":"E1","1025":"E2","1026":"E3","1027":"E4","1028":"E5","1029":"E6","1030":"E7","1031":"E8","1032":"E9","1033":"E10",
  "1280":"F1","1281":"F2","1282":"F3","1283":"F4","1284":"F5","1285":"F6","1286":"F7","1287":"F8","1288":"F9","1289":"F10",
}


def initserial():
    global sio
    global ser
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.timeout = 1
    #ser.port = args.port  # choose USB PORT - default=/dev/ttyACM0
    ser.port ='/dev/ttyS0'
    ser.open()  # open serial comunication
    time.sleep(1)  # wait for serial comunication to be established
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    return ser
      # pass the handler

def initusbserial():
    global usbsio
    global usbser
    usbser = serial.Serial()
    usbser.baudrate = 9600
    usbser.timeout = 1
    #ser.port = args.port  # choose USB PORT - default=/dev/ttyACM0
    usbser.port ='/dev/ttyUSB0'
    usbser.open()  # open serial comunication
    time.sleep(1)  # wait for serial comunication to be established
    usbsio = io.TextIOWrapper(io.BufferedRWPair(usbser, usbser))
    return usbser
      # pass the handler

def readNWaitUSB():
    global usbsio
    usbsio.flush()
    for i in range(5): #wait for 500 msecs
        usbsio.flush()
        buf = '\0'
        buf = usbsio.readline()
        #if debug:
        print("Read Card Data: " + buf + "\n")
        if len(buf)>0:  
            break
        else:
            print("...")
            time.sleep(0.1)       
    #print("Read: " + buf + "\n")
    return buf

def readNWait():
    global sio
    for i in range(5): #wait for 500 msecs
        sio.flush()
        buf = '\0'
        buf = sio.readline()
        #if debug:
        #print("Read: " + buf + "\n")
        if len(buf)>0:  
            break
        else:
            print("...")
            time.sleep(0.1)      
    #print("Read: " + buf + "\n")
    return buf

def write2Serial(message):
    sio.write(message + "\n")
    sio.flush()
    #if debug:
    print("Send: " + message + "\n")

def readCardData():
    rloop=True
    while rloop:
       carddata=readNWaitUSB()
       print(carddata)
       print(len(carddata))
       if (len(carddata))>0:
            return carddata
            break

def checkConn():
    retry=0
    conn=0
    try:
       response=requests.get("http://13.233.20.108:80",timeout=5)
       print("Internet Connected")
       conn=1
    except requests.exceptions.RequestException as e:
        #print(e)
        print("Internet not Connected")
        retry+=1
        if(retry>10):
            conn=0
    return conn

#Main Part Starts Here.......

if __name__ == '__main__':
  
    ser = initserial()
    usbser = initusbserial()
    vendCycle=0
    productWaitCycle=0
    productSelectAttempt=0
    idelstatus=0
    cBuf=0
    cData=0
    vCommand=""    
    vProduct=""
    sCardData=""
    sProduct=""
    sBuf=1
    card_no=""
    item=""
    machine = "SVZBLR0099"
    machineDate=""
    machineTime=""
    apiurl="http://smartvendz.com/credit/snaxsmart/"

    if  ser.is_open:
        while True:

            blankresponse=0
            print("sBuf:"+ str(sBuf))
            print("sBuf:"+ str(cBuf))


            if not sBuf:  
               if vCommand=="C,START,500,1":
                   print("*"*20)
                   print("vCommand="+vCommand)
                   print("*"*20)
                   if not vendCycle==0:
                       print("Stop Previous Cycle start New Vending")
                       write2Serial('C,STOP')
                       time.sleep(0.1)
                       data=readNWait()
                       print("Read data before after stop command before credit"+data)
                       time.sleep(0.1)
                       vendCycle=1
                       sBuf=1
                       cBuf=1
                       write2Serial(vCommand)
                       vCommand=""
                       data=readNWait()
                       
                       if not (data.find("c,STATUS,IDLE,500,1")==-1):
                           data=readNWait()
                           print("Read: " + data + "\n")
                           if (data.find("r,ACK")==-1):
                               time.sleep(0.)
                               data=readNWait()
                               print("Read: " + data + "\n")
                               if (data.find("r,ACK")==-1): 
                                    write2Serial("C,STOP")
                               else:    
                                    productWaitCycle=0
                                    idelstatus=1
                           else:    
                                productWaitCycle=0
                                idelstatus=1       
                   else:
                       
                       card_raw_data=readCardData()
                       print("*"*40)
                       print("card no is"+card_raw_data)
                       vArr=card_raw_data.split(" ")
                       print("*"*60)
                       print(vArr[0])
                       if (vArr[0]=="37"):
                            print(vArr[2])
                            binary_data=bin(int(str(vArr[2]), 16))[2:].zfill(37)
                            #int_value = int(hex_value, base=16)
                            print(binary_data)
                            print(binary_data[0:5]+" "+binary_data[5:37])
                            BC1=(str(binary_data[5:37])+str(binary_data[0:5]))
                            print(BC1)
                            BC2=BC1[17:36]
                            BC2=int(BC2, 2)
                            print(BC2)
                            card_no=BC2
                       elif(vArr[0]=="26"):
                            print(vArr[2])
                            binary_data=bin(int(str(vArr[2]), 16))[2:].zfill(26)
                            print(binary_data)
                            BC2=binary_data[8:25]
                            BC2=int(BC2, 2)
                            print(BC2)
                            card_no=BC2
                       elif(vArr[0]=="35"):
                            print(vArr[2])
                            hex_data=int(str(vArr[2]), 16)
                            print(hex_data)
                            binary_data=bin(int(str(vArr[2]), 16))[2:].zfill(35)
                            print(binary_data)
                            print(binary_data)
                            BC1=binary_data[0:3]
                            BC2=binary_data[3:35]
                            print(BC1)
                            print(BC2)
                            BC2=int(BC2, 2)
                            BC1=int(BC1, 2)
                            print(BC1)
                            print(BC2)
                            BC2 = BC2 & 0xFFFFF
                            print(BC2)
                            BC2 <<= 2
                            print(BC2)
                            BC1 &= 0x6
                            print(BC1)
                            BC1 >>=1
                            print(BC1)
                            BC2|=BC1
                            BC2&= 0xFFFFF
                            print(BC2)
                            card_no=BC2     
                       else:
                            card_no=(int(str(vArr[2]), 16))
                       print("New Cycle start vending")
                       vendCycle=1
                       sBuf=1
                       cBuf=1
                       write2Serial(vCommand)
                       vCommand=""
                       data=readNWait()
                       if not (data.find("c,STATUS,IDLE,500,1")==-1):
                           data=readNWait()
                           print("Read: " + data + "\n")
                           if (data.find("r,ACK")==-1):
                               time.sleep(0.1)
                               data=readNWait()
                               print("Read: " + data + "\n")
                               if (data.find("r,ACK")==-1): 
                                    write2Serial("C,STOP")
                               else:    
                                    productWaitCycle=0
                                    idelstatus=1
                           else:    
                              productWaitCycle=0
                              idelstatus=1        
                
               if vCommand=="C,VEND,1":
                  print("*"*20)
                  print("vCommand="+vCommand)
                  print("*"*20)
                  vArr=vProduct.split(",")
                  #item=vArr[4]
                  item=(thisdict[(vArr[4]).rstrip("\n")])
                  print("Selected Product is: "+vArr[4])
                  x = datetime.datetime.now()
                  machineDate=x.strftime("%x")
                  machineTime=x.strftime("%X")
                  getreq=apiurl+str(machine)+"?card="+str(card_no)+"&item="+str(item)+"&date="+str(machineDate)+"&time="+str(machineTime)+"&serial=107&status=Rejected&price=14.4"
                  # Making a get request
                  print(getreq)
                  response=""
                  #############################################
                  try:
                    response = requests.get(getreq)
                    print(response.text)
                    if not (response.text.find("success")==-1):
                        time.sleep(0.1)
                        write2Serial(vCommand)
                        sBuf=1
                        cBuf=1
                        vCommand=""
                    if not (response.text.find("fail")==-1):
                        time.sleep(0.1)
                        write2Serial("C,VEND,-1")
                        data=readNWait()
                        if not (data.find('r,ACK')==-1):
                          vendCycle=0
                          card_no=""
                          sBuf=1
                          cBuf=1
                          vCommand=""
                  except requests.exceptions.RequestException as e:
                      print(e)
                      vendCycle=0
                      card_no=""
                      vCommand=""
                      idelstatus=0
                      productSelectAttempt=0
                      productWaitCycle=0
                      write2Serial("C,STOP")
                      sBuf=1
                      cBuf=0
                  #############################################



               if vCommand=="C,1":
                  print("*"*20)
                  print("vCommand="+vCommand)
                  print("*"*20)
                  time.sleep(0.1)
                  sBuf=1
                  cBuf=1
                  write2Serial(vCommand)
                  vCommand=""
                  
               if vCommand=="C,VEND,-1":
                  print("*"*20)
                  print("vCommand="+vCommand)
                  print("*"*20)
                  time.sleep(0.1)
                  sBuf=1
                  cBuf=1
                  vCommand=""
               if vCommand=="C,STOP":
                  print("*"*20)
                  print("vCommand="+vCommand)
                  print("*"*20)
                  time.sleep(0.1)
                  sBuf=1
                  cBuf=1
                  write2Serial(vCommand)
                  vCommand=""
               if vCommand=="C,0":
                  print("*"*20)
                  print("vCommand="+vCommand)
                  print("*"*20)
                  time.sleep(0.1)
                  sBuf=1
                  cBuf=1
                  write2Serial(vCommand)
                  vCommand=""


               
              











            if not cBuf:
               print("Restarting.....")
               ips = check_output(['hostname', '--all-ip-addresses'])
               ip= str(ips.decode())
               if (len(ip)<=1):
                   print("IP not found: May be Ethernet cable is not found")
                   conn=checkConn()
                   cBuf=0
                   cData=1
               else:
                   print(len(ip))
                   print("IP address ="+ips.decode())
                   print(ips.decode())
                   conn=checkConn()
                   if conn==1:
                      write2Serial("C,0")
                      time.sleep(0.1) 
                      write2Serial("C,1")
                      cBuf=1
                      cData=0
                   else:
                      cData=1
                      cBuf=0
                      sBuf=1
  









            print("cData="+str(cData))
            if cData==1:
                data=""
            else:    
               data=readNWait()
            print("Read: " + data + "\n")
            if (data.find('r,')==-1):
                print("Read: " + data + "\n")
                if not (data.find('c,ERR,"cashless is on"')==-1):
                   print("Device ready to vend")
                   vCommand="C,START,500,1"
                   sBuf=0
                   cBuf=0
                   
                if not (data.find('c,ERR,"cashless is off"')==-1):
                   print("Device is not ready need to enable")
                   vCommand="C,1"
                   sBuf=0
                   cBuf=0
                if not (data.find('c,STATUS,ENABLED')==-1):
                   print("Device ready to vend")
                   vCommand="C,START,500,1"
                   sBuf=0
                   cBuf=0
                  
                if not (data.find('c,STATUS,VEND,')==-1):
                   productWaitCycle=0
                   idelstatus=0
                   print("Product selected:")
                   vProduct=data
                   vCommand="C,VEND,1"
                   sBuf=0
                   cBuf=0
                if not (data.find('c,VEND,SUCCESS')==-1):
                   print("vending Successfull:"+vProduct)
                   ackreq=apiurl+str(machine)+"?VEND,SUCCESS,10.00,5"
                   # Making a get request
                   print(ackreq)
                   response=""
                   #############################################
                   try:
                     response = requests.get(ackreq,timeout=5)
                     print(response.text)
                     vendCycle=0
                     card_no=""
                   except requests.exceptions.RequestException as e:
                      print(e)
                      vendCycle=0
                      card_no=""
                      vCommand=""
                      idelstatus=0
                      productSelectAttempt=0
                      productWaitCycle=0
                      write2Serial("C,STOP")
                      sBuf=1
                      cBuf=0
                if not (data.find("c,STATUS,IDLE,500,1")==-1):
                    time.sleep(0.1)
                    data=readNWait()
                    print("Read: " + data + "\n")
                    if (data.find("r,ACK")==-1):
                        time.sleep(0.1)
                        data=readNWait()
                        print("Read: " + data + "\n")
                        if (data.find("r,ACK")==-1): 
                            write2Serial("C,STOP")
                        else:
                          productWaitCycle=0
                          idelstatus=1
                    else:
                        productWaitCycle=0
                        idelstatus=1

                if not (data.find('c,STATUS,OFFLINE')==-1):
                   print("device is offline")
                   vCommand="C,1"
                   sBuf=0
                   cBuf=0
                if not (data.find('c,ERR,"VEND -3"')==-1):
                   print('c,ERR,"VEND -3"')
                   vProduct=data
                   vCommand="C,STOP"
                   sBuf=0
                   cBuf=0
                   
                if not (data.find('c,ERR,"STOP -3"')==-1):
                   print('c,ERR,"STOP -3"')
                   vProduct=data
                   vCommand="C,0"
                   sBuf=0
                   cBuf=0
                if not (data.find('c,ERR,"START -3"')==-1):
                   print('c,ERR,"START -3"')
                   print("Device retrying to vend")
                   vCommand="C,STOP"
                   sBuf=0
                   cBuf=0   

                          
            else:
              if vendCycle==1 and idelstatus==1:
                  print("productWaitCycle="+str(productWaitCycle))
                  productWaitCycle+=1
              if productWaitCycle>=3:
                   productSelectAttempt+=1
                   if(productSelectAttempt>=2):
                       vendCycle=0
                       card_no=""
                       idelstatus=0
                       productSelectAttempt=0
                       productWaitCycle=0
                       vCommand="C,STOP"
                       sBuf=1
                       cBuf=0
                   else:      
                    productWaitCycle=0
                    vCommand="C,STOP"
                    sBuf=0
                    cBuf=1

              print("waiting for valid data, \n vendCycle="+str(vendCycle)+", \nidelstatus="+str(idelstatus)+"\nprductWaitCycle="+str(productWaitCycle)+"\nprductSelectAttempt="+str(productSelectAttempt) )
