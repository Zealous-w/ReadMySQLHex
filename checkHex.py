# -*- coding:utf-8 -*-
import json
import sys
import re
import MySQLdb

filename   = 'hex.json'
typelist   = []
resultlist = []
begin      = 0
end        = 0
hexstr     = ''

def parse( data, typelist, prefix='' ):
    for entry in data:
        SplitByType(entry, typelist, prefix)

def convertL2B( source ):
    first  = 0;
    second = 0;
    target = ''
    listTemp = []
    for b in range(len(source)):
        second += 2
        listTemp.append(source[first:second])
        first += 2
    while listTemp:
        target += listTemp.pop()
    return target

def FormatStr( entry, prefix, begin, end ):
    strTemp = "%s[%8s] -> %8s : %s" % (prefix, hexstr[begin:end], entry[1], str(int(convertL2B(hexstr[begin:end]), 16)) )
    return strTemp


def SplitByType(entry, typelist, prefix):
    global begin
    global end
    dtype = entry[0]
    if dtype == 'uint8':
        end   += 2
        resultlist.append( FormatStr( entry, prefix, begin, end ) )
        begin += 2
    elif dtype == 'uint16':
        end   += 4
        resultlist.append( FormatStr( entry, prefix, begin, end ) )
        begin += 4
    elif dtype == 'uint32':
        end   += 8
        resultlist.append( FormatStr( entry, prefix, begin, end ) )
        begin += 8
    elif dtype == 'uint64':
        end   += 16
        resultlist.append( FormatStr( entry, prefix, begin, end ) )
        begin += 16
    elif dtype == 'list':
        offect = 4;
        if ( entry[2] == 'uint32' ):
            offect = 8

        end   += offect
        
        length = int(convertL2B(hexstr[begin:end]), 16)
        strTemp = "%s<%s> (%s : %d)" % (prefix, entry[1],  hexstr[begin:end], int(convertL2B(hexstr[begin:end]), 16) )
        resultlist.append( strTemp )

        begin += offect

        resultlist.append( prefix + '{')
        for i in range(length):
            resultlist.append(prefix + '\t[')
            parse(entry[3], typelist, prefix + '\t\t')
            resultlist.append(prefix +'\t]')
        resultlist.append( prefix + '}')
    elif dtype == 'string':
        strSingle = ''
        resultlist.append('')

        cursor = begin
        end    += 2
        while int(convertL2B(hexstr[begin:end]), 16) != 0 :
            strSingle += chr((int(convertL2B(hexstr[begin:end]), 16)))
            begin += 2
            end   += 2
        strTemp = "%s[%8s] -> %8s : %s" % (prefix, hexstr[cursor:end], entry[1], strSingle )
        begin += 2
        resultlist.append( strTemp )
    else:
        sys.exit("error type : " + dtype)
    
    return

def connectMysqlAndExcute( h, u, p, database, sql ):
	try:
		global hexstr
		conn=MySQLdb.connect(host=h, user=u, passwd=p, db=database)
		cur=conn.cursor()
		cur.execute(sql)
		hexstr=cur.fetchone()[0]
		cur.close()
		conn.close()
	except MySQLdb.Error, e: 
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])

if __name__=='__main__':

    if len(sys.argv) != 2:
    #if len(sys.argv) != 7:
        print 'Usage checkHex.py <opcode> <host> <user> <password> <db> <sql>'
        sys.exit()
    opcode = sys.argv[1]
    #connectMysqlAndExcute(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    if not sys.stdin.isatty():
        for line in sys.stdin:
            hexstr += line

    with open(filename,'r') as json_file:
        json_data = json.load( json_file )
        for key in json_data.keys():
            if opcode != key:
                continue
            parse( json_data[key], typelist )
            for t in resultlist:
                print t
