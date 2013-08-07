#!/usr/bin/env python3

import sys
import os
import re
import logging
from subprocess import Popen, PIPE, call

logger = logging.getLogger('spacman')

REPOS = ('community', 'core', 'extra', 'multilib')
ARCHITECTURES = ('i686', 'x86_64')
PACSEARCH = os.path.isfile('/usr/bin/pacsearch')
PACMATIC = os.path.isfile('/usr/bin/pacmatic')

pacman = PACMATIC and 'pacmatic' or 'pacman'


def get_urls(operation, packages):
    """return one url for each package

    operation: pacman operation; mostly -S
    packages: list of packages to install/update
    """

    args = ['pacman', operation, '--print'] + packages
    proc = Popen(args, shell=False, stdout=PIPE)
    result = proc.stdout.read().decode('utf-8').split(os.linesep)
    return (x for x in result
            if x.startswith('http') or x.startswith('ftp'))


def get_mirrors():
    with open('/etc/pacman.d/mirrorlist', encoding='utf-8') as fi:
        lines = (line.strip() for line in fi)
        for line in lines:
            if line.startswith('Server ='):
                yield line.strip('Server = ')


def get_downloadurls(url, mirrors):
    pattern = '^(http|ftp)://.*/(?P<repo>{0})/os/(?P<arch>{1})/(?P<pkgname>.*$)'.format(
        '|'.join(REPOS),
        '|'.join(ARCHITECTURES))
    logger.debug(pattern)
    m = re.search(pattern, url)

    if m:
        repo = m.group('repo')
        arch = m.group('arch')
        pkgname = m.group('pkgname')
        for mirror in mirrors:
            mirror = mirror.replace('$repo', repo)
            mirror = mirror.replace('$arch', arch)
            yield '{0}/{1}'.format(mirror, pkgname)
    else:
        yield url


def aria2c(urls):
    call([
        'aria2c',
        '--lowest-speed-limit=50K',
        '--continue',
        '--log-level=warn',
        '--max-concurrent-downloads=5',
        '--dir=/var/cache/pacman/pkg'] + urls)


def usage(sys):
    print('''{0} -S[ s | y | u |c ] package [package] ...
          long option names are currently not supported (e.g. -S --info)
          see pacman -h for more details.'''.format(sys.argv[0]))


def main():
    if len(sys.argv) < 2:
        usage(sys)
        return
    args_pacman = sys.argv[1:]
    args_packages = sys.argv[2:]
    operation = sys.argv[1]
    if '-h' in operation or '--help' in operation:
        usage(sys)
    elif '-Ss' in operation:
        if PACSEARCH:
            call(['pacsearch'] + args_packages)
        else:
            call(['pacman', '-Ss'] + args_packages)

    elif '-S' in operation and not (
            'i' in operation or 'p' in operation):
        urls = get_urls(operation, args_packages)
        mirrors = list(get_mirrors())
        for url in urls:
            aria2c(list(get_downloadurls(url, mirrors)))

        call(['sudo', pacman, operation.replace('y', '')] + args_packages)
    else:
        call([pacman] + args_pacman)


if __name__ == '__main__':
    main()
