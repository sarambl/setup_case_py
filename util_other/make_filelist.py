from subprocess import run
from pathlib import Path

# %%

def make_filelist_for_nudge(path_files,path_filelist = None,pattern='.h1'):
    if path_filelist is None:
        path_filelist = 'filelist.txt'
    p = Path(path_files)
    comm = f'ls -d -1 {p}/*{pattern}*.nc > {path_filelist}'
    print(comm)
    run(comm, shell=True)




if __name__ == '__main__':
    import sys

    args = sys.argv
    make_filelist_for_nudge(*args[1:])
