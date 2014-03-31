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
