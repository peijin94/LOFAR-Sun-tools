#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
requirements: 
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
- id: surls
  type: string[]

outputs:
- id: solutions
  type: File
  outputSource: calibration/solutions
- id: plots
  type: File[]
  outputSource: calibration/inspect_plots

steps: 
- id: fetch_data
  in:
  - id: surl_link
    source: surls
  scatter: surl_link
  out:
  - id: uncompressed
  run: ../steps/fetch_data.cwl
- id: calibration
  in: 
  - id: msin
    source: fetch_data/uncompressed
  run: calibrator_workflow.cwl
  out:
  - id: solutions
  - id: inspect_plots

