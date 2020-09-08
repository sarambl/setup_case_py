# %%
import glob
import shutil
from pathlib import Path
from subprocess import run
import configparser

# %%
class CaseSetup:

    def __init__(self, path_folder, case_name):
        self.case_name=case_name
        self.config_folder = path_folder
        pa = Path(path_folder)
        filen = pa / 'case_config.ini'
        config = configparser.ConfigParser()
        config.read(filen)
        config.sections()
        conf = config['CONFIG']
        self.conf = conf
        if 'DIRS' in config.sections():
            dirs = config['DIRS']
            self.dirs = dirs
        else:
            self.dirs=None

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
        compset = conf.get('COMPSET',raw=True)
        mach = conf.get('MACH')
        res = conf.get('RES')
        project = conf.get('PROJECT')
        misc = conf.get('MISC')
        create_case = \
            f'./create_newcase ' \
            f'--case {case_path} ' \
            f'--compset {compset} ' \
            f'--res {res} ' \
            f'--mach {mach} ' \
            f'--project {project} ' \
            f'{misc}'
        print(create_case)

        _r = self.root_path / Path(conf.get('ModelRoot'))
        mod = str(conf.get('model'))
        run_path = _r / mod / 'cime/scripts'
        run(create_case, cwd=run_path, shell=True)

    def do_xmlchanges(self):
        """
        Do various xml-changes.
        :return:
        """
        conf = self.conf
        case_path = self.case_path
        run_path = case_path
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

        if str(queue_type) == 'devel':
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

        if RUN_TYPE is not None:
            commands.append(f'./xmlchange RUN_TYPE={RUN_TYPE} --file env_run.xml')
        if RUN_REFCASE is not None:
            commands.append(f'./xmlchange RUN_REFCASE={RUN_REFCASE} --file env_run.xml')
        if RUN_REFDATE is not None:
            commands.append(f'./xmlchange RUN_REFDATE={RUN_REFDATE} --file env_run.xml')

        commands.append(f'./xmlchange STOP_OPTION={STOP_OPTION},STOP_N={STOP_N} --file env_run.xml')
        if REST_N is not None:
            commands.append(f'./xmlchange REST_N={REST_N} --file env_run.xml')
        # set wallclock:
        commands.append(f'./xmlchange JOB_WALLCLOCK_TIME=00:30:00 --file env_batch.xml')
        commands.append(f'./xmlchange JOB_WALLCLOCK_TIME={JOB_WALLCLOCK_TIME} --file env_batch.xml --subgroup case.run')
        # e.g. ./xmlchange --append CAM_CONFIG_OPTS=--offline_dyn:
        if CAM_CONFIG_OPTS_append1 is not None:
            commands.append(f'./xmlchange --append CAM_CONFIG_OPTS={CAM_CONFIG_OPTS_append1} --file env_build.xml')
        # Add chem_mech_infile
        if CAM_CONFIG_OPS_chem_mech_file is not None:
            commands.append(
                f'./xmlchange  --append CAM_CONFIG_OPTS="-usr_mech_infile \$CASEROOT/{CAM_CONFIG_OPS_chem_mech_file}" --file env_build.xml')
        if CALENDAR is not None:
            commands.append(f'./xmlchange CALENDAR={CALENDAR} --file env_build.xml')
        if RUN_STARTDATE is not None:
            commands.append(f'./xmlchange RUN_STARTDATE={RUN_STARTDATE} --file env_run.xml')
        commands.append(f'./xmlchange NTASKS={NUMNODES},NTASKS_ESP={NTASKS_ESP} --file env_mach_pes.xml')
        commands.append(f'./xmlchange --force JOB_QUEUE={queue_type} --file env_batch.xml')

        # run all commands:
        for com in commands:
            print(com)
            run(com, cwd=run_path, shell=True)

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
        run(comm, cwd=run_path, shell=True)
    def copy_init_restart(self):
        RUN_REFCASE = self.conf.get('RUN_REFCASE')
        RUN_REFDATE= self.conf.get('RUN_REFDATE')
        if RUN_REFCASE is None or self.dirs is None:
            return
        dirs=self.dirs
        archive_directory = dirs.get('archive_directory')
        run_directory = dirs.get('run_directory')
        if archive_directory is None or run_directory is None:
            return
        archive_directory = Path(archive_directory)
        run_directory=Path(run_directory)
        REFCASE_dir = dirs.get('REFCASE_dir')
        if REFCASE_dir is not None:
            archive_directory = Path(REFCASE_dir)
        path_restartcase = archive_directory / RUN_REFCASE
        path_rest = path_restartcase /f'rest/{RUN_REFDATE}-00000'
        path_run=run_directory/f'{self.case_name}/run/'

        comm = f'cp -rav {path_rest}/* {path_run}/'
        print(comm)
        run(comm, shell=True)
        comm_unpack=f'gunzip {RUN_REFCASE}.*.gz'
        print(comm_unpack)
        run(comm_unpack, cwd=path_run, shell=True)

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


# %%
if __name__ == '__main__':
    import sys

    args = sys.argv
    path_casefiles = Path(args[1])
    casename = path_casefiles.stem
    cs = CaseSetup(path_casefiles, casename)
    cs.create_case_all_tasks()
# %%
