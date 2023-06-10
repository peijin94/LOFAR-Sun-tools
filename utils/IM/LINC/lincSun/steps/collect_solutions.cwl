#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

inputs:
- id: solution_files
  type: File[]
  inputBinding:
    position: 1

outputs:
- id: output_solution
  type: File
  outputBinding:
    glob: solutions.h5

baseCommand: H5parm_collector.py
arguments:
- prefix: --outh5parm
  valueFrom: solutions.h5

hints:
- class: DockerRequirement
  dockerPull: astronrd/linc:latest
