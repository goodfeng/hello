# -*- coding: utf-8 -

from queue import PriorityQueue
from tcpconn import NTcpConnector
import time

class ProxyS(object):
    def __init__(self, max_size, host, port):
        self.max_size = max_size
        self._q = PriorityQueue()
        self.nSn = 0
        self.host = host
        self.port = port

    def getSN(self):
        self.nSn+=1
        return self.nSn
            
    def getConn(self):
        conn = None
        try:                                                               
            if self._q.qsize()>=self.max_size:
                while self._q.qsize()>0:                    
                    conn =self._q.get(False)[1]                     
                    if conn.is_connected():
                        return conn
                    else:
                        self._reap_connection(conn)
            else:                              
                conn = NTcpConnector(self.host,self.port)
                return conn
                        
        except Exception as e:
            conn.handle_exception(e)
        finally:
            self.release_connection(conn)   
                                          
    def release_connection(self, conn):
        if self._q.qsize() < self.max_size and conn.is_connected():
            self._q.put((time.time(), conn))
        else:
            self._reap_connection(conn) 
                
    def _reap_connection(self, conn):
        if conn and conn.is_connected():
            conn.invalidate()          
            
