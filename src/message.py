def encodeName(name):
    domainList = name.split('.')
    encodedName = b''

    for d in domainList:
        encodedName += len(d).to_bytes(1, 'big')
        for letter in d:
            encodedName += bytes(letter, 'latin-1')
    encodedName += b'\x00'

    return encodedName


def encode_compressed_name(name, previous_names, begin):
    encoded_name = b''
    split_name = name
    i = begin
    to_encode = []

    while split_name != '' and split_name not in previous_names:
        tmp, sep, split_name = split_name.partition('.')
        to_encode.append([tmp,i])
        encoded_name += len(to_encode[-1][0]).to_bytes(1, 'big')
        i += 1
        for letter in to_encode[-1][0]:
            encoded_name += bytes(letter, 'latin-1')
            i += 1
        for k in range(len(to_encode) - 1):
            to_encode[k][0] += '.' + to_encode[-1][0]

    if split_name != '':
        encoded_name += previous_names[split_name]
        i += 2
        for (ns, index) in to_encode:
            previous_names[ns + '.' + split_name] = (49152 + index).to_bytes(2, 'big')
    else:
        encoded_name += b'\x00'
        i += 1
        for (ns, index) in to_encode:
            previous_names[ns] = (49152 + index).to_bytes(2, 'big')

    return encoded_name, i


def decodeName(b, begin):
    name = ""
    nameLength = 0
    i = begin

    while b[i:i + 1].hex() != '00' and int(b[i:i + 1].hex(), 16) < 192:
        length = int(b[i:i + 1].hex(), 16)
        for j in range(length):
            name += str(b[i + 1 + j:i + 2 + j], 'latin-1')
        nameLength += length + 1
        i += length + 1
        if b[i:i + 1].hex() != '00':
            name += '.'

    if int(b[i:i + 1].hex(), 16) >= 192:
        name += decodeName(b, int(b[i:i+2].hex(), 16) - 49152)[0]
        nameLength += 1

    return name, nameLength + 1


def getType(type_data):
    if type_data == 1:
        return 'A'
    elif type_data == 2:
        return 'NS'
    elif type_data == 3:
        return 'MD'
    elif type_data == 4:
        return 'MF'
    elif type_data == 5:
        return 'CNAME'
    elif type_data == 6:
        return 'SOA'
    elif type_data == 7:
        return 'MB'
    elif type_data == 8:
        return 'MG'
    elif type_data == 9:
        return 'MR'
    elif type_data == 10:
        return 'NULL'
    elif type_data == 11:
        return 'WKS'
    elif type_data == 12:
        return 'PTR'
    elif type_data == 13:
        return 'HINFO'
    elif type_data == 14:
        return 'MINFO'
    elif type_data == 15:
        return 'MX'
    elif type_data == 16:
        return 'TXT'
    elif type_data == 28:
        return 'AAAA'
    elif type_data == 252:
        return 'AXFR'
    elif type_data == 253:
        return 'MAILB'
    elif type_data == 254:
        return 'MAILA'
    elif type_data == 255:
        return '*'
    else:
        return type_data.to_bytes(2, 'big').hex()


def getClass(classe):
    if classe == 1:
        return 'IN'
    elif classe == 2:
        return 'CS'
    elif classe == 3:
        return 'CH'
    elif classe == 4:
        return 'HS'
    elif classe == 255:
        return '*'
    else:
        return classe.to_bytes(2, 'big').hex()


class Header:

    def __init__(self, id, qr, opcode, aa=False, tc=False, rd=True, ra=False, z=0, rcode=0, qdcount=1, ancount=0,
                 nscount=0, arcount=0):
        self.id = id
        self.qr = qr
        self.opcode = opcode
        self.aa = int(aa)
        self.tc = int(tc)
        self.rd = int(rd)
        self.ra = int(ra)
        self.z = z
        self.rcode = rcode
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = nscount
        self.arcount = arcount

    def getBytes(self):
        msg = bytes.fromhex(self.id)
        msg += ((self.qr << 7) + (self.opcode << 3) + (self.aa << 2) + (self.tc << 1) + self.rd).to_bytes(1, 'big')
        msg += ((self.ra << 7) + (self.z << 4) + self.rcode).to_bytes(1, 'big')
        msg += self.qdcount.to_bytes(2, 'big')
        msg += self.ancount.to_bytes(2, 'big')
        msg += self.nscount.to_bytes(2, 'big')
        msg += self.arcount.to_bytes(2, 'big')

        return msg

    def getOpcode(self):
        if self.opcode == 0:
            return 'QUERY'
        elif self.opcode == 1:
            return 'IQUERY'
        elif self.opcode == 2:
            return 'STATUS'
        elif self.opcode <= 15:
            return str(self.opcode)

    def getRcode(self):
        if self.rcode == 0:
            return 'No error condition'
        elif self.rcode == 1:
            return 'Format error'
        elif self.rcode == 2:
            return 'Server failure'
        elif self.rcode == 3:
            return 'Name error'
        elif self.rcode == 4:
            return 'Not implemented'
        elif self.rcode == 5:
            return 'Refused'
        elif self.rcode <= 15:
            return str(self.rcode)

    def __str__(self):
        string = "* Header *\n"
        string += "ID : " + self.id.upper()
        string += "\nQr : " + str(self.qr) + "\t\tOpcode : " + str(bool(self.opcode)) + "\t\tAa : " + str(
            bool(self.aa)) + "\t\tTc : " + str(bool(self.tc)) + "\t\tRd : " + str(bool(self.rd))
        string += "\nRa : " + str(bool(self.ra)) + "\t\tZ : " + str(self.z) + "\t\tRcode : " + self.getRcode()
        string += "\nQdcount : " + str(self.qdcount)
        string += "\nAncount : " + str(self.ancount)
        string += "\nNscount : " + str(self.nscount)
        string += "\nArcount : " + str(self.arcount)

        return string


