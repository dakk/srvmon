import subprocess 

def removeEmptyStrings(l):
    return list(filter(None, l))

def parseFree(r):
    """ Given free output, returns [total, used, free, percentage] """
    r = r.split('\n')[1]
    r = removeEmptyStrings(r.split(' '))
        
    return { 'total': int(r[1]), 'used': int(r[2]), 'free': int(r[3]), 'percentage': 100 * int(r[2]) / int(r[1]) }


class Server:
    def __init__(self, sconf):
        self.name = sconf.name if hasattr(sconf, 'name') else sconf.host
        self.host = sconf.host 
        self.user = sconf.user if hasattr(sconf, 'user') else 'root'
        self.checks = sconf.checks if hasattr(sconf, 'checks') else []
        self.sconf = sconf

    def ping(self):
        try:
            r = subprocess.check_output(['ping', self.host, '-q', '-c2']).decode("utf-8") 
            if r.find('100% packet loss') != -1:
                return (False, 0)
            else:
                return (True, r.split('time ')[1].split('\n')[0])
        except:
            return (False, 0)

    def executeCommand(self, cmd):
        return subprocess.check_output(['ssh', self.user + '@' + self.host] + cmd).decode("utf-8") 

    def free(self):
        return parseFree(self.executeCommand(['free']))


    # Proxmox specific actions
    def pmListContainers(self):
        rnet = {}
        for x in self.executeCommand(['grep', '-R', "\'net[0-9]*\'", '/etc/pve/lxc/']).split('\n'):
            try:
                rnet[x.split('/etc/pve/lxc/')[1].split('.')[0]] = x.split('ip=')[1].split('/')[0]
            except:
                pass


        r = self.executeCommand(['pct', 'list']).split('\n')[1::]
        lr = []
        for x in r:
            line = removeEmptyStrings(x.split(' '))

            if len(line) > 1:
                lr.append({'id': line[0], 'status': line[1], 'name': line[2], 'ip': rnet[line[0]]})
        return lr

    def pmExecuteCommandInContainer(self, ct, cmd):
        return self.executeCommand(['pct', 'exec', ct, '--', 'bash', '-c', '"' + cmd + '"'])

    def pmDf(self, ct):
        return int (float(removeEmptyStrings(self.executeCommand(['pct', 'df', ct]).split('\n')[1].split(' '))[5]) * 100.)

    def pmFree(self, ct):
        cd = self.pmExecuteCommandInContainer(ct, 'free')
        return parseFree(cd)
