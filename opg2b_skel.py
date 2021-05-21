#!/usr/bin/env python3

__version__ = '1.0'
__author__  = '(c) 2019,2020 Frans Schippers (f.h.schippers@hva.nl) for SMP/Python'
__opgave__ = 'opg2b.py'

import sys, os
import getopt
import stat
import datetime
import json

# Student work {{
# Student work }}

def scan(fname, dname):
        """ De eigen schappen van de file worden opgehaald.
            Als het een directory is worden het programma recursief aangeroepen.
            Het is resultaat is een structuur met informatie over de file(s) bv een "list of dicts"
            Zorg dat de uiteindelijke return waarde van deze methode de informatie van alle files bevat.
        """
        fsInfos = {}
# Student work {{
# Student work }}
        return fsInfos

def show(fsInfo):
        """ Show toon te informatie van de verschillende files.
            Voor elke file wordt een beschrijven string gemaakt in de vorm van:
            fname:dir,dname:,mode:rwxr-xr-x,mtime:20200420113520,ino:8662408162,uid:501,gid:0,size:160
            Hierbij fnane, dname, mode, ... de tags en dir, , rwxr-xr-x, 20200420113520 de waarden.
            De retur waarde is een lijst van deze strings die de eigeschappen van de file beschrijven.
            Een lijst wordt teruggegeven en er wordt niet in de methode geprint.
            Dit om automatisch toesen mogelijk te maken
        """
        lines = []
# Student work {{
# Student work }}
        return lines

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
# Student work }}
    return errs

def load(fname):
    res = None
# Student work {{
# Student work }}
    return res

def dump(fsInfo, fname):
# Student work {{
# Student work }}
    return

def usage():
    print('Usage: {} -[?h] --scan <file.json> <dir>'.format(sys.argv[0],))
    print('Usage: {} -[?h] --show <file.json>'.format(sys.argv[0],))
    print('Usage: {} -[?h] --cmp <file1.json> <file2.json>'.format(sys.argv[0],))
    sys.exit()


if __name__ == '__main__':
# Voorbeeld gebruikt
# python3 opg2b_setup.py --clr dir
# python3 opg2b_setup.py --set dir
# python3 opg2b.py --scan scanOld.json dir
# python3 opg2b.py --show scanOld.json
# python3 opg2b_setup.py --mod dir
# python3 opg2b.py --scan scanNew.json dir
# python3 opg2b.py --show scanNew.json
# python3 opg2b.py --cmp scan1.json scan2.json

    # Handle the options and args
    cmd = ''
    opts, args = getopt.getopt(sys.argv[1:], '?h', ['show', 'scan', 'cmp'])
    for opt, arg in opts:
        if opt in [ '-?', '-h' ]:
            usage(); sys.exit()
        if opt in [ '--scan',  '--cmp', '--show' ]: cmd = opt[2:]

    # Scan and show the file-system trees
    if cmd == 'scan':
        if len(args) != 2:
            usage(); sys.exit()
        fsInfo = scan(args[1], '')
        dump(fsInfo, args[0])

    elif cmd == 'show':
        fsInfos = load(args[0])
        infos = show(fsInfos)
        for info in infos:
            print(info)

    elif cmd == 'cmp':
        if len(args) != 2:
            usage(); sys.exit()
        fsInfosOld = load(args[0])
        fsInfosNew = load(args[1])
        errs = cmp(fsInfosOld, fsInfosNew)
        for err in errs:
            print(err)
