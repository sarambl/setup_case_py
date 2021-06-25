# Run setup:

## spinup:
Use my old case: spinup_freemet_from2000 from 2007-01-01 as 
init file. Spin up until 2008-07-01.

2008-07-01 to 2009-01-01 is spinup. 

Spinup case name: CTRL_stlznrg_spinup. Only change to original code is 
nudging fix and dry deposition fix. 


## Cases:

Idea: 
- CTRL
    - SECT
    - noSECT
- noOrgLeh -- no organics in lehtinen parameterization
    - SECT
    - noSECT
- noOrg10 -- no organics condense below 10 nm 
    - SECT
- noOrg25
    - SECT
- noOrg39
    - SECT
- noNuc -- no nucleation at all. ¶
    - SECT
    - noSECT