class Question:

    def __init__(self, domainName, qtype=1, qclass=1):
        self.qname = domainName
        self.qtype = qtype
        self.qclass = qclass

    def getBytes(self):
        msg = encodeName(self.qname)
        msg += self.qtype.to_bytes(2, 'big')
        msg += self.qclass.to_bytes(2, 'big')

        return msg

    def __str__(self):
        string = "* Question *\n"
        string += "Domain name : " + self.qname
        string += "\nQuestion type : " + getType(self.qtype)
        string += "\nQuestion class : " + getClass(self.qclass)

        return string


class RR:

    def __init__(self, name, rdata, type_data=1, classe=1, ttl=0):
        self.name = name
        self.type_data = type_data
        self.classe = classe
        self.ttl = ttl
        self.rdata = rdata

    def getBytes(self):
        msg = encodeName(self.name)
        msg += self.type_data.to_bytes(2, 'big')
        msg += self.classe.to_bytes(2, 'big')
        msg += self.ttl.to_bytes(4, 'big')
        msg += len(self.rdata).to_bytes(2, 'big')
        msg += self.rdata

        return msg

    def __str__(self):
        string = "* Resource Record *\n"
        string += "Domain name : " + self.name
        string += "\nType : " + getType(self.type_data)
        string += "\nClass : " + getClass(self.classe)
        string += "\nTTL : " + str(self.ttl)
        string += "\nRaw data : " + self.rdata.hex().upper()

        return string


class Message:

    def __init__(self, header, qList=[], rrList=[]):
        self.header = header
        self.qList = qList
        self.rrList = rrList

    def getBytes(self):
        previous_names = {}
        msg = self.header.getBytes()
        i = 12
        for q in self.qList:
            tmp, i = encode_compressed_name(q.qname, previous_names, i)
            msg += tmp
            msg += q.qtype.to_bytes(2, 'big')
            msg += q.qclass.to_bytes(2, 'big')
            i += 4
        for rr in self.rrList:
            tmp, i = encode_compressed_name(rr.name, previous_names, i)
            msg += tmp
            msg += rr.type_data.to_bytes(2, 'big')
            msg += rr.classe.to_bytes(2, 'big')
            msg += rr.ttl.to_bytes(4, 'big')
            i += 10
            if rr.type_data == 2:
                tmp, i2 = encode_compressed_name(rr.rdata, previous_names, i)
                msg += (i2-i).to_bytes(2, 'big')
                msg += tmp
                i = i2
            elif rr.type_data == 15:
                tmp, i2 = encode_compressed_name(rr.rdata, previous_names, i + 2)
                msg += (i2-i).to_bytes(2, 'big')
                msg += b'\x00\x01'
                msg += tmp
                i = i2
            else:
                msg += len(rr.rdata).to_bytes(2, 'big')
                msg += rr.rdata
                i += len(rr.rdata)

        return msg

    def getAnswer(self):
        if self.header.ancount > 0:
            return self.rrList[:self.header.ancount]
        else:
            return []

    def getAuthority(self):
        if self.header.nscount > 0:
            return self.rrList[self.header.ancount:(self.header.ancount + self.header.nscount)]
        else:
            return []

    def getAdditional(self):
        if self.header.arcount > 0:
            return self.rrList[(self.header.ancount + self.header.nscount):(
                        self.header.ancount + self.header.nscount + self.header.arcount)]
        else:
            return []

    def __str__(self):
        string = "==============================\n\n"
        string += str(self.header)
        for i in range(self.header.qdcount):
            string += "\n\n" + str(i + 1) + "\t"
            string += str(self.qList[i])
        answer = self.getAnswer()
        for i in range(self.header.ancount):
            string += "\n\n" + str(i + 1) + "\t"
            string += str(answer[i])
        authority = self.getAuthority()
        for i in range(self.header.nscount):
            string += "\n\n" + str(i + 1) + "\t"
            string += str(authority[i])
        additional = self.getAdditional()
        for i in range(self.header.arcount):
            string += "\n\n" + str(i + 1) + "\t"
            string += str(additional[i])

        return string


