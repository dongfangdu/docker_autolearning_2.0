# -*- coding; utf8 -*-

import os


def restart_server():
    sudoPassword = 'yjyjs123'
    command = 'sh ./bin/alisr-ctrl.sh restart'
    p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))


if __name__ == '__main__':
    restart_server()
