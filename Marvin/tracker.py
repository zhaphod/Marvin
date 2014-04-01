import os
import sys
import socket
import struct
import time
import urllib
import random

def from_string(s):
  "Convert dotted IPv4 address to integer."
  return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))
 
def to_string(ip):
  "Convert 32-bit integer to dotted IPv4 address."
  return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

class Tracker:
    def __init__(self):
        self.trackers = {}
        pass
    
    def get_connection_id(self, host_ip, port):
        if host_ip == None:
            return None
        
        if port == None:
            port = 80
            
        try:
            tracker = self.trackers[host_ip]
        except KeyError:
            pass
        else:
            curr_time = time.time()
            if curr_time - tracker[0] < 60:
                return None       
        
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            soc.connect((host_ip, port))
        except:
            raise

        connection_id = 0x41727101980
        action = 0
        transaction_id = random.randint(256, 4096)

        msg = struct.pack('!qii', connection_id, action, transaction_id)    
        
        n = 0
        delay = 15 * (2 ** n)
        while True:
            soc.sendall(msg)
            print "setting delay to ", delay, " seconds"
            soc.settimeout(delay)
            try:
                data  = soc.recv(1024)
            except socket.timeout:
                n += 1
                delay *= 2
                if n > 8:
                    raise RuntimeError("Server not responding, so giving it up")
            except socket.error:
                print "connection to ", host_ip, " failed [error : ]", socket.error
                return None
            else:        
                action, ret_transaction_id, connection_id = struct.unpack("!iiq", data)
                if action != 0 or \
                   ret_transaction_id != transaction_id:
                   print "Invalid message received from the tracker. Trying again"
                   n = 0
                   continue
                else:
                    print "Obtained connection_id ", connection_id
                    self.trackers[host_ip] = [connection_id, time.time(), port]
                    return connection_id   
        
    def get_announce_response(self, host_ip, hashes):
        peers = []
        try:
            connection_id, connec_time, port = self.trackers[host_ip]
        except KeyError:
            return None
            
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            soc.connect((host_ip, port))
        except:
            raise

        action = 1
        transaction_id = random.randint(256, 4096)
           
        quoted_hash = hashes[0]
        unquoted_hash = hashes[1]
                 
        info_hash   = unquoted_hash
        peer_id     = "IMPL_TORRENT__PYTHON"
        downloaded  = 0
        left        = 121114746
        uploaded    = 0
        event       = 0
        ip          = 0
        key         = 0
        num_want    = -1
        port        = 6881

        msg = struct.pack('!qii20s20sqqqiiiih',\
                          connection_id,\
                          action,\
                          transaction_id,\
                          info_hash,\
                          peer_id,\
                          downloaded,\
                          left,\
                          uploaded,\
                          event,\
                          ip,\
                          key,\
                          num_want,\
                          port)
                          
        n = 0
        delay = 15 * (2 ** n)

        pause = 3
        print "waiting for ", pause, " seconds"
        time.sleep(pause)
        while True:
            soc.sendall(msg)
            print "setting delay to ", delay, " seconds"
            soc.settimeout(delay)
            try:
                data = soc.recv(1024)
            except socket.timeout:
                n += 1
                delay *= 2
                if n > 8:
                    raise RuntimeError("Server not responding, so giving it up")
            except:
                raise #some other error so throw it to the user
            else:        
                temp = data[:20]
                action, ret_transaction_id, interval, leechers, seeders = struct.unpack("!iiiii", temp)
                if action != 1 or \
                   ret_transaction_id != transaction_id:
                   print "Invalid message received from the tracker. Trying again"
                   n = 0
                   continue
                else:
                    print "interval ", interval
                    print "leechers ", leechers
                    print "seeders ", seeders
                    #print "peer_ip", to_string(peer_ip)
                    #print "peer_port", peer_port
                    #break #we got the connection_id
                

                if len(data) > 20:
                    for index in range(20, len(data), 6):
                        peer_ip, peer_port = struct.unpack_from("!ih", data, index)
                        peer_ip = to_string(peer_ip)
                        peers.append((peer_ip, peer_port))
                    
                    return peers

        soc.close()
        del(soc)            
            
    def get_peers(self, torrent):
        peers = []
        hashes = torrent.get_info_hash()
        for tracker in torrent["announce-list"]:
            scheme, tracker_ip, tracker_port = self.get_scheme_host_n_port(tracker)
            print scheme, tracker_ip, tracker_port
            if scheme == "udp":
                if self.get_connection_id(tracker_ip, tracker_port):
                    print self.trackers[tracker_ip]
                    temp = self.get_announce_response(tracker_ip, torrent.get_info_hash())
                    if temp:
                        peers.append(temp)
        return peers
            
    
    def get_scheme_host_n_port(self, tracker):
        import urlparse
        print tracker
        pres = urlparse.urlparse(tracker[0])
        print pres.netloc.split(":")[0]
        try:
            ip = socket.gethostbyname(pres.netloc.split(":")[0])
        except:
            ip = None
            
        port = pres.port
        return pres.scheme, ip, port


      
    
if __name__ == "__main__":
    import torrent
    fn = sys.argv[1]

    file = open(fn, "rb")
    line = file.read()
    file.close()
    
    torrent = torrent.Torrent(line)

    tracker = Tracker()
    peers = tracker.get_peers(torrent)
    print "\n"*5
    print peers