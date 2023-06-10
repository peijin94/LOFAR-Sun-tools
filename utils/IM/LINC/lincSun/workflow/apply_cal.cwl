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
