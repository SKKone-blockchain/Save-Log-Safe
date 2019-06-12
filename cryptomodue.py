import json
from base64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import keccak
import ipfshttpclient
import time
import os

debug = 0

class DecryptionError(Exception):
    pass
class encrypt:
    def __init__(self, loglist, password, salt):
        self.salt = salt
        self.key = PBKDF2(password, self.salt)
        self.c = AES.new(self.key, AES.MODE_GCM)
        self.loglist = loglist
    
    def concate(self):
        string = ''
        if self.loglist == None:
            return string
        for i in range(len(self.loglist)):
            try:
                string += self.loglist[i]
            except TypeError:
                string += self.loglist[i].decode()
        return string
    
    def engine(self):
        data = self.concate()
        header = str(time.time()).encode()
        self.c.update(header)
        ciphertext, tag = self.c.encrypt_and_digest(data.encode())
        json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
        json_v = [ b64encode(self.c.nonce).decode('utf-8'), b64encode(header).decode('utf-8'), b64encode(ciphertext).decode('utf-8'), b64encode(tag).decode('utf-8') ]
        self.ct = json.dumps(dict(zip(json_k, json_v)))
        return self.ct

    def extract(self):
        json_p = json.loads(self.ct)
        filename = '/etc/savelog/cypertext/'+b64decode(json_p['header']).decode()
        try:
            f = open (filename, 'wb')
        except FileNotFoundError:
            os.mkdir('/etc/savelog/cypertext')
            f = open (filename, 'wb')
        f.write(self.ct.encode())
        f.close()

class decrypt:
    def __init__(self, password, salt):
        self.salt = salt
        self.key = PBKDF2(password, self.salt)

    def engine(self, ct):
        try:
            #b64 = json.loads(ct)
            b64 = ct
            json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
            jv = {k:b64decode(b64[k]) for k in json_k}
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=jv['nonce'])
            cipher.update(jv['header'])
            plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
            return plaintext
        
        except ValueError as e:
            return False
        except KeyError as e:
            return False

class ipfs:
    def __init__(self):
        self.client=ipfshttpclient.connect(session=True)
        self.cidlist = []

    def upload(self, json_i):
        try:
            json_p = json.loads(json_i)
            filename = '/etc/savelog/cypertext/'+b64decode(json_p['header']).decode()
            res = self.client.add(filename)
            self.cidlist.append(res['Hash'])
            return res['Hash']
        except:
            return False

    def download(self, jsonhash):
        json = self.client.get_json(jsonhash)
        return json
    
    def extract(self, filename="/etc/savelog/hash"):
        f = open(filename, 'a')
        for h in self.cidlist:
            f.write(h+'\n')
        f.close()
    
    def rm(self):
        for h in self.client.pin.ls()['Keys']:
            try:
                self.client.pin.rm(h)
            except:
                pass
        self.cidlist = []

    def close(self):
        self.client.close()



class wrapper:
    def __init__(self, password):
        self.ipfs = ipfs()
        self.password = None
        try:
            f = open('/etc/savelog/salt', 'rb')
            self.salt = f.read(-1)
            f.close()
        except FileNotFoundError:
            f.close()
            f = open('/etc/savelog/salt', 'wb')
            self.salt = get_random_bytes(16)
            f.write(self.salt)
            f.close()
        
    def encandup(self, password, loglist):
        if self.password is None:
            self.savepassword(password)
        c = encrypt(loglist, password, self.salt)
        ct = c.engine()
        c.extract()
        myhash = self.ipfs.upload(ct)
        self.ipfs.extract()
        return myhash
    
    def downanddec(self,password, h=None):
        d = decrypt(password, self.salt)
        mlist = []
        if h is None:
            for x in self.ipfs.cidlist:
                ct = self.ipfs.download(x)
                pt = d.engine(ct)
                if pt is False:
                    raise DecryptionError
                    return False
                else :
                    mlist.append(d.engine(ct))
        else:
            ct = self.ipfs.download(h)
            pt = d.engine(ct)
            if pt is False:
                raise DecryptionError
                return False
            else :
                mlist.append(d.engine(ct))
        return mlist
    
    def changepassword(self, password, new_password):
        loglist = self.downanddec(password)
        self.salt = get_random_bytes(16)
        f = open('/etc/savelog/salt', 'wb')
        f.write(self.salt)
        self.ipfs.rm()
        newhash = self.encandup(new_password, loglist)

        f = open('/etc/savelog/hash', 'w')
        f.write(newhash)
        f.close()
        self.savepassword(new_password)
        return newhash

    def gethashlist(self):
        return self.ipfs.cidlist
    
    def comparepassword(self, password):
        keccak_hash = keccak.new(digest_bits=512)
        keccak_hash.update(password.encode())
        if keccak_hash.hexdigest() == self.passwordhash:
            return (True, keccak_hash.hexdigest())
        else:
            return (False, keccak_hash.hexdigest())
   
    def savepassword(self, password):
        khash = keccak.new(digest_bits=512)
        khash.update(password.encode())
        self.passwordhash = khash.hexdigest()

if __name__ == "__main__":
    w = wrapper()
    w.ipfs.rm()
    w.ipfs.close()

