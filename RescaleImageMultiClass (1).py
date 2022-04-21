#!/usr/bin/python3
import SimpleITK as sitk
import sys
import os
import argparse
import numpy as np
import scipy
from scipy import stats

def main(args):
 
    #print(args.labelList)
    #print(args.intensityList)

    inputITK = sitk.ReadImage(args.inputImage, sitk.sitkFloat32)
    imageArray = sitk.GetArrayFromImage(inputITK).flatten()
    # imageArray is numpy array of image data

    labelITK = sitk.ReadImage(args.labelImage, sitk.sitkInt16)
    labelArray = sitk.GetArrayFromImage(labelITK).flatten()
    
    imagestats = sitk.LabelStatisticsImageFilter()
    imagestats.UseHistogramsOn()
    imagestats.Execute(inputITK,labelITK)

    if (args.median):
        firstClassVal = imagestats.GetMedian(args.labelList[0])
        secondClassVal = imagestats.GetMedian(args.labelList[1])
        print('using median')
    elif (args.mode):
        scaleFactor = 100
        condArray = labelArray == args.labelList[0]
        scaledArray = imageArray[condArray]*scaleFactor
        # need to remove 0
        cond2Array =  scaledArray != 0
        scaledArray = scaledArray[cond2Array]

        labelmode = scipy.stats.mode(scaledArray.astype(int), axis=None).mode
        firstClassVal = labelmode[0]/scaleFactor

        condArray = labelArray == args.labelList[1]
        scaledArray = imageArray[condArray]*scaleFactor
        # need to remove 0
        cond2Array =  scaledArray != 0
        scaledArray = scaledArray[cond2Array]

        labelmode = scipy.stats.mode(scaledArray.astype(int), axis=None).mode
        secondClassVal = labelmode[0]/scaleFactor
        print('using mode')

    else:
        firstClassVal = imagestats.GetMean(args.labelList[0])
        secondClassVal = imagestats.GetMean(args.labelList[1])

    print(firstClassVal)
    print(secondClassVal)

    firstTargetVal = args.intensityList[0] 
    secondTargetVal = args.intensityList[1]

    scale = (secondTargetVal - firstTargetVal) / (secondClassVal -  firstClassVal)
    shift = (secondClassVal * firstTargetVal - firstClassVal * secondTargetVal) / (secondClassVal - firstClassVal) / scale

    print(shift)
    print(scale)

    rescaleFilter = sitk.ShiftScaleImageFilter()
    rescaleFilter.SetShift(shift)
    rescaleFilter.SetScale(scale)
    outputITK = rescaleFilter.Execute(inputITK)
    
    sitk.WriteImage(outputITK, args.outputImage, True)
##############################################################################################################


if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(usage="%(prog)s inputImage labelImage outputImage -l l1 l2 -i I1 I2 [--median | --mode]")

    parser.add_argument('inputImage', help='image to be rescaled (intensitywise)')
    parser.add_argument('labelImage', help='image with labels, in voxelwise correspondence with inputImage')
    parser.add_argument('outputImage', help='Rescaled image')
    #parser.add_argument('-n', '--numberClasses',  help='the number of classes used for the intensity rescaling', type=int, default=2 )
    parser.add_argument('-l', '--labelList', help='list with label IDs to be used as target for rescaling, these have to be in the same order as the intensityList', type=int, nargs='+', required=True)
    parser.add_argument("-i", "--intensityList", help="list with intensity values to be used as target for rescaling, these have to be in the same order as the labelList", type=float, nargs='+', required=True)
    parser.add_argument("--median", help="use median instead of mean", nargs='?', const=True, default=False)
    parser.add_argument("--mode", help="use mode instead of mean", nargs='?', const=True, default=False)
    args = parser.parse_args()

    if ( (len(args.labelList) != 2) or (len(args.intensityList) != 2)):
        print("label or intensity list is not of length 2, exiting")
        sys.exit(1)

    main(args)
