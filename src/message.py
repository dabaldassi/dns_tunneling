
def encodeName(name):
    domainList = name.split('.')
    encodedName = b''

    for d in domainList:
        encodedName += len(d).to_bytes(1, 'big')
        for letter in d:
            encodedName += bytes(letter, 'ascii')
    encodedName += (0).to_bytes(1, 'big')

    return encodedName

def decodeName(b):
    name = ""
    nameLength = 0
    i = 0

    while b[i:i+1].hex() != '00':
        length = int(b[i:i+1].hex(), 16)
        for j in range(length):
            name += str(b[i+1+j:i+2+j], 'ascii')
        nameLength += length + 1
        i += length + 1
        if b[i:i+1].hex() != '00':
            name += '.'

    return name, nameLength + 1

def getType(type):
    if type == 1:
        return 'A'
    elif type == 2:
        return 'NS'
    elif type == 3:
        return 'MD'
    elif type == 4:
        return 'MF'
    elif type == 5:
        return 'CNAME'
    elif type == 6:
        return 'SOA'
    elif type == 7:
        return 'MB'
    elif type == 8:
        return 'MG'
    elif type == 9:
        return 'MR'
    elif type == 10:
        return 'NULL'
    elif type == 11:
        return 'WKS'
    elif type == 12:
        return 'PTR'
    elif type == 13:
        return 'HINFO'
    elif type == 14:
        return 'MINFO'
    elif type == 15:
        return 'MX'
    elif type == 16:
        return 'TXT'
    elif type == 252:
        return 'AXFR'
    elif type == 253:
        return 'MAILB'
    elif type == 254:
        return 'MAILA'
    elif type == 255:
        return '*'

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

class Header:

    def __init__(self, id, qr, opcode, aa = False, tc = False, rd = True, ra = False, z = 0, rcode = 0, qdcount = 1, ancount = 0, nscount = 0, arcount = 0):
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
        string += "\nQr : " + str(self.qr) + "\t\tOpcode : " + str(bool(self.opcode)) + "\t\tAa : " + str(bool(self.aa)) + "\t\tTc : " + str(bool(self.tc)) + "\t\tRd : " + str(bool(self.rd))
        string += "\nRa : " + str(bool(self.ra)) + "\t\tZ : " + str(self.z) + "\t\tRcode : " + str(self.rcode)
        string += "\nQdcount : " + str(self.qdcount)
        string += "\nAncount : " + str(self.ancount)
        string += "\nNscount : " + str(self.nscount)
        string += "\nArcount : " + str(self.arcount)

        return string

class Question:

    def __init__(self, domainName, qtype = 1, qclass = 1):
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

    def __init__(self, name, rdata, type = 1, classe = 1, ttl = 0):
        self.name = name
        self.type = type
        self.classe = classe
        self.ttl = ttl
        self.rdata = rdata

    def getBytes(self):
        msg = encodeName(self.name)
        msg += self.type.to_bytes(2, 'big')
        msg += self.classe.to_bytes(2, 'big')
        msg += self.ttl.to_bytes(4, 'big')
        msg += len(self.rdata).to_bytes(2, 'big')
        msg += self.rdata

        return msg

    def __str__(self):
        string = "* Resource Record *\n"
        string += "Domain name : " + self.name
        string += "\nType : " + getType(self.type)
        string += "\nClass : " + getClass(self.classe)
        string += "\nTTL : " + str(self.ttl)
        string += "\nRaw data : " + self.rdata.hex().upper()

        return string


class Message:

    def __init__(self, header, qList = [], rrList = []):
        self.header = header
        self.qList = qList
        self.rrList = rrList

    def getBytes(self):
        msg = self.header.getBytes()
        for q in self.qList:
            msg += q.getBytes()
        for rr in self.rrList:
            msg += rr.getBytes()

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
            return self.rrList[(self.header.ancount + self.header.nscount):(self.header.ancount + self.header.nscount + self.header.arcount)]
        else:
            return []

    def __str__(self):
        string = "==============================\n\n"
        string += str(self.header)
        for i in range(self.header.qdcount):
            string += "\n\n" + str(i+1) + "\t"
            string += str(self.qList[i])
        answer = self.getAnswer()
        for i in range(self.header.ancount):
            string += "\n\n" + str(i+1) + "\t"
            string += str(answer[i])
        authority = self.getAuthority()
        for i in range(self.header.nscount):
            string += "\n\n" + str(i+1) + "\t"
            string += str(authority[i])
        additional = self.getAdditional()
        for i in range(self.header.arcount):
            string += "\n\n" + str(i+1) + "\t"
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
        int(b[10:].hex(), 16)
    )

def bytesToQuestion(b):
    name, nameLength = decodeName(b)
    return Question(
        name,
        int(b[nameLength:nameLength + 2].hex(), 16),
        int(b[nameLength + 2:nameLength + 4].hex(), 16)
    )

def bytesToRecord(b):
    name, nameLength = decodeName(b)
    return RR(
        name,
        b[nameLength + 10:nameLength + 10 + int(b[nameLength + 8:nameLength + 10].hex(), 16)],
        int(b[nameLength:nameLength + 2].hex(), 16),
        int(b[nameLength + 2:nameLength + 4].hex(), 16),
        int(b[nameLength + 4:nameLength + 8].hex(), 16)
    )

def bytesToMessage(b):
    header = bytesToHeader(b[:12])
    qList = []
    rrList = []
    length = 0
    for i in range(header.qdcount):
        q = bytesToQuestion(b[12 + length:])
        length += len(q.qname) + 6
        qList.append(q)
    for i in range(header.ancount + header.nscount + header.arcount):
        rr = bytesToRecord(b[12 + length:])
        length += len(rr.name) + len(rr.rdata) + 12
        rrList.append(rr)

    return Message(header, qList, rrList)
