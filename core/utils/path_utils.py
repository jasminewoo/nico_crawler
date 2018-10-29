import os


def get_root_prefix():
    prefix = ''
    cwd = os.getcwd().split('/')
    while cwd[-1] != 'nico_crawler':
        cwd = cwd[:-1]
        prefix += '../'
    return prefix
