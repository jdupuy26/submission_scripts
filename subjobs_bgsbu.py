#!/usr/bin/env python

import os 
import errno
import shutil
import subprocess
import socket as s
comp = s.gethostname()

#===============================================================
#
#  Code: subjobs_sys.py
#
#  Purpose: Submit jobs to explore parameter space 
#            of HVC sims. This file will edit athinput
#            so that different HVC parameters can be input 
#
#  Usage: python subjobs_sys.py  
#          
#  Author: John Dupuy (based heavily of cfrazer's sub script)
#          UNC Chapel Hill
#  Date:    11/12/17
#  Updated: 12/13/17
#==============================================================

def main():
    rootrundir = os.getcwd() + '/'
    # Right now -> restart starts @ 250 Myr

    # Machine specific parameters 
    if 'dogwood' in comp:     # if using dogwood
        base    = '/nas/longleaf/home/jdupuy26/'
        restart = base+'restart_files/bar.0001.rst'
        queue   = '528_queue'
            # Cooltable location
        cooltable = base+'gainloss.dmp'
            # SII Table location
        siitable  = base+'siiemission.bin'

    elif 'killdevil' in comp: # if using killdevil
        base    = '/nas02/home/j/d/jdupuy26/'
        restart = base+'restart_files/bar.0001.rst' 
        queue   = 'mpi'
            # Cooltable location
        cooltable = base+'gainloss.dmp'
        siitable  = base+'siiemission.bin' 
    
    else:
        print("[main]: Computer %s not recognized!" %comp)
        quit()
    
    # Start defining default parameters
    num_domains = 1
    
    # <output>
    maxout      = '6'
    dtbin       = '10.0'
    dthst       = '1'
    dtrst       = '200'
    dtlv        = '20.0'
    dtsii       = '20.0'
    dtotf       = '2.5'

    # <time>
    CourNo      = '0.20'
    tlim        = '1000'

    # <domain1>
    ilog        = '1'
    x1rat       = '1.015'
    Nx1         = '256'
    x1min       = '10'
    x1max       = '5000'

    Nx2         = '256'
    x2min       = '0.0'
    x2max       = '6.28318530718'

    NGrid_x1    = '8'
    NGrid_x2    = '8'

    # <problem>
    mu          = '1.0'
    gamma       = '1.666666667'
    Pgas0       = '577.899'
    scaleh      = '300.0'
    da          = '10.0'
    aval        = '1200.0'
    iso_csound  = '10.22'
    ieta1       = '1e-3'  # not used in current formulation of dual energy
    ieta2       = '1e-12' # set to low value to not influence results 

        # bar parameters
    ibar        = '1'
    omg         = '0.064424'
    Nq          = '30'
    qend        = '0.75'
    tstart      = '5'
    tend        = '155'

        # HVC parameters
    ihvc        = '0'
    thvcs       = '305'
    thvce       = ['325']
    mhvc        = ['0']
    mhvc        = ['1e6','1e7','5e7','1e8']
    rhvc        = ['100','500','1000']
    #rpos        = ['1000']
    #ahvc        = ['0.0','1.571']
    facvhvc     = ['1.0']
    #rhvc        = ['200','400','600','800']
    rpos        = ['1000','2000','3000']
    ahvc        = ['0.0','1.5708']
    #facvhvc     = ['0.0','1.0','2.0']
    
        # HVC Analysis
    rcirc       = '300'
    Nang        = '8'

        # Metallicity variables
    dm          = '-0.05'
    lm0         = '0.45'
    imet        = '1'
    Ncol        = '1.e18'
        # LV OTF analysis
    Rsun        = '8000'
    vsun        = '225'
    p0          = '160'
    minl        = '-20'
    maxl        = '20'
    dl          = '0.1'
    dvscan      = '1.5'
    dr          = '1.0'

        # SII Emission analysis 
    isii        = '0'
    minx        = '-1500'
    maxx        = '1500'
    dx          = '5'
    miny        = '-1000'
    maxy        = '1000'
    dy          = '5'

       # End of parameters 

    # Compute job number
    jobno = len(mhvc)*len(thvce)*len(rhvc)*len(rpos)*len(ahvc)*len(facvhvc)
    # Compute no. of proc required 
    procpjob = int(NGrid_x1)*int(NGrid_x2)

    # Now loop through parameters and start making run directories
    i = 0
    for m in mhvc:
        for te in thvce:
            for rc in rhvc:
                for r in rpos:
                    for a in ahvc:
                        for fac in facvhvc:
                            i += 1
                            rundir  = rootrundir+'m'+m+'/te'+te+'/rc'+rc+'/r'+r+'/a'+a+'/fac'+fac+'/'
                            jobname = 'm'+m+'te'+te+'rc'+rc+'r'+r+'a'+a+'fac'+fac 

                            if not os.path.exists(rundir):
                                os.makedirs(rundir)
                            # write input file 
                                # make this computer specific 
                            if 'dogwood' in comp:
                                f1 = open('dogwood.slurm_in'    , 'r')
                                f2 = open(rundir+'dogwood.sh', 'w')
                                for line in f1:
                                    line = line.replace('in_nprocs' , str(procpjob))
                                    line = line.replace('in_queue'  , queue)
                                    line = line.replace('in_jobname', jobname)
                                    line = line.replace('in_restart', restart)
                                    f2.write(line)
                                f1.close()
                                f2.close()
                            
                            elif 'killdevil' in comp:
                                f1 = open('killdevil.lsf_in'    , 'r')
                                f2 = open(rundir+'killdevil.lsf', 'w')
                                for line in f1:
                                    line = line.replace('in_nprocs' , str(procpjob))
                                    line = line.replace('in_queue'  , queue)
                                    line = line.replace('in_jobname', jobname)
                                    line = line.replace('in_restart', restart)
                                    f2.write(line)
                                f1.close()
                                f2.close()


                            # write athinput
                            f1 = open('athinput.bgsbu_in'   , 'r')
                            f2 = open(rundir + 'athinput.bgsbu', 'w')
                            for line in f1:
                                # <job>
                                line = line.replace('in_maxout', maxout)
                                line = line.replace('in_numdomains', str(num_domains))
                                # <outputs>
                                line = line.replace('in_dthst',dthst)
                                line = line.replace('in_dtbin',dtbin)
                                line = line.replace('in_dtrst',dtrst)
                                line = line.replace('in_dtotf',dtotf)
                                line = line.replace('in_dtlv',dtlv)
                                line = line.replace('in_dtsii',dtsii)
                                # <time>
                                line = line.replace('in_courno',CourNo)
                                line = line.replace('in_tlim',  tlim)
                                
                                # <domain1>
                                line = line.replace('in_ilog',ilog)
                                line = line.replace('in_x1rat',x1rat)
                                line = line.replace('in_nx1',Nx1)
                                line = line.replace('in_x1min',x1min)
                                line = line.replace('in_x1max',x1max)
                                line = line.replace('in_nx2',Nx2)
                                line = line.replace('in_x2min',x2min)
                                line = line.replace('in_x2max',x2max)
                                line = line.replace('in_ng1',NGrid_x1)
                                line = line.replace('in_ng2',NGrid_x2)
                                
                                # <problem>
                                line = line.replace('in_mu',mu)
                                line = line.replace('in_gamma',gamma)
                                line = line.replace('in_pgas0',Pgas0)
                                line = line.replace('in_scaleh',scaleh)
                                line = line.replace('in_da',da)
                                line = line.replace('in_aval',aval)
                                line = line.replace('in_ieta1',ieta1)
                                line = line.replace('in_ieta2',ieta2) 
                                    # bar params
                                line = line.replace('in_ibar',ibar)
                                line = line.replace('in_omg',omg)
                                line = line.replace('in_Nq', Nq)
                                line = line.replace('in_qend', qend)
                                line = line.replace('in_tend', tend)
                                line = line.replace('in_tstart', tstart)
                                    # HVC params (looped over params)
                                line = line.replace('in_ihvc',ihvc)
                                line = line.replace('in_mhvc',m)
                                line = line.replace('in_thvcs', thvcs)
                                line = line.replace('in_thvce', te)
                                line = line.replace('in_rhvc', rc)
                                line = line.replace('in_rpos', r)
                                line = line.replace('in_ahvc', a)
                                line = line.replace('in_facvhvc',fac)
                                    # HVC analysis
                                line = line.replace('in_rcirc', rcirc)
                                line = line.replace('in_Nang', Nang)
                                    # Metallicity var
                                line = line.replace('in_dm', dm)
                                line = line.replace('in_lm0', lm0)
                                line = line.replace('in_imet',imet)
                                line = line.replace('in_Ncol',Ncol)
                                    # LV OTF analysis
                                line = line.replace('in_rsun',Rsun)
                                line = line.replace('in_vsun',vsun)
                                line = line.replace('in_p0',p0)
                                line = line.replace('in_minl',minl)
                                line = line.replace('in_maxl',maxl)
                                line = line.replace('in_dl',dl)
                                line = line.replace('in_dvscan',dvscan)
                                line = line.replace('in_dr',dr)
                                    # SII OTF analysis
                                line = line.replace('in_isii',isii)
                                line = line.replace('in_minx',minx)
                                line = line.replace('in_maxx',maxx)
                                line = line.replace('in_dx', dx)
                                line = line.replace('in_miny',miny)
                                line = line.replace('in_maxy',maxy)
                                line = line.replace('in_dy',dy)
                                    # Cooltable location
                                line = line.replace('in_cooltable', cooltable) 
                                    # SII Emission table
                                line = line.replace('in_siitable',siitable)
                                #   Write the changes
                                f2.write(line)
                            f1.close()
                            f2.close()

                            # Copy athena to rundir
                            shutil.copy2(rootrundir+'athena', rundir+'athena')

                            # Submit the job 
                            os.chdir(rundir)
                            if 'dogwood' in comp:
                                subprocess.call("sbatch dogwood.sh",
                                                shell=True)
                            elif 'killdevil' in comp:
                                subprocess.call("bsub < killdevil.lsf",
                                                shell=True)
                            os.chdir(rootrundir)
                            #print("[main]: submitting job %i out of %i"  % (i,jobno) )

    
    print('[main]: Total no. of jobs to submit: %i ' % jobno) 
    print('[main]: Processors per job:          %i ' % procpjob)
    print('[main]: Total processors required:   %i'  % (procpjob*jobno) )
    print("[main]: program complete.")
    quit()


main()


    

