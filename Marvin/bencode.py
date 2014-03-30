import os
import sys
import collections
import hashlib
import urllib
import httplib2


def restore_buffer(buffer, value):
    temp = collec.deque(value)
    temp.reverse()
    buffer.extendleft(temp)


def read_int(buffer):
    value = ""
    integer = None
    negative = 1
        
    ch = buffer.popleft()
    if ch == "i":
        try:
            while True:
                ch = buffer.popleft()
                if ch == 'e': break
                value += ch
        except:
            restore_buffer(buffer, 'i' + value)
            return None
            
        gobbled = 'i' + value + 'e'
        
        if value[0] == '-':
            negative = -1
            value = value[1:]
        if value[0] == '0':
            if len(value) > 1:
                restore_buffer(buffer, gobbled)
                return None
        try:
            integer = int(value)
        except:
            restore_buffer(buffer, gobbled)
            return None
        
        return integer * negative
    else:
        buffer.appendleft(ch)
        
    return None

def read_string(buffer):
    value = "" 
    ch = ''
    
    try:
        while True:
            ch = buffer.popleft()
            if ch == ':': break
            value += ch
    except:
        restore_buffer(buffer, value)
        return None
        
    try:
        length = int(value)
    except:
        value += ch
        restore_buffer(buffer, value)
        return None
    
    value = ""
    for x in range(length):
        value += buffer.popleft()
    
    return value

def read_list(buffer):
    from string import digits
    value = []
    ch = ''
    
    ch = buffer.popleft()
    if ch == 'l':
        while buffer[0] != 'e':
            if buffer[0] == 'l':
                ret = read_list(buffer)
                if ret: value.append(ret)
            elif buffer[0] == 'i':
                ret = read_int(buffer)
                if ret: value.append(ret)
            elif buffer[0] in digits[1:]:
                ret = read_string(buffer)
                if ret: value.append(ret)
            elif buffer[0] == 'd':
                ret = read_dict(buffer)
                if ret: value.append(ret)
            else:
                return None
        else:
            buffer.popleft()
            return value
    else:
        buffer.appendleft(ch)
    return None
    
def read_dict(buffer):
    from string import digits
    value = {}
    ch = ''
    
    ch = buffer.popleft()
    if ch == 'd':
        while buffer[0] != 'e':
            key = read_string(buffer)
            if key:
                if buffer[0] == 'l':
                    ret = read_list(buffer)
                    value[key] = ret
                elif buffer[0] == 'i':
                    ret = read_int(buffer)
                    value[key] = ret
                elif buffer[0] in digits[1:]:
                    ret = read_string(buffer)
                    value[key] = ret
                elif buffer[0] == 'd':
                    ret = read_dict(buffer)
                    value[key] = ret
                else:
                    return None                
            else:
                #have to do proper reconstruction based on the current "value" not just appendleft
                buffer.appendleft(ch)
                return None
        else:
            buffer.popleft()
            return value
    else:
        buffer.appendleft(ch)
    return None            

fn = sys.argv[1]

file = open(fn, "rb")
line = file.read()
file.close()

buf = collections.deque(line)

torrent =  read_dict(buf)

#print torrent['announce-list']

index_info_value = line.index("4:info") + 6

sha = hashlib.sha1()
sha.update(line[index_info_value:])
print sha.digest()
print bytearray(sha.digest())

info_hash = urllib.quote_plus(sha.digest())

tracker_query_param = {\
    "info_hash" : "%E7%E5%D8%5D%97%E6d%93C%C9%AC%E9Ld%9EA%8FL%2B%F3",\
    "peer_id"   : "IMPL_TORRENT__PYTHON",\
    "port"      : "6881",\
    "uploaded"  : "0",\
    "downloaded": "0",\
    "left"      : "0"\
    }
    
tracker_query_param["info_hash"] = info_hash
    
param = urllib.urlencode(tracker_query_param)

print info_hash
print urllib.unquote_plus(info_hash)
print tracker_query_param["info_hash"]
print param
    
#tracker = "http://tracker.istole.it/announce"    
tracker = "http://tracker.publicbt.com/announce"
tracker = "http://fr33dom.h33t.com:3310/announce"
tracker = "http://exodus.desync.com:6969/announce"

if 0:
    http = httplib2.Http('.cache')

    url = tracker + "?" + param
    response, content = http.request(url)

    print "\n\n\n==========================="
    print response
    print "==========================="
    print content
    print "===========================\n\n\n"


