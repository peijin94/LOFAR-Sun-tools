#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

hints:
- class: DockerRequirement
  dockerPull: astronrd/linc:latest

arguments:
- format=<
- outtype=blob
- out=calibrator.sourcedb
inputs:
- id: skymodel
  type: File
  inputBinding: 
    prefix: in=
    separate: false

outputs: 
- id: sourcedb
  type: File
  outputBinding:
    glob: calibrator.sourcedb

baseCommand: makesourcedb
