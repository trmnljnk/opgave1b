# Tested on Linux Debian Python 3.7.3
# Tested on Macos Python 3.8.2
import sys, os
import stat
import getopt
import shutil
import time, datetime

gHandleSymlinks = True

ruid, rgid = 501, 20
try: # Windows doesn't support geteuid
    gHandleSymlinks = False
    ruid = os.getuid()
    rgid = os.getgid()
    euid = os.geteuid()
except:
    euid = ruid

import platform
if ruid == 0 and platform.system() == 'Darwin':
    # Macos doesn't honor getuid rightful
    from pwd import getpwnam
    pwent = getpwnam(os.getlogin())
    ruid = pwent.pw_uid; rgid = pwent.pw_gid

_fmt = '%Y%m%d%H%M%S'
def ts2str(ts):
    return datetime.datetime.fromtimestamp(ts).strftime(_fmt)
def str2ts(s):
    return (datetime.datetime.strptime(s, _fmt)-datetime.datetime.fromtimestamp(0)).total_seconds()

filesSet = {
    '': {
        'type': 'd', 'mode': 0o0755, },
    'file1': {
        'type': '-', 'mode': 0o0644, 'data': 'text\n' },
    'file2': {
        'type': '-', 'mode': 0o0440, 'data': 'texttext' },
    'file3': {
        'type': '-', 'mode': 0o0750, 'data': '#!/bin/bash\necho "hallo"\n' },
    'dir1': {
        'type': 'd', 'mode': 0o0750, },
    'dir1/file11': {
        'type': '-', 'mode': 0o0644, 'data': 'file11' },
    'dir2': {
        'type': 'd', 'mode': 0o511, },
    'dir2/file21': {
        'type': '-', 'mode': 0o0644, 'data': 'file11' },
}

filesSetExtra = {
    'dir1/slnk': {
        'type': 'l', 'mode': 0o0644, 'slnk': 'dir1/file11' },
    'dev': {
        'type': 'd', 'mode': 0o0750, },
    'dev/zero': {
        'type': 'c', 'mode': 0o0644, 'maj': 3, 'min': 3, 'uid': 0, 'gid': 0, 'super': True },
}

filesMod = {
    'file1': { 'action': 'd' },
    'file4': { 'action': 'a' ,
        'type': '-', 'mode': 0o0644, 'data': 'text' },
    'dir2/file21': { 'action': 'm',
        'mode': 0o1644, 
        'atime': str2ts('20200513000000'),
        'mtime': str2ts('20200514000000'),
        'ctime': None,
        'size': 10,
        'uid': 502,
        'gid': 503,
        'data': None,
    },
    'file3': { 'action': 'm' ,
        'type': '-', 'mode': 0o4755, 'data': '#!/bin/bash\neco "HALLO"\n"',
        'mtime': None, 'ctime': None},
}
filesModExtra = {
}

def mkFile(dname, fname, fileInfo):
    _fname = os.path.join(dname, fname)
    if fileInfo['type'] == '-':
        with open(_fname, 'w') as fp:
            fp.write(fileInfo['data'])
    elif fileInfo['type'] == 'd':
        os.mkdir(_fname)
    elif fileInfo['type'] == 'l':
        _sname =  os.path.join(dname, fileInfo['slnk'])
        os.symlink(_sname, _fname)
    elif fileInfo['type'] == 'f':
        os.mkfifo(_fname)
    elif fileInfo['type'] == 'c':
        if euid == 0: # Can only peformed as root
            os.mknod(_fname, stat.S_IFCHR, os.makedev(fileInfo['maj'], fileInfo['min']))
    elif fileInfo['type'] == 'b':
        if euid == 0: # Can only peformed as root
            os.mknod(_fname, stat.S_IFBLK, 0)
    else:
        raise NotImplementedError

    if os.path.lexists(_fname):
        if fileInfo.get('mode') is not None:
            if gHandleSymlinks:
                os.chmod(_fname, fileInfo['mode'], follow_symlinks=False)
            elif fileInfo.get('type') not in [ 'd', 'l']:
                os.chmod(_fname, fileInfo['mode'])

        if euid == 0: # Can only peformed as root
            uid = fileInfo['uid'] if fileInfo.get('uid') is not None else ruid
            gid = fileInfo['gid'] if fileInfo.get('gid') is not None else rgid
            if gHandleSymlinks:
                os.chown(_fname, uid, gid, follow_symlinks=False)
            elif fileInfo.get('type') not in [ 'l']:
                os.chown(_fname, uid, gid)

def rmAll(dname):
    if os.path.isdir(dname) and not os.path.islink(dname):
        os.chmod(dname, 0o755)
        for fname in os.listdir(dname):
            rmAll(os.path.join(dname, fname))
        os.rmdir(dname)
    else:
        os.unlink(dname)

