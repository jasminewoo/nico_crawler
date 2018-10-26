import os


def get_resource_fp(path):
    prefix = ''
    cwd = os.getcwd().split('/')
    while cwd[-1] != 'nico_crawler':
        cwd.remove(cwd[-1])
        prefix += '../'
    return open(prefix + 'tests/resources/' + path.strip('/'), 'r')
