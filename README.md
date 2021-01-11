We developed an open-source QSM processing framework, QSMxT, that provides a full QSM workflow including converting DICOM data to BIDS, a variety of robust masking strategies, phase unwrapping, background field correction, dipole inversion and region-of-interest analyses based on automated anatomical segmentations. We make all required external dependencies available in a reproducible and scalable analysis environment enabling users to process QSM data for large groups of participants on any operating system in a robust way. 

# 1) install dependencies
Windows/Mac:
- https://github.com/NeuroDesk/vnm/

Linux:
- singularity: https://sylabs.io/guides/3.7/user-guide/quick_start.html
- Australian Mirror: 
```
singularity shell https://swift.rc.nectar.org.au:8888/v1/AUTH_d6165cc7b52841659ce8644df1884d5e/singularityImages/qsmxt_1.0.0_20210111.simg
```
- US Mirror: 
```
singularity shell  https://objectstorage.us-ashburn-1.oraclecloud.com/n/nrrir2sdpmdp/b/neurodesk/o/qsmxt_1.0.0_20210111.simg
```
- European Mirror: 
```
singularity shell https://objectstorage.eu-zurich-1.oraclecloud.com/n/nrrir2sdpmdp/b/neurodesk/o/qsmxt_1.0.0_20210111.simg
```

# 2) run
Convert Dicom data to BIDS:
```
cd REPLACE_WITH_YOUR_DATA_DIRECTORY
python3 /opt/QSMxT/run_0_dicomSort.py REPLACE_WITH_YOUR_DICOM_INPUT_DATA_DIRECTORY dicom
python3 /opt/QSMxT/run_1_dicomToBids.py
```
Run pipeline:
```
python3 /opt/QSMxT/run_2_nipype_qsm.py bids output
```
