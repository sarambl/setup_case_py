from pathlib import Path
from subprocess import run
import glob
import os


def nc3to4(dir_in, dir_out, pattern):
    """
    Convert netcdf4 in folder to netcdf 3 in another folder
    :param dir_in: directory with input
    :param dir_out: directory for output
    :param pattern: e.g. '.h1.'
    :return:
    """
    dir_in = Path(dir_in)
    dir_out = Path(dir_out)
    if not dir_out.exists():
        os.makedirs(dir_out)
    fl = glob.glob(str(dir_in) + f'/*{pattern}*.nc')
    cmm_ls = []
    for f in fl:
        f_out = dir_out / Path(f).name
        cmm_ls.append(f'ncks -3 {f} {f_out}')
    for cmm in cmm_ls:
        run(cmm, shell=True)
    return


if __name__ == '__main__':
    import sys

    args = sys.argv
    dir_input = args[1]
    dir_output = args[2]
    patt = args[3]
    nc3to4(dir_input, dir_output, patt)
