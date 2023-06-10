#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow

inputs:
- id: msin
  type: Directory
  
outputs:
- id: images
  type: File[]
  outputSource: create_images/outputImages
- id: psf
  type: File[]
  outputSource: create_images/outputPSF
- id: dirty
  type: File[]
  outputSource: create_images/outputDirty
- id: model
  type: File[]
  outputSource: create_images/outputModel
- id: reprojected
  type: File[]
  outputSource: reproject/reprojected_images
- id: preview_video
  type: File
  outputSource: reproject/preview_video
  

steps:
- id: derive_time_samples
  in:
  - id: msin
    source: msin
  run: ../steps/derive_time_samples.cwl
  out:
  - n_visibilities
  - samples
- id: create_images
  in:
  - id: msin
    source: msin
  - id: n_intervals
    source: derive_time_samples/samples
  run: ../steps/wsclean.cwl
  out:
  - id: outputImages
  - id: outputDirty
  - id: outputPSF
  - id: outputModel
  
- id: reproject
  in: 
  - id: fits_files
    source: create_images/outputImages
  out:
  - id: preview_video
  - id: reprojected_images
  run: ../steps/reproject.cwl