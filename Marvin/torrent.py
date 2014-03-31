import bencode
import os
import sys
import collections
import hashlib
import urllib
import string


class Torrent:
    def __init__(self, buf):
        self.torbuf = buf[:]
        self.deq    = collections.deque(self.torbuf)
        self.metainfo = bencode.read_dict(self.deq)
        self.info_hash_quoted = ""
        self.info_hash_unquoted = ""
    
    def get_info_hash():
        if self.info_hash_quoted:
            pass
        else:
            index = self.torbuf.index("4:info") + 6
            
            sha1 = hashlib.sha1()
            sha1.update(self.torbuf[index:])
            self.info_hash_unquoted = sha1.digest()
            self.info_hash_quoted = urllib.quote_plus(self.info_hash_unquoted)
            
            del(sha1)
            
        return self.info_hash_quoted, self.info_hash_unquoted
            
    
    def __getitem__(self, key):
        return self.metainfo[key]
    def __setitem__(self, key, value):
        self.metainfo[key] = value
        
        
if __name__ == "__main__":
    fn = sys.argv[1]

    file = open(fn, "rb")
    line = file.read()
    file.close()
    
    torrent = Torrent(line)

    print torrent["info"]