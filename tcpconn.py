# -*- coding: utf-8 -

from tornado.iostream import IOStream
import socket,struct,time

class NTcpConnector(object):
    def __init__(self,host,port):
        self.routes = {}
        self.host = host
        self.port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = IOStream(self._s)
        self.stream.connect((self.host, self.port), self._start_recv)

    def unregister(self,client):
        self.routes = dict(filter(lambda x: x[1] != client, self.routes.items()))

    def __lt__(self,other):
        return id(self)<id(other)
                
    def sendMsg(self,client,content):
        sn = client.application.proxys.getSN()
        self.routes[sn]=client
        data =struct.pack('<i6I%dsI'%len(content),int(-1),10020,20+len(content),sn,0,int(time.time()),1,content.encode('utf-8'),int((20+len(content)) ^ 0xaaaaaaaa))
        self.stream.write(data)

    def is_connected(self):
        return not self.stream.closed()
    
    def invalidate(self):
        self.stream.close_fd()
    
    def _start_recv(self):  
        self.stream.read_bytes(12, self._on_frame)
    
    def _on_frame(self,data):
        nLen=struct.unpack('<i2I',data)[2]
        self.stream.read_bytes(nLen, self._on_msg)
        
    def _on_msg(self,data):
        nLen = len(data)  
        sn,nTag,nTime,nCmdId,dataS=struct.unpack('<4I%dsI'%(nLen-20),data)[0:-1]
        
        if sn==0:
            self.stream.write(struct.pack('<i7I',int(-1),10000,20,0,0,int(time.time()),0,int(20 ^ 0xaaaaaaaa)))
        elif sn>0 and (sn in self.routes):
            fs,strField = {},''       
            if  nCmdId==110 and nLen==292:#十档报价
                ds=struct.unpack('<2iIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIqIq',dataS)
                strField='nSecurityID,nTime,nPxBid1,llVolumeBid1,nPxBid2,llVolumeBid2,nPxBid3,llVolumeBid3,nPxBid4,llVolumeBid4,nPxBid5,llVolumeBid5,nPxBid6,llVolumeBid6,nPxBid7,llVolumeBid7,nPxBid8,llVolumeBid8,nPxBid9,llVolumeBid9,nPxBid10,llVolumeBid10,nWeightedAvgBidPx,llTotalBidVolume,nPxOffer1,llVolumeOffer1,nPxOffer2,llVolumeOffer2,nPxOffer3,llVolumeOffer3,nPxOffer4,llVolumeOffer4,nPxOffer5,llVolumeOffer5,nPxOffer6,llVolumeOffer6,nPxOffer7,llVolumeOffer7,nPxOffer8,llVolumeOffer8,nPxOffer9,llVolumeOffer9,nPxOffer10,llVolumeOffer10,nWeightedAvgOfferPx,llTotalOfferVolume'                 
            elif nCmdId==165 and nLen==644:#委托明细
                ds=struct.unpack('<2iI3i150i',dataS)
                strField='nSecurityID,nTime,nPx,nLevel,nOrderCount,nRevealCount,nStatus1,nVolume1,nChangeVolume1,nStatus2,nVolume2,nChangeVolume2,nStatus3,nVolume3,nChangeVolume3,nStatus4,nVolume4,nChangeVolume4,nStatus5,nVolume5,nChangeVolume5,nStatus6,nVolume6,nChangeVolume6,nStatus7,nVolume7,nChangeVolume7,nStatus8,nVolume8,nChangeVolume8,nStatus9,nVolume9,nChangeVolume9,nStatus10,nVolume10,nChangeVolume10,nStatus11,nVolume11,nChangeVolume11,nStatus12,nVolume12,nChangeVolume12,nStatus13,nVolume13,nChangeVolume13,nStatus14,nVolume14,nChangeVolume14,nStatus15,nVolume15,nChangeVolume15,nStatus16,nVolume16,nChangeVolume16,nStatus17,nVolume17,nChangeVolume17,nStatus18,nVolume18,nChangeVolume18,nStatus19,nVolume19,nChangeVolume19,nStatus20,nVolume20,nChangeVolume20,nStatus21,nVolume21,nChangeVolume21,nStatus22,nVolume22,nChangeVolume22,nStatus23,nVolume23,nChangeVolume23,nStatus24,nVolume24,nChangeVolume24,nStatus25,nVolume25,nChangeVolume25,nStatus26,nVolume26,nChangeVolume26,nStatus27,nVolume27,nChangeVolume27,nStatus28,nVolume28,nChangeVolume28,nStatus29,nVolume29,nChangeVolume29,nStatus30,nVolume30,nChangeVolume30,nStatus31,nVolume31,nChangeVolume31,nStatus32,nVolume32,nChangeVolume32,nStatus33,nVolume33,nChangeVolume33,nStatus34,nVolume34,nChangeVolume34,nStatus35,nVolume35,nChangeVolume35,nStatus36,nVolume36,nChangeVolume36,nStatus37,nVolume37,nChangeVolume37,nStatus38,nVolume38,nChangeVolume38,nStatus39,nVolume39,nChangeVolume39,nStatus40,nVolume40,nChangeVolume40,nStatus41,nVolume41,nChangeVolume41,nStatus42,nVolume42,nChangeVolume42,nStatus43,nVolume43,nChangeVolume43,nStatus44,nVolume44,nChangeVolume44,nStatus45,nVolume45,nChangeVolume45,nStatus46,nVolume46,nChangeVolume46,nStatus47,nVolume47,nChangeVolume47,nStatus48,nVolume48,nChangeVolume48,nStatus49,nVolume49,nChangeVolume49,nStatus50,nVolume50,nChangeVolume50'                      
            else:pass
            
            if strField :
                fields = strField.split(',')                        
                for i in range(0,len(fields)):fs[fields[i]]=ds[i] 
                fs['nCmdId'] = nCmdId
                self.routes[sn].callback(fs)
            
        self._start_recv() 