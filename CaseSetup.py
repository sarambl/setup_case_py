# %%
import glob
import shutil
from pathlib import Path
from subprocess import run
import configparser

model_comps = ["ATM", "CPL", "OCN", "WAV", "GLC", "ICE", "ROF", "LND", "ESP"]
# %%
tetralith_purge_load_models = [
    "module purge",
    "module load buildenv-intel/2018.u1-bare ",
    "module load netCDF/4.4.1.1-HDF5-1.8.19-nsc1-intel-2018a-eb ",
    "module load HDF5/1.8.19-nsc1-intel-2018a-eb ",
    "module load PnetCDF/1.8.1-nsc1-intel-2018a-eb "]

def run_clean_env(run_path='/', comms = tetralith_purge_load_models):
    for co in comms:
        print(co)
        run(co,  shell=True, cwd=run_path)

def add_clean_env2comm(com):
    out = ' ;'.join(tetralith_purge_load_models) + '; ' + com
    return out

# %%
def test():
    # %%
    p = '/home/x_sarbl/NorESM/setup_case_py/example_case_tetralith5'#example/noresm2_pipd/LU2000/NF1850_aeroxid2014_LU2000_lospinup'
    pa = Path(p)
    print(pa.exists())
    casename = pa.stem
    path_folder = pa
    case_name = casename
    filen = pa / 'case_config.ini'
    config = configparser.ConfigParser()
    config.read(filen)
    config.sections()
    conf = config['CONFIG']
    # conf_ch = config['XMLCHANGE']
    # %%
    commands = []
    for sec in config.sections():
        if 'XMLCHANGE' in sec:
            confsec = config[sec]
            s_split = sec.split('/')
            print(s_split)
            ext = f' --file {s_split[-1]}'  # xml file to change
            if len(s_split) == 1:
                ext = ''
            if s_split[0] == 'XMLCHANGEapp':
                pre_com = './xmlchange --append '
            else:
                pre_com = './xmlchange '
            for key in confsec.keys():
                comm = f'{pre_com} {key.upper()}={confsec[key]} {ext}'
                commands.append(comm)
    # %%
    if 'XMLCHANGE' in config.sections():
        ss_xml=config['XMLCHANGE']
        for key in ss_xml:
            comm = f'./xmlchange {ss_xml[key]}'
            commands.append(comm)
    # %%




