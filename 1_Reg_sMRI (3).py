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
PROCDIR = "Proc_v1.0"

#tools
BRAINSFITCmd = '/proj/NIRAL/tools/BRAINSFit'
ResampleCmd = '/proj/NIRAL/tools/ResampleScalarVectorDWIVolume'
N4Cmd = '/proj/NIRAL/tools/N4BiasFieldCorrection'
ImageMathCmd = '/proj/NIRAL/tools/ImageMath'

def main(opts, argv):
        CASE_LIST = []	
        if (argv[0] == "all"):
            
            CASE_LIST = sorted(glob.glob(DATADIR  + "/" + PREFIX + "*[0123456789][0123456789][0123456789]*")) #any number that follows the data directory and prefix (with all), glob is the retriever
            #calls /017/sMRI/T1_T2_longleaf/001 to 019 for the current example 
        
        else:
            CASE_LIST = [ DATADIR + "/" + PREFIX + argv[0] ] #no numbers
        print(CASE_LIST)
        #print(MASK, os.path.exists(MASK))
       
    
        if (os.path.exists(MASK)):
                use_mask = True #only use it if available

        for CASE_FOLDER in CASE_LIST :
                SMRI_FOLDER = CASE_FOLDER + "/sMRI/"
                print(SMRI_FOLDER)
                T1 = ""
                T2 = ""
                ID = os.path.basename(CASE_FOLDER) #create my own folder, can delete
                if (os.path.exists(SMRI_FOLDER)): #if the smri folder is available
                        T1_FILELIST = glob.glob(SMRI_FOLDER + "/*T1*.nrrd")
                        T2_FILELIST = glob.glob(SMRI_FOLDER + "/*T2*.nrrd") #get all the files with T1 and T2 respectively
                        print(T1_FILELIST, T2_FILELIST)
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

                        print ("Doing " + ID)
                        PROC_FOLDER = SMRI_FOLDER + PROCDIR
                        if (not os.path.exists(PROC_FOLDER)):
                                os.mkdir(PROC_FOLDER) #make a folder if not yet available
                        REG_FOLDER = PROC_FOLDER + "/" + "Reg2Template"
                        if (not os.path.exists(REG_FOLDER)):
                                os.mkdir(REG_FOLDER)
                        #BIAS_T1 = PROC_FOLDER + "/" + ID + "_T1_bs.nrrd"
                        #BIAS_T2 = PROC_FOLDER + "/" + ID + "_T2_bs.nrrd"

                        #print(BIAS_T1)

                        #if (not os.path.exists(BIAS_T1) and os.path.exists(T1)):
                         #       print("running bias correction T1 " + BIAS_T1)
                          #      subprocess.run(["%s -d 3 -i %s -o %s -s 2 " %(N4Cmd, T1, BIAS_T1) ], #look at this later
                           #                    shell=True)
                        #if (not os.path.exists(BIAS_T2) and os.path.exists(T2)):
                         #       print ("running bias correction T2 " + BIAS_T2)
                          #      subprocess.run(["%s -d 3 -i %s -o %s -s 2 " %(N4Cmd, T2, BIAS_T2) ], 
                           #                    shell=True)
	
                       # STX_T1 = PROC_FOLDER + '/stx_' + ID + "_T1_bs.nrrd" 
                       # STX_T2 = PROC_FOLDER + '/stx_' + ID + "_T2_bs.nrrd"
                        STX_T1 = REG_FOLDER + '/stx_' + ID + "_T1.nrrd"
                        STX_T2 = REG_FOLDER + '/stx_' + ID + "_T2.nrrd"               
                        STX_T1_transform = REG_FOLDER + '/stx_rigid_transformT1.txt'
                        STX_T2_transform = REG_FOLDER + '/stx_rigid_transformT2.txt'
                        STX_T1_transform_init = REG_FOLDER + '/stx_rigid_transformT1_init.txt'
                        STX_T2_transform_init = REG_FOLDER + '/stx_rigid_transformT2_init.txt'

                        if (not os.path.exists(STX_T1) and os.path.exists(T1)):
                                print ("running atlas registration T1 " + STX_T1) 
                                
                                if (use_mask):
                                        print ("using mask " )
                                        #print (["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ])
                                        # start with affine to get brain mask to individual space
                                        if (os.path.exists(STX_T1_transform_init)):
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useAffine --numberOfSamples 600000 --initialTransform %s --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform_init, STX_T1_transform) ], 
                                                               shell=True) 
                                        else:
                                                #print(["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ])
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ], 
                                                               shell=True) #initialize transform mode
                                                
                                        MASK_INDIV = REG_FOLDER + '/brainmaskAtlasToIndiv_Tmp.nrrd'
                                        # applies the inverse to get brainmask into indiv space
                                        subprocess.run(["%s %s %s -f %s -R %s -i nn -b" %(ResampleCmd, MASK, MASK_INDIV, STX_T1_transform, T1)], 
                                                       shell=True)
                                        
                                        print ("updating atlas registration T1 (with mask) " + STX_T1) 
                                                
                                        if (os.path.exists(STX_T1_transform_init)):
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid  --numberOfSamples 600000 --fixedBinaryVolume %s --movingBinaryVolume %s --initialTransform %s --linearTransform %s --maskProcessingMode ROI" %(BRAINSFITCmd, ATLAS, T1, MASK, MASK_INDIV, STX_T1_transform_init, STX_T1_transform) ], 
                                                               shell=True)
                                        else:
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --fixedBinaryVolume %s --movingBinaryVolume %s --linearTransform %s --maskProcessingMode ROI" %(BRAINSFITCmd, ATLAS, T1, MASK, MASK_INDIV, STX_T1_transform) ], 
                                                               shell=True) #initialize transform mode

                                        # remove mask, as it was only temporarily used
                                        os.remove(MASK_INDIV)

                                else:
                                        subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ], 
                                                       shell=True) #do not touch the binary volume
                                        

                                #resample output image
                                subprocess.run(["%s %s %s -f %s -R %s -i bs -t rt" %(ResampleCmd, T1, STX_T1, STX_T1_transform, ATLAS)], 
                                               shell=True)
                                subprocess.run(["%s %s -outfile %s -threshMask 0,100000" %(ImageMathCmd,STX_T1,STX_T1)], shell=True)
                                
                        if (not os.path.exists(STX_T2) and os.path.exists(STX_T1) and os.path.exists(T2)):
                                print ("running atlas T1 registration T2 " + STX_T2)
                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid  --numberOfSamples 600000 --initialTransform %s --linearTransform %s" %(BRAINSFITCmd, STX_T1, T2, STX_T1_transform, STX_T2_transform)], 
                                               shell=True) 
                                subprocess.run(["%s %s %s -f %s -R %s -i bs -t rt" %(ResampleCmd, T2, STX_T2, STX_T2_transform, ATLAS)], 
                                               shell=True)
                                subprocess.run(["%s %s -outfile %s -threshMask 0,100000" %(ImageMathCmd, STX_T2, STX_T2)], shell=True)


                        #special case: no T1, but T2, now register T2 directly to atlas (rather than T1 in atlas space)
                        if (not os.path.exists(STX_T2) and not os.path.exists(T1) and os.path.exists(T2)):

                                print ("running atlas registration T2 " + STX_T2) 
                                
                                if (use_mask):
                                        print ("using mask " )
                                        print (["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T2, STX_T2_transform) ])
                                        # start with affine to get brain mask to individual space
                                        if (os.path.exists(STX_T2_transform_init)):
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useAffine --numberOfSamples 600000 --initialTransform %s --linearTransform %s" %(BRAINSFITCmd, ATLAS, T2, STX_T2_transform_init, STX_T2_transform) ], 
                                                               shell=True) 
                                        else:
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useAffine --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T2, STX_T2_transform) ], 
                                                               shell=True) #no initial transform

                                        MASK_INDIV = REG_FOLDER + '/brainmaskAtlasToIndiv_Tmp.nrrd'
                                        # applies the inverse to get brainmask into indiv space
                                        subprocess.run(["%s %s %s -f %s -R %s -i nn -b" %(ResampleCmd, MASK, MASK_INDIV, STX_T2_transform, T2)], 
                                                       shell=True)
                                        
                                        print ("updating atlas registration T2 (with mask) " + STX_T2) 
                                                
                                        if (os.path.exists(STX_T2_transform_init)):
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid  --numberOfSamples 600000 --fixedBinaryVolume %s --movingBinaryVolume %s --initialTransform %s --linearTransform %s --maskProcessingMode ROI" %(BRAINSFITCmd, ATLAS, T2, MASK, MASK_INDIV, STX_T2_transform_init, STX_T2_transform) ], 
                                                               shell=True)
                                        else:
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --fixedBinaryVolume %s --movingBinaryVolume %s --linearTransform %s --maskProcessingMode ROI" %(BRAINSFITCmd, ATLAS, T2, MASK, MASK_INDIV, STX_T2_transform) ], 
                                                               shell=True) #no initial transform

                                        # remove mask, as it was only temporarily used
                                        os.remove(MASK_INDIV)

                                else:
                                        subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T2, STX_T2_transform) ], 
                                                       shell=True) 

                                #resample output image
                                subprocess.run(["%s %s %s -f %s -R %s -i bs -t rt" %(ResampleCmd, T2, STX_T2, STX_T2_transform, ATLAS)], 
                                               shell=True)
                                subprocess.run(["%s %s -outfile %s -threshMask 0,100000" %(ImageMathCmd,STX_T2,STX_T2)], shell=True)
                #end of if

#end of main 

	
if (__name__ == "__main__"):
        parser = OptionParser(usage="%prog [options] ID \n if ID = 'all' then do all cases, otherwise provide ID of case (without prefix " + PREFIX + ")")
        parser.add_option("-o","--changeOrient",action="store_true", dest="orientation", default="False", help="if input data orientation is LPI, change the orientation RAI ")
        (opts, argv) = parser.parse_args(["007_EID"])
        if (len(argv)<1):
                parser.print_help()
                sys.exit(0)
        
        main(opts, argv)
        


