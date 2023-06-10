#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow

requirements:
- class: ScatterFeatureRequirement
- class: SubworkflowFeatureRequirement

inputs:
- id: msin
  type: Directory[]
- id: solutions
  type: File

outputs:
- id: msout
  type: Directory[]
  outputSource: applycal/msout
- id: images
  type:
    type: array 
    items: 
      type: array
      items: File
  outputSource: create_images/images

- id: psf
  type:
    type: array 
    items: 
      type: array
      items: File
  outputSource: create_images/psf

- id: reprojected
  type:
    type: array 
    items: 
      type: array
      items: File
  outputSource: create_images/reprojected

- id: preview_video
  type:
    type: array 
    items: File
  outputSource: create_images/preview_video

steps:
- id: applycal
  in:
  - id: msin
    source: msin
  - id: solutions
    source: solutions
  run: ../steps/applycal.cwl
  out:
  - msout
  scatter: msin

- id: create_images
  in:
  - id: msin
    source: applycal/msout
  run: ./image_series.cwl
  scatter: msin
  out:
    - images
    - reprojected
    - preview_video
    - psf