def setupClr(dname):
    if os.path.exists(dname):
        rmAll(dname)

def setupSet(dname, files):
    if os.path.exists(dname):
        print('Error: Existing directory:{}'.format(dname))
        return

    for fname in sorted(files):
        mkFile(dname, fname, files[fname])
    # Set mode for directory strict, after all files are created
    for fname in sorted(files, reverse=True):
        if files[fname].get('type') == 'd':
            _fname = os.path.join(dname, fname)
            if gHandleSymlinks:
                os.chmod(_fname, files[fname]['mode'], follow_symlinks=False)
            else:
                os.chmod(_fname, files[fname]['mode'])

def setupMod(dname, files):
    time.sleep(1)
    for fname in sorted(files):
        fileInfo = files[fname]
        _fname = os.path.join(dname, fname)
        if fileInfo['action'] == 'd':
            os.unlink(_fname)
            if gVbs: print('D:{}'.format(_fname))
            continue
        elif fileInfo['action'] == 'a':
            mkFile(dname, fname, fileInfo)
            if gVbs: print('A:{}'.format(_fname))
            continue

        # Sequence is important
        sbuf = os.lstat(_fname)

        if fileInfo.get('size'):
            _buf = open(_fname, 'r').read(); open(_fname, 'w').write('@'*fileInfo['size']) 
            _sbuf = os.lstat(_fname)
            if gVbs: print('M:{}:size:{}:{}'.format(_fname, sbuf.st_size, _sbuf.st_size))

        if fileInfo.get('data') is not None:
            with open(_fname, 'w') as fp:
                fp.write(fileInfo['data'])
        
        if fileInfo.get('uid') or fileInfo.get('gid'):
            uid = fileInfo.get('uid', -1)
            gid = fileInfo.get('gid', -1)
            if euid == 0: # Can only peformed as root
                if gHandleSymlinks:
                    os.chown(_fname, uid, gid, follow_symlinks=False)
                elif fileInfo.get('t') not in [ 'l' ]:
                    os.chown(_fname, uid, gid)
                _sbuf = os.lstat(_fname)
                if 'uid' in fileInfo:
                    if gVbs: print('M:{}:uid:{}:{}'.format(_fname, sbuf.st_uid, _sbuf.st_uid))
                if 'gid' in fileInfo:
                    if gVbs: print('M:{}:gid:{}:{}'.format(_fname, sbuf.st_gid, _sbuf.st_gid))

        if fileInfo.get('mode'):
            if gHandleSymlinks:
                os.chmod(_fname, fileInfo['mode'], follow_symlinks=False)
            elif fileInfo.get('type') not in [ 'f' ]:
                os.chmod(_fname, fileInfo['mode'])
            _sbuf = os.lstat(_fname)
            if gVbs: print('M:{}:mode:{}:{}'.format(_fname,
                stat.filemode(sbuf.st_mode)[1:], stat.filemode(_sbuf.st_mode)[1:]))

        if fileInfo.get('ino'):
            # Not implemented
            # os.unlink(_fname)
            # mkFile(dname, fname, fileInfo)
            pass

        if fileInfo.get('atime') or fileInfo.get('mtime'):
            atime = fileInfo.get('atime', sbuf.st_atime)
            mtime = fileInfo.get('mtime', sbuf.st_mtime)
            os.utime(_fname, times=(atime, mtime))
            _sbuf = os.lstat(_fname)

            if fileInfo.get('mtime'):
                if gVbs: print('M:{}:atime:{}:{}'.format(_fname, ts2str(sbuf.st_atime), ts2str(_sbuf.st_atime)))
            if fileInfo.get('atime'):
                if gVbs: print('M:{}:mtime:{}:{}'.format(_fname, ts2str(sbuf.st_mtime), ts2str(_sbuf.st_mtime)))
                
def usage():
    print('Usage: {} -[Vhe] [--clr|--set|--mod] <dir>'.format(sys.argv[0]))
    sys.exit()

gVbs = True
if __name__ == '__main__':
    cmd = ''; extra = False
    opts, args = getopt.getopt(sys.argv[1:], '?hVe', ['clr', 'set', 'mod'])
    for opt, arg in opts:
        if opt == '-h': usage()
        if opt == '-V': gVbs = True
        if opt == '--clr': cmd = 'clr'
        if opt == '--set': cmd = 'set'
        if opt == '--mod': cmd = 'mod'
        if opt == '-e': extra = True

    if len(args) != 1:
        usage()

    if extra:
        filesSet.update(filesSetExtra)
        filesMod.update(filesModExtra)

    if cmd == 'clr':
        setupClr(args[0])
    if cmd == 'set':
        setupSet(args[0], filesSet)
    if cmd == 'mod':
        setupMod(args[0], filesMod)
