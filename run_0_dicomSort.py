#!/usr/bin/env python3

# Adapted from Alex Weston
# Digital Innovation Lab, Mayo Clinic
# https://gist.github.com/alex-weston-13/4dae048b423f1b4cb9828734a4ec8b83
import argparse
import os
import pydicom  # pydicom is using the gdcm package for decompression
import shutil
import numpy

def empty_dirs(root_dir='.', recursive=True):
    empty_dirs = []
    for root, dirs, files in os.walk(root_dir, topdown=False):
        #print root, dirs, files
        if recursive:
            all_subs_empty = True  # until proven otherwise
            for sub in dirs:
                full_sub = os.path.join(root, sub)
                if full_sub not in empty_dirs:
                    #print full_sub, "not empty"
                    all_subs_empty = False
                    break
        else:
            all_subs_empty = (len(dirs) == 0)
        if all_subs_empty and len(files) == 0:
            empty_dirs.append(root)
            yield root

def find_empty_dirs(root_dir='.', recursive=True):
    return list(empty_dirs(root_dir, recursive))

def clean_text(string):
    # clean and standardize text descriptions, which makes searching files easier
    for symbol in ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " "]:
        string = string.replace(str(symbol), "_") # replace everything with an underscore
    return string.lower()  

def dicomsort(input_dir, output_dir, use_patient_names, use_session_dates, delete_originals):
    os.makedirs(output_dir, exist_ok=True)
    extension = '.IMA'
    print('reading file list...')
    unsortedList = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file[-4:] in ['.ima', '.IMA']: # exclude non-dicoms, good for messy folders
                unsortedList.append(os.path.join(root, file))
            elif file[-4:] in ['.dcm', '.DCM']:
                extension = '.dcm'
                unsortedList.append(os.path.join(root, file))
            elif file[:3] == 'MR.':
                extension = '.dcm'
                unsortedList.append(os.path.join(root, file))
            elif file[:2] == 'IM':
                extension = '.dcm'
                unsortedList.append(os.path.join(root, file))

    print(f'{len(unsortedList)} files found.')
    
    fail = False

    subjName_dates = []
    subjName_sessionNums = {}

    for dicom_loc in unsortedList:
        # read the file
        ds = pydicom.read_file(dicom_loc, force=True)
    
        # get patient, study, and series information
        patientName = clean_text(str(ds.get("PatientName", "NA")))
        patientID = clean_text(ds.get("PatientID", "NA"))
        studyDate = clean_text(ds.get("StudyDate", "NA"))
        studyDescription = clean_text(ds.get("StudyDescription", "NA"))
        seriesDescription = clean_text(ds.get("SeriesDescription", "NA"))
        seriesNumber = clean_text(str(ds.get("SeriesNumber", "NA")))
    
        # generate new, standardized file name
        modality = ds.get("Modality","NA")
        studyInstanceUID = ds.get("StudyInstanceUID","NA")
        seriesInstanceUID = ds.get("SeriesInstanceUID","NA")
        instanceNumber = str(ds.get("InstanceNumber","0"))
        fileName = modality + "." + seriesInstanceUID + "." + instanceNumber + extension

        subj_name = patientName if use_patient_names else patientID
        
        # uncompress files (using the gdcm package)
        try:
            ds.decompress()
        except Exception as e:
            print(f'An exception occurred while decompressing {dicom_loc}')
            print(f'Exception details: {e}')
            exit()
        
        # save files to a 3-tier nested folder structure
        subjFolderName = f"sub-{subj_name}"
        seriesFolderName = f"{seriesDescription}"
    
        subjName_date = f"{subj_name}_{studyDate}"

        if not any(subj_name in x for x in subjName_dates):
            print(f'Identified subject: {subj_name}')
        
        if subjName_date not in subjName_dates:
            subjName_dates.append(subjName_date)
            if subj_name in subjName_sessionNums.keys():
                subjName_sessionNums[subj_name] += 1
            else:
                subjName_sessionNums[subj_name] = 1
            print(f'Identified session: {subj_name} #{subjName_sessionNums[subj_name]} {studyDate}')

        sesFolderName = f"ses-{subjName_sessionNums[subj_name]}" if not use_session_dates else f"ses-{studyDate}"
        
        if not os.path.exists(os.path.join(output_dir, subjFolderName, sesFolderName, seriesFolderName)):
            print(f'Identified series: {subjFolderName}/{sesFolderName}/{seriesFolderName}')
            os.makedirs(os.path.join(output_dir, subjFolderName, sesFolderName, seriesFolderName), exist_ok=True)
        
        ds.save_as(os.path.join(output_dir, subjFolderName, sesFolderName, seriesFolderName, fileName))

        if not os.path.exists(os.path.join(output_dir, subjFolderName, sesFolderName, seriesFolderName, fileName)):
            fail = True

    if not fail and delete_originals:
        for dicom_loc in unsortedList:
            os.remove(dicom_loc)

        for folder in find_empty_dirs(input_dir):
            print(folder)
            #shutil.rmtree(folder)

    print('done.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="QSMxT dicomSort: Sorts DICOM files into a folder structure of the form <out_dir>/<PatientID>_<StudyDate>/<SeriesDescription>/",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'input_dir',
        help='input DICOM directory; will be recursively searched for DICOM files'
    )

    parser.add_argument(
        'output_dir',
        default=None,
        help='output directory for sorted DICOMs; by default this is the same as input_dir'
    )

    parser.add_argument(
        '--use_patient_names',
        action='store_true',
        help='use the PatientName rather than PatientID for subject folders'
    )

    parser.add_argument(
        '--use_session_dates',
        action='store_true',
        help='Use the StudyDate field rather than an incrementer for session IDs'
    )

    parser.add_argument(
        '--delete_originals',
        action='store_true',
        help='delete the original DICOM files and folders after successfully sorting; by ' +
             'default this is on when input_dir == output_dir'
    )

    args = parser.parse_args()

    dicomsort(
        input_dir=args.input_dir,
        output_dir=args.output_dir if args.output_dir is not None else args.input_dir,
        use_patient_names=args.use_patient_names,
        use_session_dates=args.use_session_dates,
        delete_originals=args.input_dir == args.output_dir or args.delete_originals
    )
    
    