def bytesToHeader(b):
    return Header(
        b[:2].hex(),
        int(b[2:3].hex(), 16) >> 7,
        (int(b[2:3].hex(), 16) >> 3) % 16,
        (int(b[2:3].hex(), 16) >> 2) % 2,
        (int(b[2:3].hex(), 16) >> 1) % 2,
        int(b[2:3].hex(), 16) % 2,
        (int(b[3:4].hex(), 16) >> 7) % 2,
        (int(b[3:4].hex(), 16) >> 4) % 8,
        int(b[3:4].hex(), 16) % 16,
        int(b[4:6].hex(), 16),
        int(b[6:8].hex(), 16),
        int(b[8:10].hex(), 16),
        int(b[10:12].hex(), 16)
    )


def bytesToQuestion(b, begin):
    name, nameLength = decodeName(b, begin)
    return Question(
        name,
        int(b[begin + nameLength:begin + nameLength + 2].hex(), 16),
        int(b[begin + nameLength + 2:begin + nameLength + 4].hex(), 16)
    ), nameLength + 4


def bytesToRecord(b, begin):
    name, nameLength = decodeName(b, begin)
    dataLength = int(b[begin + nameLength + 8:begin + nameLength + 10].hex(), 16)
    return RR(
        name,
        b[begin + nameLength + 10:begin + nameLength + 10 + dataLength],
        int(b[begin + nameLength:begin + nameLength + 2].hex(), 16),
        int(b[begin + nameLength + 2:begin + nameLength + 4].hex(), 16),
        int(b[begin + nameLength + 4:begin + nameLength + 8].hex(), 16)
    ), nameLength + dataLength + 10


def bytesToMessage(b):
    header = bytesToHeader(b)
    qList = []
    rrList = []
    length = 0

    for i in range(header.qdcount):
        q, l = bytesToQuestion(b, 12 + length)
        length += l
        qList.append(q)

    for i in range(header.ancount + header.nscount + header.arcount):
        rr, l = bytesToRecord(b, 12 + length)
        length += l
        rrList.append(rr)

    return Message(header, qList, rrList)

def readTXT(txt):
    result=b''
    i = 0

    try:
        while(i < len(txt)):
            length = txt[i]
            i += 1
            if(i+length > len(txt)):
                print("Error while decoding txt record")
            result += txt[i:i+length]
            i += length
    except:
        print("Error while decoding txt record")
        
    return result


def writeTXT(txt):
    result = b''
    i=0
    lentxt = len(txt)

    while(i < lentxt):
        l = min(255,lentxt - i)
        result += l.to_bytes(1,'big')
        result += txt[i:i+l]
        i+=l

    return result

def defaultMessage(query):
    name = query.qList[0].qname
    default_RR = { 1:([RR(name,b'\x01'*4,1,1,1)],
                      [],
                      []),
                   2:([RR(name,b'\x01'*4,1,1,1)],
                      [RR(name,b'salut.devtoplay.com',2,1,1)],
                      [RR("salut.devtoplay.com",b'\x02'*4,1,1,1)]),
                   16:([RR(name,writeTXT(b'ACK'),16,1,1)],
                       [],
                       []),
                   28:([RR(name,b'\x01'*16,28,1,1)],
                       [],
                       []) }

    try:
        answer,ns,additional = default_RR[query.qList[0].qtype]
    except:
        answer,ns,additional = default_RR[1]

    return Message(Header(query.header.id,1,0,False,False,True,True,0,0,1,len(answer),len(ns),len(additional)),
                   query.qList,
                   answer+ns+additional)

def removePoint(s):
    nb_dot = s.count('.')
    
    if(nb_dot == 0):
        s = '\x00'+s
    else:
        tmp = list(s)
        pos = ''
        
        for i in range(nb_dot):
            ind = tmp.index('.')
            tmp.pop(ind)
            pos += chr(0x80 | ((nb_dot != i+1) << 6) | (ind+i))
            
        s = pos + ''.join(tmp)

    return s

def insertPoint(s):
    if(ord(s[0]) & 0x80):
        i = 0
        r = True
        tmp = list(s)
        pos = []
        
        while(r):
            pos.append(ord(tmp[0]) & 0x3f)
            r = ord(tmp[0]) & 0x40
            tmp.pop(0)

        for i in pos:
            tmp.insert(i,'.')

        s = ''.join(tmp)
            
    else:
        s = s.replace(s[0],'',1)
            
    return s
    
