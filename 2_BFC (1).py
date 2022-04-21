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
PROCDIR = 'Proc_v1.0'
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
            #fix 1: the original did not capture 002b          
        
        else:
            CASE_LIST = [ DATADIR + "/" + PREFIX + argv[0] ] #choose only one of the files, i.e. the first one
        print(CASE_LIST)
        #print(MASK, os.path.exists(MASK))
        shrink_conditions = [2,3,4]
        noise = [0.005, 0.01, 0.02]
        FWHM = [0.1, 0.15, 0.2]
        bins = [50,100,200]
        spline_conditions = [30,50,100,150]
        #print(bins[2])
        
    
        if (os.path.exists(MASK)):
                use_mask = True #only use it if available
        
        for CASE_FOLDER in CASE_LIST :
                SMRI_FOLDER = CASE_FOLDER + "/sMRI/"
                PROC_FOLDER = SMRI_FOLDER + PROCDIR
                REG_FOLDER = PROC_FOLDER + "/Reg2Template/"
                T1 = ""
                T2 = ""
                ID = os.path.basename(CASE_FOLDER) #create my own folder, can delete
                if (os.path.exists(SMRI_FOLDER)): #if the smri folder is available
                        T1_FILELIST = glob.glob(REG_FOLDER + "/*_T1*.nrrd")
                        T2_FILELIST = glob.glob(REG_FOLDER + "/*_T2*.nrrd") #get all the files with T1 and T2 respectively
                        #print(T1_FILELIST, T2_FILELIST)
                        
                        if (len(T1_FILELIST) < 1):
                                print ("WARNING: no T1's in " + SMRI_FOLDER) #if nothing then return nothing
                        elif (len(T1_FILELIST) > 1): 
                                # check if there is a selected case
                                SELLIST = glob.glob(SMRI_FOLDER + "/*_T1*select.nrrd") #select the T1 from the file list
                                if (len(SELLIST) < 1):
                                        print ("WARNING: more than one T1 in " + SMRI_FOLDER + " , but no file selected : # " + str(len(T1_FILELIST))) #error, there are more than 1 T1 but no selected file, use the latest one
                                        command = "echo " + str(len(T1_FILELIST)) + " > " +  SMRI_FOLDER + "/NumT1.txt" #show the number of files > numT1
                                        #print(command)
                                        subprocess.run(command, shell=True)
                                else:
                                        T1 = SELLIST[0] #select the first one
                                        if (not os.path.exists(T1)):
                                                print("T1 bad link? " + T1) #error
                        else:
                                T1 = T1_FILELIST[0] #T1 is the only file in the list

                        if (len(T2_FILELIST) < 1):
                                print ("WARNING: no T2's in " + SMRI_FOLDER)
                        elif (len(T2_FILELIST) > 1):
                                # check if there is a selected case
                                SELLIST = glob.glob(SMRI_FOLDER + "/*_T2*select.nrrd")
                                if (len(SELLIST) < 1):
                                        print ("WARNING: more than one T2 in " + SMRI_FOLDER + " , but no file selected for processing")
                                        command = "echo " + str(len(T2_FILELIST)) + " > " +  SMRI_FOLDER + "/NumT2.txt"
                                        subprocess.run(command, shell=True)
                                else:
                                        T2 = SELLIST[0]
                                        if (not os.path.exists(T2)):
                                                print("T2 bad link? " + T2)
                        else:
                                T2 = T2_FILELIST[0] #same thing for T2

                        #print(T1 + " " + T2)
                    
                if (os.path.exists(T1) or os.path.exists(T2)):
                        counter =0
                        #print ("Doing " + ID)
                        if (not os.path.exists(PROC_FOLDER)):
                                os.mkdir(PROC_FOLDER) #make a folder if not yet available
                        BFC_FOLDER = PROC_FOLDER + "/" + "BFC"
                        if (not os.path.exists(BFC_FOLDER)):
                                os.mkdir(BFC_FOLDER)
                        NO_MASK_NO_WEIGHT_T1 = BFC_FOLDER + "/" + "No_Mask_No_Weight_T1"
                        NO_MASK_NO_WEIGHT_T2 = BFC_FOLDER + "/" + "No_Mask_No_Weight_T2"
                        MASK_NO_WEIGHT_T1 = BFC_FOLDER + "/" + "Mask_No_Weight_T1" 
                        MASK_NO_WEIGHT_T2 = BFC_FOLDER + "/" + "Mask_No_Weight_T2"
                        MASK_WEIGHT_T1 = BFC_FOLDER + "/" + "Mask_Weight_T1"
                        MASK_WEIGHT_T2 = BFC_FOLDER + "/" + "Mask_Weight_T2"
                        if (not os.path.exists(NO_MASK_NO_WEIGHT_T1)):
                                os.mkdir(NO_MASK_NO_WEIGHT_T1)
                        if (not os.path.exists(NO_MASK_NO_WEIGHT_T2)):
                                os.mkdir(NO_MASK_NO_WEIGHT_T2)    
                        if (not os.path.exists(MASK_NO_WEIGHT_T1)):
                                os.mkdir(MASK_NO_WEIGHT_T1)
                        if (not os.path.exists(MASK_NO_WEIGHT_T2)):
                                os.mkdir(MASK_NO_WEIGHT_T2)
                        if (not os.path.exists(MASK_WEIGHT_T1)):
                                os.mkdir(MASK_WEIGHT_T1)
                        if (not os.path.exists(MASK_WEIGHT_T2)):
                                os.mkdir(MASK_WEIGHT_T2)
                        #add code to form the different conditions: no mask no weight, no mask with weight, with mask and with weight
                        for i in range(len(spline_conditions)):
                            spline_letter = spline_conditions[i] 
                            for k in range (len(noise)):
                                noise_letter = noise[k]
                                for l in range (len(FWHM)):
                                    FWHM_i = FWHM[l]
                                    for m in range (len(bins)):
                                        bins_i = bins[m]
                                        for n in range(len(shrink_conditions)):
                                            shrink_letter = shrink_conditions[n]
                               
                                            #print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                            curFileT1_all = MASK_WEIGHT_T1 + "/" + ID + "_T1_bs_" + str(spline_letter) + "_" + str(noise_letter) + "_" + str(FWHM_i) + "_" + str(bins_i) + "_" + str(shrink_letter)+ ".nrrd"
                                            curFileT2_all = MASK_WEIGHT_T2 + "/" + ID + "_T2_bs_" +  str(spline_letter) + "_" + str(noise_letter) + "_" + str(FWHM_i) + "_" + str(bins_i) +"_"+ str(shrink_letter) + ".nrrd"
                                            curFileT1_no_weight = MASK_NO_WEIGHT_T1 + "/" + ID + "_T1_bs_" + str(spline_letter) + "_" + str(noise_letter) + "_" + str(FWHM_i) + "_" + str(bins_i) + "_" + str(shrink_letter)+ ".nrrd"
                                            curFileT2_no_weight = MASK_NO_WEIGHT_T2 + "/" + ID + "_T2_bs_" +  str(spline_letter) + "_" + str(noise_letter) + "_" + str(FWHM_i) + "_" + str(bins_i) +"_"+ str(shrink_letter) + ".nrrd"
                                            curFileT1_none = NO_MASK_NO_WEIGHT_T1 + "/" + ID + "_T1_bs_" + str(spline_letter) + "_" + str(noise_letter) + "_" + str(FWHM_i) + "_" + str(bins_i) + "_" + str(shrink_letter)+ ".nrrd"
                                            curFileT2_none = NO_MASK_NO_WEIGHT_T2 + "/" + ID + "_T2_bs_" +  str(spline_letter) + "_" + str(noise_letter) + "_" + str(FWHM_i) + "_" + str(bins_i) +"_"+ str(shrink_letter) + ".nrrd"
                                            
                                            if (not os.path.exists(curFileT1_all)) and os.path.exists(T1):
                                             #   print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                                print("running bias correction T1 " + curFileT1_all)
                                                T = [FWHM_i, noise_letter, bins_i]
                                                dim = 3
                                                M = MASK
                                                W = WEIGHTEDMASK
                       
                                                subprocess.run(["%s -d %s -x %s -w %s -t %s -b %s -i  %s -o %s -s %s " %(N4Cmd, dim, M, W,T, spline_letter, T1, curFileT1_all, shrink_letter)], 
                                               shell=True)
                                            if (not os.path.exists(curFileT2_all)) and os.path.exists(T2):
                                              #  print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                                print("running bias correction T2" + curFileT2_all)
                                                T = [FWHM_i, noise_letter, bins_i]
                                                dim = 3
                                                M = MASK
                                                W = WEIGHTEDMASK
                             
                                                subprocess.run(["%s -d %s -x %s -w %s -t %s -b %s -i %s -o %s -s %s " %(N4Cmd, dim, M, W,T, spline_letter, T2, curFileT2_all, shrink_letter)], shell = True)
                                            if (not os.path.exists(curFileT1_none)) and os.path.exists(T1):
                                             #   print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                                print("running bias correction T1 " + curFileT1_none)
                                                T = [FWHM_i, noise_letter, bins_i]
                                                dim = 3
                                                subprocess.run(["%s -d %s -t %s -b %s -i  %s -o %s -s %s " %(N4Cmd, dim,T, spline_letter, T1, curFileT1_none, shrink_letter)], 
                                               shell=True)
                                            if (not os.path.exists(curFileT2_none)) and os.path.exists(T2):
                                              #  print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                                print("running bias correction T2" + curFileT2_none)
                                                T = [FWHM_i, noise_letter, bins_i]
                                                dim = 3
                                             
                                                subprocess.run(["%s -d %s -t %s -b %s -i %s -o %s -s %s " %(N4Cmd, dim,T, spline_letter, T2, curFileT2_none, shrink_letter)], shell = True)
                                            if (not os.path.exists(curFileT1_no_weight)) and os.path.exists(T1):
                                             #   print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                                print("running bias correction T1 " + curFileT1_no_weight)
                                                T = [FWHM_i, noise_letter, bins_i]
                                                dim = 3
                                                M = MASK
                                                subprocess.run(["%s -d %s -x %s -t %s -b %s -i  %s -o %s -s %s " %(N4Cmd, dim, M,T, spline_letter, T1, curFileT1_no_weight, shrink_letter)], 
                                               shell=True)
                                            if (not os.path.exists(curFileT2_no_weight)) and os.path.exists(T2):
                                              #  print(spline_letter, shrink_letter, noise_letter, FWHM_i, bins_i)
                                                print("running bias correction T2" + curFileT2_no_weight)
                                                T = [FWHM_i, noise_letter, bins_i]
                                                dim = 3
                                                M = MASK
                                                subprocess.run(["%s -d %s -x %s -t %s -b %s -i %s -o %s -s %s " %(N4Cmd, dim, M,T, spline_letter, T2, curFileT2_no_weight, shrink_letter)], shell = True)
                                
                                         
                 
                                 
	
if (__name__ == "__main__"):
        parser = OptionParser(usage="%prog [options] ID \n if ID = 'all' then do all cases, otherwise provide ID of case (without prefix " + PREFIX + ")")
        parser.add_option("-o","--changeOrient",action="store_true", dest="orientation", default="False", help="if input data orientation is LPI, change the orientation RAI ")
        (opts, argv) = parser.parse_args(["002b"]) #can change to the indices needed
        if (len(argv)<1):
                parser.print_help()
                sys.exit(0)
        
        main(opts, argv)
        


