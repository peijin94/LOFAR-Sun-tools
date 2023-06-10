#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
label: gaincal
hints:
- class: DockerRequirement
  dockerPull: astronrd/linc:latest
- class: ResourceRequirement
  coresMin: 16

requirements:
- class: InitialWorkDirRequirement
  listing:
  - writable: true
    entry: $(inputs.msin)

inputs:
- id: msin
  type: Directory
  inputBinding:
    prefix: msin=
    separate: false
- id: sources
  type: string
  inputBinding:
    prefix: gaincal.sources=
    separate: false
- id: sourcedb
  type: File
  inputBinding:
    prefix: gaincal.sourcedb=
    separate: false

outputs:
- id: solutions
  type: File
  outputBinding:
    glob: $(inputs.msin.basename).h5
    
baseCommand: DP3
arguments:
- gaincal.solint=4
- steps=[gaincal]
- gaincal.onebeamperpatch=true
- gaincal.caltype=diagonal
- gaincal.parmdb=$(inputs.msin.basename).h5
- gaincal.usebeammodel=true
- msout=.
