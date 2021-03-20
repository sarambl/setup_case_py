from subprocess import run


def make_filelist_for_nudge(path_files,path_filelist = None,pattern='.h1'):
    if path_filelist is None:
        path_filelist = 'filelist.txt'
    comm = f'ls -d -1 {path_files}/*{pattern}*.nc > {path_filelist}'
    print(comm)
    run(comm, shell=True)




if __name__ == '__main__':
    import sys

    args = sys.argv
    make_filelist_for_nudge(*args[1:])
