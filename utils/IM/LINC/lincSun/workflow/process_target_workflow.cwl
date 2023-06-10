#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
requirements:
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
- id: surls
  type: string[]
- id: solutions
  type: string


outputs:
- id: images
  type:
    type: array
    items:
      type: array
      items: File
  outputSource: imaging/images

- id: psf
  type:
    type: array
    items:
      type: array
      items: File
  outputSource: imaging/psf

- id: reprojected
  type:
    type: array
    items:
      type: array
      items: File
  outputSource: imaging/reprojected

- id: preview_video
  type:
    type: array
    items: File
  outputSource: imaging/preview_video


steps:
- id: fetch_solutions
  in: 
  - id: surl_link
    source: solutions
  out: 
  - id: solution
  run: ../steps/fetch_solutions.cwl
- id: fetch_data
  in:
  - id: surl_link
    source: surls
  scatter: surl_link
  out:
  - uncompressed
  run: ../steps/fetch_data.cwl
- id: imaging
  in:
  - id: msin
    source: fetch_data/uncompressed
  - id: solutions
    source: fetch_solutions/solution
  run: image_workflow.cwl
  out:
  - id: images
  - id: psf
  - id: reprojected
  - id: preview_video
