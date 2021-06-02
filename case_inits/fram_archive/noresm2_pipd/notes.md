## Computing indirect effect

### Conclusion:
- Run MET (NF1850_MMET) with init from N1850_f19_tn14_20190621 for 6 years - use 4 last years
    - compset: 1850_CAM60%NORESM%NORBC_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
- Run spinup PI (NF1850_spinup) for two years free meteorology
- Run spinup PI_AEROXID2014 (NF1850_aeroxid2014_spinup) for two years with free meteorology
    - compset: 1850_CAM60%NORESM%NORBC%AEROXID2014

**NUDGED RUNS**:
- PI:
    - noSECT_def (NF1850_noSECT_def)
    - SECT_ctrl (NF1850_SECT_ctrl)
    - (noSECT_ox_ricc (NF1850_noSECT_ox_ricc))
- PI_aeroxid2014:
     - noSECT_def (NF1850_aeroxid2014_noSECT_def)
     - SECT_ctrl (NF1850_aeroxid2014_SECT_ctrl)
     - noSECT_ox_ricc (NF1850_aeroxid2014_noSECT_ox_ricc)
     
### Ideas:




IDEA 1:
- RUN MET: run free meteorology pre-industrial case --> produce meteorology
- RUN PI: run nudged meteorology in pre-industrial conditions
- RUN PD: run nudged meteorology with pre-industrial cond but PD emissions of aerosols and oxidants. 


IDEA 2:
nudge to ERA-Interim meteorology
- RUN1: PD: already done 2008-2009 
- RUN2: PI: as RUN1 but with pre-industrial cond 
 
## compsets:
- NHISTpiaer
    - HIST_CAM60%NORESM%PIAER_CLM50%BGC-CROP_CICE%NORESM-CMIP6_BLOM%ECO_MOSART_SGLC_SWAV_BGC%BDRDDMS
    - <science_support grid="f19_tn14"/>
 - NHISTpiaeroxid
    - HIST_CAM60%NORESM%PIAEROXID_CLM50%BGC-CROP_CICE%NORESM-CMIP6_BLOM%ECO_MOSART_SGLC_SWAV_BGC%BDRDDMS
    - <science_support grid="f19_tn14"/>
 - Can I do:
    - HIST_CAM60%NORESM%PIAEROXID_CLM50%BGC-CROP_CICE%NORESM-CMIP6_BLOM%ECO_MOSART_SGLC_SWAV_BGC%BDRDDMS
    
- NFHISTnorbc_piaer
    - HIST_CAM60%NORESM%NORBC%PIAER_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
    - <science_support grid="f19_f19"/>
- NFHISTnorpibc
    - HIST_CAM60%NORESM%NORPIBC_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
    - <science_support grid="f19_f19"/>


what happens if I do:
- HIST_CAM60%NORESM%PIAEROXID_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
    - Build is ok... let's see if it runs. 
What about:
- 2000_CAM60%NORESM%PIAEROXID_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
    - Does not seem to work! Fields seem to be non-noresm. 
    
What about: 
- 1850_CAM60%NORESM%NORBC%AEROXID2014
    - Fields do not exist. 
vs
- 1850_CAM60%NORESM%NORBC


# Plan:
Run similar to 
- 1850_CAM60%NORESM%NORBC%AEROXID2014
vs 
- 1850_CAM60%NORESM%NORBC

Follow karset et al 2018:
- case: make_met (noSECTv21, compset PI)
- cases: PI_AEROXID2014 (SEC, noSEC) 
- case: PI (SEC, noSEC)

 
- make_met: run yrs 1-6(?)
spinup:
- spinup_PI_AEROXID2014: year 1-2
- spinup_PI: year 1-2

nudged to make_met:
- nudge_PI_AEROXID2014: year (3), 4-5 
- nudge_PI: year (3), 4-5

#