#!/usr/bin/env python3

import sys
import os
import getopt
import json

__version__ = '1.0'
__author__  = 'Peter Vissers, 500863381'
__opgave__ = 'opg2b.py'

def scan(fname, dname):
    """ De eigen schappen van de file worden opgehaald.
        Als het een directory is worden het programma recursief aangeroepen.
        Het is resultaat is een structuur met informatie over de file(s) bv een "list of dicts"
        Zorg dat de uiteindelijke return waarde van deze methode de informatie van alle files bevat.
    """
    fInfos = []
    fpath = os.path.join(dname, fname)
    sbuf = os.stat(fpath)
    fInfo = {'fname': fname, 'dname': os.path.dirname(fpath), 'mode': sbuf.st_mode, 'mtime': sbuf.st_mtime, 'ino': sbuf.st_ino, 'uid': sbuf.st_uid, 'gid': sbuf.st_gid, 'size': sbuf.st_size}
    fInfos.append(fInfo)

    if os.path.isdir(fpath):
        for fname in os.listdir(fpath):
            fInfos.extend(scan(fname, fpath))
    return fInfos


def show(fsInfo):
    """ Show toon te informatie van de verschillende files.
        Voor elke file wordt een beschrijven string gemaakt in de vorm van:
        fname:dir,dname:,mode:rwxr-xr-x,mtime:20200420113520,ino:8662408162,uid:501,uid:0,size:160
        Hierbij fnane, dname, mode, ... de tags en dir, , rwxr-xr-x, 20200420113520 de waarden.
        De retur waarde is een lijst van deze strings die de eigeschappen van de file beschrijven.
        Een lijst wordt teruggegeven en er wordt niet in de methode geprint.
        Dit om automatisch toesen mogelijk te maken
    """
    res = []
    for fInfo in fsInfo:
        keys = ['fname', 'dname', 'mode', 'mtime', 'ino', 'uid', 'gid', 'size']
        values = [fInfo.get(key) for key in keys]
        fileString = 'fname:' + str(values[0]) + ',dname:' + str(values[1]) + ',mode:' + str(values[2]) + ',mtime:' + str(values[3]) + ',ino:' + str(values[4]) + ',uid:' + str(values[5]) + ',gid:' + str(values[6]) + ',size:' + str(values[7])
    res.append(fileString)
    return res


def cmp(fsInfoOld, fsInfoNew):
    """ Compares to fsInfos
        return a list of error-strings.
        Format error-string:
            "A:<path>"
            "D:<path>"
            "M:<path>:<attr>:<oldVal>:<newVal>"
    """
    errs = []
# Student work {{
    print('DEBUG' + 'fsInfosOld', (fsInfosOld))
    print('second file')
    print('DEBUG' + 'fsInfosOld', (fsInfosNew))

  
# Student work }}
    return errs

def load(fname):
    res = None
    with open(fname) as file:
        res = json.load(file)
    return res

def dump(fsInfo, fname):
    with open(fname, "w") as jsonfile:
        json.dump(fsInfo, jsonfile, indent=4)

def usage():
    print('Usage: {} -[?h] --scan <file.json> <dir>'.format(sys.argv[0],))
    print('Usage: {} -[?h] --show <file.json>'.format(sys.argv[0],))
    print('Usage: {} -[?h] --cmp <file1.json> <file2.json>'.format(sys.argv[0],))
    sys.exit()


if __name__ == '__main__':

    # Handle the options and args
    cmd = ''
    opts, args = getopt.getopt(sys.argv[1:], '?h', ['show', 'scan', 'cmp'])
    for opt, arg in opts:
        if opt in ['-?', '-h']:
            usage()
            sys.exit()
        if opt in ['--scan', '--cmp', '--show']: cmd = opt[2:]

    # Scan and show the file-system trees
    if cmd == 'scan':
        if len(args) != 2:
            usage()
            sys.exit()
        fsInfo = scan(args[1], '')
        dump(fsInfo, args[0])

    elif cmd == 'show':
        fsInfos = load(args[0])
        infos = show(fsInfos)
        for info in infos:
            print(info)

    elif cmd == 'cmp':
        if len(args) != 2:
            usage()
            sys.exit()
        fsInfosOld = load(args[0])
        fsInfosNew = load(args[1])
        errs = cmp(fsInfosOld, fsInfosNew)
        for err in errs:
            print(err)