# %%
class CaseSetup:
    """
    Class for setting up cases
    """

    def __init__(self, path_folder, case_name):
        """
        Set parameters for case
        :param path_folder:
        :param case_name:
        """
        self.case_name = case_name
        self.config_folder = path_folder
        # Path where the case info lives:
        pa = Path(path_folder)
        # path to ini file (keeps xmlchanges)
        filen = pa / 'case_config.ini'

        print('Reading settings from: ',filen)
        config = configparser.ConfigParser()
        config.read(filen)
        config.sections()
        conf = config['CONFIG']
        self.config = config
        self.conf = conf
        if 'DIRS' in config.sections():
            # contains the paths to the rundir and archive
            # Used to copy init/restart files.
            dirs = config['DIRS']
            self.dirs = dirs
        else:
            self.dirs = None

        self.root_path = Path(conf.get('root'))
        case_root = self.root_path / Path(conf.get('CASEROOT'))
        case_path = case_root / case_name
        self.case_path = case_path

    def setup_case(self):
        """
        Run create_newcase with specified settings
        :return:
        """
        conf = self.conf
        case_path = self.case_path
        compset = conf.get('COMPSET', raw=True)
        mach = conf.get('MACH')
        self.mach = mach
        res = conf.get('RES')
        project = conf.get('PROJECT')
        misc = conf.get('MISC')
        #if mach =='tetralith':
        pecount = conf.get('PECOUNT')
        create_case = \
            f'./create_newcase ' \
            f'--case {case_path} ' \
            f'--compset {compset} ' \
            f'--res {res} ' \
            f'--mach {mach} '
        if mach=='tetralith':# is None:
            create_case = create_case +f' --pecount {pecount} ' \
                                       f'--project {project} '
        else:
            create_case = create_case + f' --project {project} '
        create_case = create_case + misc
        #f'--project {project} ' \
        #f'{misc}'
        print(create_case)

        _r = self.root_path / Path(conf.get('ModelRoot'))
        mod = str(conf.get('model'))
        run_path = _r / mod / 'cime/scripts'
        if mach=='tetralith':
            create_case = add_clean_env2comm(create_case)
        run(create_case, cwd=run_path, shell=True)
        #if mach=='tetralith':
        #    # clean environment and load appropriate modules:
        #    run_clean_env(run_path)

    def do_xmlchanges(self):
        """
        Do various xml-changes.
        :return:
        """
        conf = self.conf
        case_path = self.case_path
        run_path = case_path
        # various preset options which I have used.
        # much of the below options can instead be invoced by specifying
        # options under [XMLCHANGES/name_of_file.xml] which will then be run after
        STOP_OPTION = conf.get('STOP_OPTION')
        STOP_N = conf.get('STOP_N')
        JOB_WALLCLOCK_TIME = conf.get('JOB_WALLCLOCK_TIME')
        CAM_CONFIG_OPTS_append1 = conf.get('CAM_CONFIG_OPTS_append1')
        CALENDAR = conf.get('CALENDAR')
        RUN_STARTDATE = conf.get('RUN_STARTDATE')
        NUMNODES = conf.get('NUMNODES')
        NTASKS_ESP = conf.get('NTASKS_ESP')
        queue_type = conf.get('queue_type')
        REST_N = conf.get('REST_N')
        RUN_TYPE = conf.get('RUN_TYPE')
        RUN_REFCASE = conf.get('RUN_REFCASE')
        RUN_REFDATE = conf.get('RUN_REFDATE')
        CAM_CONFIG_OPS_chem_mech_file = conf.get('CAM_CONFIG_OPS_chem_mech_file')
        print(queue_type)
        if queue_type is None:
            queue_type = 'normal'
        # list of commands to be run:
        commands = []

        if str(queue_type) == 'devel' and self.mach =='fram':
            # appropriate time limit:
            JOB_WALLCLOCK_TIME = '00:30:00'
            NTASKS_ESP = 1
            NUMNODES = -4
            REST_N = 4
            STOP_OPTION = 'ndays'
            # stupid quickfix to use the development queue: replace line in file
            commands.append(
                'sed -i \'s/<arg flag="-p" name="$JOB_QUEUE"/<arg flag="--qos" name="$JOB_QUEUE"/\' env_batch.xml')
        else:
            # probably unnecessary:
            commands.append(
                'sed -i \'s/<arg flag="--qos" name="$JOB_QUEUE"/<arg flag="-p" name="$JOB_QUEUE"/\' env_batch.xml')


        if RUN_STARTDATE is not None:
            commands.append(f'./xmlchange RUN_STARTDATE={RUN_STARTDATE} --file env_run.xml')
        # xmlchanges to xml files. Preferably these can be set by specifying options under
        # [XMLCHANGES/env_*.xml], but these are kept for consistency with old cases.
        self._set_xmlchanges_old(CALENDAR, NTASKS_ESP, NUMNODES, REST_N, RUN_REFCASE, RUN_REFDATE, RUN_TYPE, STOP_N,
                                 STOP_OPTION, commands)

        # set wallclock:
        commands.append(f'./xmlchange JOB_WALLCLOCK_TIME={JOB_WALLCLOCK_TIME} --file env_batch.xml --subgroup case.run')
        # e.g. ./xmlchange --append CAM_CONFIG_OPTS=--offline_dyn:
        if CAM_CONFIG_OPTS_append1 is not None:
            commands.append(f'./xmlchange --append CAM_CONFIG_OPTS={CAM_CONFIG_OPTS_append1} --file env_build.xml')
        # Add chem_mech_infile
        if CAM_CONFIG_OPS_chem_mech_file is not None:
            commands.append(
                f'./xmlchange  --append CAM_CONFIG_OPTS="-usr_mech_infile \$CASEROOT/{CAM_CONFIG_OPS_chem_mech_file}" --file env_build.xml')

        commands.append(f'./xmlchange --force JOB_QUEUE={queue_type} --file env_batch.xml')


        for sec in self.config.sections():
            if 'XMLCHANGE' in sec:
                confsec = self.config[sec]
                s_split = sec.split('/')
                # xml file to change:
                ext = f' --file {s_split[-1]}'
                if len(s_split) == 1:
                    ext = ''
                if s_split[0] == 'XMLCHANGEapp':
                    pre_com = './xmlchange --append '
                else:
                    pre_com = './xmlchange '
                for key in confsec.keys():
                    comm = f'{pre_com} {key.upper()}={confsec[key]} {ext}'
                    commands.append(comm)

        # run all commands:
        for com in commands:
            print(com)
            run(com, cwd=run_path, shell=True)

        return

    def _set_xmlchanges_old(self, CALENDAR, NTASKS_ESP, NUMNODES, REST_N, RUN_REFCASE, RUN_REFDATE, RUN_TYPE, STOP_N,
                            STOP_OPTION, commands):
        """
        xmlchanges to xml files. Preferably these can be set by specifying options under
        [XMLCHANGES/env_*.xml], but these are kept for consistency with old cases.

        :param CALENDAR:
        :param NTASKS_ESP:
        :param NUMNODES:
        :param REST_N:
        :param RUN_REFCASE:
        :param RUN_REFDATE:
        :param RUN_TYPE:
        :param STOP_N:
        :param STOP_OPTION:
        :param commands:
        :return:
        """
        if RUN_TYPE is not None:
            commands.append(f'./xmlchange RUN_TYPE={RUN_TYPE} --file env_run.xml')
        if RUN_REFCASE is not None:
            commands.append(f'./xmlchange RUN_REFCASE={RUN_REFCASE} --file env_run.xml')
        if RUN_REFDATE is not None:
            commands.append(f'./xmlchange RUN_REFDATE={RUN_REFDATE} --file env_run.xml')
        if STOP_N is not None:
            commands.append(f'./xmlchange STOP_N={STOP_N} --file env_run.xml')
        if STOP_OPTION is not None:
            commands.append(f'./xmlchange STOP_OPTION={STOP_OPTION} --file env_run.xml')
        if REST_N is not None:
            commands.append(f'./xmlchange REST_N={REST_N} --file env_run.xml')
        if CALENDAR is not None:
            commands.append(f'./xmlchange CALENDAR={CALENDAR} --file env_build.xml')
        if NUMNODES is not None:
            commands.append(f'./xmlchange NTASKS={NUMNODES},NTASKS_ESP={NTASKS_ESP} --file env_mach_pes.xml')
        self.set_NTASKS()

    def cp_code(self):
        """
        If e.g. code needs to be copied, put here:
        :return:
        """
        conf = self.conf
        case_path = self.case_path
        # copy alternative chem_mech.in file
        if conf.get('pathChem') is not None and \
                conf.get('pathSourceMod') is not None:
            pathChem = self.root_path / Path(conf.get('pathChem'))
            comm = f'cp  {pathChem} {case_path}'
            print(comm)
            run(comm, shell=True)
        # copy sourcemods:
        if conf.get('pathSourceMod') is not None:
            pathSourceMod = self.root_path / Path(conf.get('pathSourceMod'))
            path_case_SourceMods = case_path / 'SourceMods/'
            comm = f'cp -r {pathSourceMod}/* {path_case_SourceMods}/'
            print(comm)
            run(comm, shell=True)
        return

    def run_setup(self):
        """
        run ./case.setup
        :return:
        """
        case_path = self.case_path
        comm = './case.setup'
        if self.mach=='tetralith':
            comm = add_clean_env2comm(comm)

        run(comm, cwd=case_path, shell=True)

    def setup_nl(self):
        """
        Copy namelists from case setup-folder
        :return:
        """
        config_path = Path(self.config_folder)
        case_path = self.case_path

        li_f = glob.glob(str(config_path) + '/*')
        for f in li_f:
            if 'user_nl_' in f:
                shutil.copy(f, case_path)

    def case_build(self):
        """
        Run ./case.build
        :return:
        """
        run_path = self.case_path
        comm = './case.build'
        if self.mach=='tetralith':
            comm = add_clean_env2comm(comm)

        run(comm, cwd=run_path, shell=True)

    def copy_init_restart(self):
        """
        Copy init/restart files and unpacks them
        :return:
        """
        RUN_REFCASE = self.conf.get('RUN_REFCASE')
        RUN_REFDATE = self.conf.get('RUN_REFDATE')
        if RUN_REFDATE is None:
            RUN_REFDATE = self.conf.get('RUN_STARTDATE')
        if RUN_REFCASE is None :
            if 'XMLCHANGE/env_run.xml' in self.config.sections():
                conf_envrun  = self.config['XMLCHANGE/env_run.xml']
                RUN_REFCASE = conf_envrun.get('RUN_REFCASE')
                if RUN_REFDATE is None:
                    RUN_REFDATE = conf_envrun.get('RUN_REFDATE')
                if RUN_REFDATE is None:
                    RUN_REFDATE = conf_envrun.get('RUN_STARTDATE')
        if RUN_REFCASE is None or RUN_REFDATE is None:
            return

        if self.dirs is None:
            return
        dirs = self.dirs
        archive_directory = dirs.get('archive_directory')
        run_directory = dirs.get('run_directory')
        if archive_directory is None or run_directory is None:
            return
        archive_directory = Path(archive_directory)
        run_directory = Path(run_directory)
        REFCASE_dir = dirs.get('REFCASE_dir')
        if REFCASE_dir is not None:
            archive_directory = Path(REFCASE_dir)
        path_restartcase = archive_directory / RUN_REFCASE
        path_rest = path_restartcase / f'rest/{RUN_REFDATE}-00000'
        path_run = run_directory / f'{self.case_name}/run/'

        comm = f'cp -rav {path_rest}/* {path_run}/'

        print(comm)
        run(comm, shell=True)
        comm_unpack = f'yes n | gunzip {RUN_REFCASE}.*.gz'
        print(comm_unpack)
        run(comm_unpack, cwd=path_run, shell=True)

        path_init_atm = archive_directory / RUN_REFCASE /'atm'/'hist'
        RUN_REFCASE=RUN_REFCASE.strip("'")
        RUN_REFDATE = RUN_REFDATE.strip("'")
        init_file_path = path_init_atm /f'{RUN_REFCASE}.cam.i.{RUN_REFDATE}-00000.nc'
        print(init_file_path)
        if init_file_path.exists():
            comm = f'cp -rav {init_file_path} {path_run}'
            run(comm, cwd=path_run, shell=True)

    def create_case_all_tasks(self):
        """
        Run all tasks to create, setup and build case.
        :return:
        """
        self.setup_case()
        self.do_xmlchanges()
        self.cp_code()
        self.run_setup()
        self.setup_nl()
        self.case_build()
        self.copy_init_restart()
        return

    def set_NTASKS(self):
        commands = []
        for comp in model_comps:
            ntasks = f'NTASKS_{comp}'
            conf = self.conf
            task_val = conf.get(ntasks)
            if task_val is not None:
                commands.append(f'./xmlchange {ntasks}={task_val} --file env_mach_pes.xml')

        case_path = self.case_path
        for com in commands:
            print(com)
            run(com, cwd=case_path, shell=True)


# %%
if __name__ == '__main__':
    import sys

    args = sys.argv
    path_casefiles = Path(args[1])
    casename = path_casefiles.stem
    cs = CaseSetup(path_casefiles, casename)
    cs.create_case_all_tasks()
# %%
