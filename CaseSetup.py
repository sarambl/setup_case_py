# %%
import configparser
import glob
import shutil
from pathlib import Path
from subprocess import run
# %%

class CaseSetup:

    def __init__(self, path_folder, case_name):
        self.config_folder = path_folder
        pa = Path(path_folder)
        filen = pa / 'case_config.ini'

        config = configparser.ConfigParser()
        config.read(filen)
        config.sections()
        print('here')
        conf = config['CONFIG']
        self.conf = conf
        self.root_path = Path(conf.get('root'))
        case_root = self.root_path / Path(conf.get('CASEROOT'))
        case_path = case_root / case_name
        self.case_path = case_path

    def setup_case(self):
        conf = self.conf
        case_path = self.case_path
        compset = conf.get('COMPSET')
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
        RUN_TYPE=conf.get('RUN_TYPE')
        RUN_REFCASE=conf.get('RUN_REFCASE')
        RUN_REFDATE=conf.get('RUN_REFDATE')
        CAM_CONFIG_OPS_chem_mech_file=conf.get('CAM_CONFIG_OPS_chem_mech_file')
        print(queue_type)
        if queue_type is None:
            queue_type = 'normal'
        commands = []

        if str(queue_type) == 'devel':
            JOB_WALLCLOCK_TIME = '00:30:00'
            NTASKS_ESP = 1
            NUMNODES = -4
            REST_N = 4
            STOP_OPTION = 'ndays'
            commands.append(
                'sed -i \'s/<arg flag="-p" name="$JOB_QUEUE"/<arg flag="--qos" name="$JOB_QUEUE"/\' env_batch.xml')
        else:
            commands.append(
                'sed -i \'s/<arg flag="--qos" name="$JOB_QUEUE"/<arg flag="-p" name="$JOB_QUEUE"/\' env_batch.xml')
        if RUN_TYPE is not None:
            commands.append(f'./xmlchange RUN_TYPE={RUN_TYPE} --file env_run.xml')
        if RUN_REFCASE is not None:
            commands.append(f'./xmlchange RUN_REFCASE={RUN_REFCASE} --file env_run.xml')
        if RUN_REFDATE is not None:
            commands.append(f'./xmlchange RUN_REFDATE={RUN_REFDATE} --file env_run.xml')

        commands.append(f'./xmlchange STOP_OPTION={STOP_OPTION},STOP_N={STOP_N},REST_N={REST_N} --file env_run.xml')
        commands.append(f'./xmlchange JOB_WALLCLOCK_TIME={JOB_WALLCLOCK_TIME} --file env_batch.xml --subgroup case.run')
        if CAM_CONFIG_OPTS_append1 is not None:
            commands.append(f'./xmlchange --append CAM_CONFIG_OPTS={CAM_CONFIG_OPTS_append1} --file env_build.xml')
        if CAM_CONFIG_OPS_chem_mech_file is not None:
            commands.append(f'./xmlchange  --append CAM_CONFIG_OPTS="-usr_mech_infile \$CASEROOT/{CAM_CONFIG_OPS_chem_mech_file}" --file env_build.xml')
        commands.append(f'./xmlchange CALENDAR={CALENDAR} --file env_build.xml')
        commands.append(f'./xmlchange RUN_STARTDATE={RUN_STARTDATE} --file env_run.xml')
        commands.append(f'./xmlchange NTASKS={NUMNODES},NTASKS_ESP={NTASKS_ESP} --file env_mach_pes.xml')
        commands.append(f'./xmlchange --force JOB_QUEUE={queue_type} --file env_batch.xml')

        for com in commands:
            print(com)
            run(com, cwd=run_path, shell=True)

    def cp_code(self):
        conf = self.conf
        case_path = self.case_path
        if conf.get('pathChem') is not None and \
                conf.get('pathSourceMod') is not None:
            pathChem = self.root_path / Path(conf.get('pathChem'))
            comm = f'cp  {pathChem} {case_path}'
            print(comm)
            run(comm, shell=True)
        if conf.get('source_mod_path') is not None:
            pathSourceMod = self.root_path / Path(conf.get('pathSourceMod'))
            path_case_SourceMods = case_path / 'SourceMods/'
            comm = f'cp -r {pathSourceMod}/* {path_case_SourceMods}/'
            print(comm)
            run(comm, shell=True)
        return

    def run_setup(self):
        case_path = self.case_path
        comm = './case.setup'
        run(comm, cwd=case_path, shell=True)

    def setup_nl(self):
        config_path = Path(self.config_folder)
        case_path = self.case_path

        li_f = glob.glob(str(config_path) + '/*')
        for f in li_f:
            if 'user_nl_' in f:
                shutil.copy(f, case_path)

    def case_build(self):
        run_path = self.case_path
        comm = './case.build'
        run(comm, cwd=run_path, shell=True)

    def create_case_all_tasks(self):
        self.setup_case()
        self.do_xmlchanges()
        self.cp_code()
        self.run_setup()
        self.setup_nl()
        self.case_build()
        return
    # %%


# %%
if __name__ == '__main__':
    import sys

    args = sys.argv
    path_casefiles = Path(args[1])
    casename = path_casefiles.stem
    cs = CaseSetup(path_casefiles, casename)
# %%
    cs.create_case_all_tasks()
# %%