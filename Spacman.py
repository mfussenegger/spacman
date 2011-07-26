#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import subprocess
from Reflector import MirrorStatus

PACSEARCH = os.path.isfile('/usr/bin/pacsearch')


def get_urls(operation, args_packages):
    proc = subprocess.Popen(['pacman', operation, '--print'] + args_packages,
            shell=False, stdout=subprocess.PIPE)
    result = proc.stdout.read().decode('utf-8').split(os.linesep)
    urls = [x for x in result \
            if x.startswith('http') or x.startswith('ftp')]
    return urls

def get_mirrors(use_reflector = False):
    if use_reflector:
        return get_mirrors_reflector()
    return get_mirrors_mirrorlist()

def get_mirrors_reflector():
    ms = MirrorStatus()
    mirrors = ms.get_mirrors()
    mirrors = ms.sort(mirrors, 'age')
    mirrors = mirrors[:20]
    mirrors = ms.sort(mirrors, 'rate')
    return [ MirrorStatus.MIRROR_URL_FORMAT.format(x['url'], '$repo', '$arch') for x in mirrors ]

def get_mirrors_mirrorlist():
    mirrors = []
    with open('/etc/pacman.d/mirrorlist', encoding='utf-8') as fi:
        for line in fi:
            mirrors.append(line.rstrip())
    return [x.strip('Server = ') for x in mirrors \
            if x.startswith('Server =')]

#    proc = subprocess.Popen(['reflector', '-l', '20', '--sort', 'rate'],
#            stdout=subprocess.PIPE)
#    result = proc.stdout.read().decode('utf-8').split(os.linesep)
#    mirrors = [x.strip('Server = ') for x in result \
#            if x.startswith('Server = ')]
#    return mirrors

def get_downloadurls(url, mirrors):
    pattern = '^(http|ftp)://.*/(?P<repo>{0})/os/(?P<arch>{1})/(?P<pkgname>.*$)'.format(
            '|'.join(MirrorStatus.REPOSITORIES),
            '|'.join(MirrorStatus.ARCHITECTURES))
    m = re.search(pattern, url)
    repo = m.group('repo')
    arch = m.group('arch')
    pkgname = m.group('pkgname')
    for mirror in mirrors:
        mirror = mirror.replace('$repo', repo)
        mirror = mirror.replace('$arch', arch)
        yield '{0}/{1}'.format(mirror, pkgname)

def aria2c(urls):
    subprocess.call([
        'aria2c',
        '--lowest-speed-limit=50K',
        '--continue',
        '--log-level=warn',
        '--max-concurrent-downloads=5',
        '--dir=/var/cache/pacman/pkg'] + urls)

def main():
    args_pacman = sys.argv[1:]
    args_packages = sys.argv[2:]
    operation = sys.argv[1]
    if '-h' in operation or '--help' in operation:
        print('''{0} -S[ s | y | u |c ] package [package] ...

                long option names are currently not supported (e.g. -S --info)
                see pacman -h for more details.'''.format(sys.argv[0]))

    elif '-Ss' in operation:
        if PACSEARCH:
            retcode = subprocess.call(['pacsearch'] + args_packages)
        else:
            retcode = subprocess.call(['pacman', '-Ss'] + args_packages)

    elif '-S' in operation and not ( \
            'i' in operation or 'p' in operation):
        urls = get_urls(operation, args_packages)
        mirrors = get_mirrors()
        for url in urls:
            aria2c(list(get_downloadurls(url, mirrors)))

        retcode = subprocess.call(['pacman', operation.replace('y', '')] + args_packages)
    else:
        retcode = subprocess.call(['pacman'] + args_pacman)

if __name__ == '__main__':
    main()
