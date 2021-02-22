import sys
import logging
import time
import json
from types import SimpleNamespace

from notifier import TelegramNotifier
from server import Server
from utils import htimeToSeconds

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("srvmon")


class ServerMon:
    def __init__(self, conf):
        self.conf = conf
        self.servers = []
        for x in conf.servers:
            self.servers.append(Server(x))

        self.telegramNotifier = TelegramNotifier(self.conf.notification.telegram.token, self.conf.notification.telegram.chatIds)

    def isCheckEnabled(self, server, chname):
        if chname in self.conf.checks.default:
            return True 
        if chname in server.checks:
            return True
        return False

    def run(self):
        logger.info('srvmon started')
        self.telegramNotifier.sendMessage('srvmon is started')

        i = 0

        while True:
            alerts, reports = self.runStep()
            
            print (alerts, reports)

            if i % self.conf.reportEvery == 0:
                rep = self.generateReport(reports)
                print (rep)
                self.telegramNotifier.sendMessage(rep)

            i += 1
            time.sleep(htimeToSeconds(self.conf.checkInterval))

    def generateReport(self, r):
        rs = ""

        for x in r:
            rs += 'Server %s - %s\n' % (x['server'].host, x['server'].name)
            if 'ping' in x:
                if x['ping'][0] == False:
                    rs += '\tServer is unreachable!\n\n'
                    continue
                rs += '\tPing: %s\n' % (x['ping'][1])
            if 'mem' in x:
                rs += '\tMem: %d%% used\n' % (int(x['mem']['percentage']))

            rs += '\n'

            if 'containers' in x:
                for c in x['containers']:
                    rs += '%s - %s (%s, %s):\n' % (c['id'], c['name'], c['status'], c['ip'])
                    if 'mem' in c:
                        rs += '\tMem: %d%% used\n' % (int(c['mem']['percentage']))
                    if 'disk' in c:
                        rs += '\tDisk: %d%% used\n' % (int(c['disk']))
                    rs += '\n'

        return rs

    def runStep(self):
        alerts = []
        reports = []

        for s in self.servers:
            a, r = self.checkServer(s)

            alerts += a 
            reports.append(r)

        return (alerts, reports)

                
    def checkServer(self, s):
        r = {'server': s}
        alerts = []

        if self.isCheckEnabled(s, 'ping'):
            up, ms = s.ping()

            if not up:
                alerts.append((s, 'ping', 'host is down'))

            r['ping'] = (up, ms)


        if self.isCheckEnabled(s, 'mem'):
            f = s.free()

            r['mem'] = f

        if self.isCheckEnabled(s, 'proxmox-containers'):
            ct = s.pmListContainers()
            ctn = []

            for x in ct:
                if x['status'] == 'running':
                    if 'mem' in self.conf.checks.containerDefault:
                        x['mem'] = s.pmFree(x['id'])

                if 'disk' in self.conf.checks.containerDefault:
                    x['disk'] = s.pmDf(x['id'])

                ctn.append(x)


            r['containers'] = ctn

        return (alerts, r)

def main():
    conf = json.loads(open(sys.argv[1], 'r').read(), object_hook=lambda d: SimpleNamespace(**d))

    sm = ServerMon(conf)
    sm.run()


if __name__ == "__main__":
    main()