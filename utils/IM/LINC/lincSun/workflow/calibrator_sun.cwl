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
- id: refant
  type: string?
  default: 'CS001HBA0'

outputs:
- id: solutions
  type: File
  outputSource: combine_solutions/output_solution
- id: save_inspection
  type: File[]
  outputSource: save_inspection/dir

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
- id: create_inspect_solutions
  run: ../steps/inspect_solutions.cwl
  in:
  - id: solution_file
    source: combine_solutions/output_solution
  - id: refant
    source: refant
  out:
  - id: inspection
- id: save_inspection
  in:
    - id: files
      linkMerge: merge_flattened
      source:
        - create_inspect_solutions/inspection
    - id: sub_directory_name
      default: inspection
  out:
    - id: dir
  run: ../steps/collectfiles.cwl
  label: save_inspection

