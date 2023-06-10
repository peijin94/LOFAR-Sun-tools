#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
requirements: 
  - class: ScatterFeatureRequirement
  - class: StepInputExpressionRequirement
inputs:
- id: msin
  type: Directory[]
- id: ATeam_skymodel
  type: File
- id: avg_timeresolution
  type: int?
  default: 4
- id: avg_freqresolution
  type: string?
  default: 48.82kHz

outputs:
- id: solutions
  type: File
  outputSource: combine_solutions/output_solution
- id: inspect_plots
  type: File[]
  outputSource: create_inspect_plots/plots

steps:
- id: find_skymodel
  in:
  - id: msin
    source: msin
  - id: ATeam_skymodel
    source: ATeam_skymodel
  out:
  - skymodel_file
  - target_source
  run: ../steps/find_skymodel.cwl
- id: makesourcedb
  in:
  - id: skymodel
    source: find_skymodel/skymodel_file
  run: ../steps/makesourcedb.cwl
  out:
  - sourcedb
- id: find_solution
  in:
  - id: msin
    source: msin
  - id: sources
    source: find_skymodel/target_source
  - id: sourcedb
    source: makesourcedb/sourcedb
  scatter: msin
  run: ../steps/gaincal.cwl
  out:
  - solutions
- id: combine_solutions
  in:
  - id: solution_files
    source: find_solution/solutions
  run: ../steps/collect_solutions.cwl
  out:
  - id: output_solution
- id: create_inspect_plots
  run: ../steps/inspect_solutions.cwl
  in:
  - id: solution_file
    source: combine_solutions/output_solution
  out:
  - plots
