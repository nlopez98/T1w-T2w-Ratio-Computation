#!/tools/Python/Python-3.8.0/bin/python3
## adapted by M Styner, original script by SunHyung 
## changed to python3
## added support for brainmask => significantly improved results
## added support for optional initial T1 transform file 
##           => allows update with initial transform in case of failures
## replaced linear interpolation by b-spline interpolation
## added removal of negative scalars from final image
######################################################################################################### 

import os
import sys
import glob
import subprocess
import shlex, subprocess
from os.path import exists
from optparse import OptionParser

Current_Dir = os.getcwd()

DATADIR = Current_Dir + '/T1T2_longleaf' #hardcoded
#PREFIX = "UPSIDE"
#PREFIX = "CT"
PREFIX = ""

# infant nih pd atlas as template
ATLAS = '/proj/NIRAL/users/rozav/12months_Extended/T1_12months_withSkull.nrrd'
MASK = '/proj/NIRAL/users/rozav/12months_Extended/BrainMask.nrrd'
PROCDIR = '/Proc_v1.0'
WEIGHTEDMASK = '/proj/NIRAL/users/rozav/T1T2Ratio/002b_mask_bin.nrrd'
#tools
BRAINSFITCmd = '/proj/NIRAL/tools/BRAINSFit'
ResampleCmd = '/proj/NIRAL/tools/ResampleScalarVectorDWIVolume'
N4Cmd = '/proj/NIRAL/tools/N4BiasFieldCorrection'
ImageMathCmd = '/proj/NIRAL/tools/ImageMath'

def main(opts, argv):
        CASE_LIST = []	
        if (argv[0] == "all"):
            
            CASE_LIST = sorted(glob.glob(DATADIR  + "/" + PREFIX + "*[0123456789][0123456789][0123456789B]*")) #any number that follows the data directory and prefix (with all), glob is the retriever        
        
        else:
            CASE_LIST = [ DATADIR + "/" + PREFIX + argv[0] ] #choose only one of the files, i.e. the first one
        for CASE_FOLDER in CASE_LIST :
                SMRI_FOLDER = CASE_FOLDER + "/sMRI"
                PROC_FOLDER = SMRI_FOLDER + PROCDIR
                #if (os.path.exists(T1) or os.path.exists(T2)):     #maybe can remove                  
                BFC_FOLDER = PROC_FOLDER + "/" + "BFC"
                RATIO_FOLDER = BFC_FOLDER + "/" + "T1T2RATIO"
                NO_BOTH = RATIO_FOLDER + "/" + "NO_MASK_NO_WEIGHT"
                NO_WEIGHT = RATIO_FOLDER + "/" + "MASK_NO_WEIGHT"
                BOTH = RATIO_FOLDER + "/" + "MASK_WEIGHT"
                settingArray = [NO_BOTH, NO_WEIGHT, BOTH]
                if (not os.path.exists(RATIO_FOLDER)):
                    os.mkdir(RATIO_FOLDER)
                for i in settingArray:
                    if (not os.path.exists(i)):
                        os.mkdir(i)
                MASK_NO_WEIGHT_T1 = BFC_FOLDER + "/" + "Mask_No_Weight_T1" #change this to generalize in 2_BFC.py
                MASK_NO_WEIGHT_T2 = BFC_FOLDER + "/" + "Mask_No_Weight_T2"
                MASK_WEIGHT_T1 = BFC_FOLDER + "/" + "Mask_Weight_T1"
                MASK_WEIGHT_T2 = BFC_FOLDER + "/" + "Mask_Weight_T2"
                NO_MASK_NO_WEIGHT_T1 = BFC_FOLDER + "/" + "No_Mask_No_Weight_T1"
                NO_MASK_NO_WEIGHT_T2 = BFC_FOLDER + "/" + "No_Mask_No_Weight_T2"
                folderArray = [(NO_MASK_NO_WEIGHT_T1, NO_MASK_NO_WEIGHT_T2),(MASK_NO_WEIGHT_T1, MASK_NO_WEIGHT_T2), (MASK_WEIGHT_T1, MASK_WEIGHT_T2) ] 
                for i in range(len(folderArray)):
                    T1_FILES = tuple(sorted(glob.glob(folderArray[i][0] + "/*.nrrd"))) #sorted by spline, noise, FWHM, bins, shrink
                    T2_FILES = tuple(sorted(glob.glob(folderArray[i][1] + "/*.nrrd")))
                            #print(T2_FILES[1])
                    for f1, f2 in zip(T1_FILES, T2_FILES):
                        tmp1 = RATIO_FOLDER + "/" + "tmp1.nrrd"
                        tmp2 = RATIO_FOLDER + "/" + "tmp2.nrrd"
                        #tmp3 = RATIO_FOLDER + "/" + "tmp3.nrrd"
                        for j in range(len(f1)):
                                    #print(f1[j])
                            if f1[j] == "s":
                                tgt = settingArray[i] + "/" + "targetT1T2ratioRaw" + f1[j+1:]
                        if (os.path.exists(f1) and os.path.exists(f2) and not os.path.exists(tmp1) and not os.path.exists(tmp2) and not os.path.exists(tgt)):
                            #print(tmp1,tmp2,tmp3,f1,f2)
                            print("Running ImageMath I " + tgt)
                            subprocess.run(["%s %s -outfile %s -constOper 0,1 -type float " %(ImageMathCmd,f1,tmp1)], shell=True) 
                            print("Running ImageMath II " + tgt)
                            subprocess.run(["%s %s -outfile %s -constOper 0,1 -type float" %(ImageMathCmd,f2,tmp2)], shell=True) 
                            print("Running division " + tgt)
                            subprocess.run(["%s %s -div %s -outfile %s -type float" %(ImageMathCmd,tmp1,tmp2,tgt)], shell=True) #tgt is tmp3 now 
                            #print("Running masking " + tgt)
                            #subprocess.run(["%s %s -outfile %s -threshMask 0,5 -type float" %(ImageMathCmd,tmp3,tgt)], shell=True)
                            os.remove(tmp1)
                            os.remove(tmp2)
                            #os.remove(tmp3)
                                
                            
                            
if (__name__ == "__main__"):
        parser = OptionParser(usage="%prog [options] ID \n if ID = 'all' then do all cases, otherwise provide ID of case (without prefix " + PREFIX + ")")
        parser.add_option("-o","--changeOrient",action="store_true", dest="orientation", default="False", help="if input data orientation is LPI, change the orientation RAI ")
        (opts, argv) = parser.parse_args(["002b"]) #can change to the indices needed
        if (len(argv)<1):
                parser.print_help()
                sys.exit(0)
        
        main(opts, argv)
        

