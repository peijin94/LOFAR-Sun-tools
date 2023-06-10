#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
inputs:
- id: solution_file
  type: File
  inputBinding:
    position: 1
- id: soltab
  type: string
  default: sol000
  inputBinding:
    prefix: --solset
outputs:
- id: plots
  type: File[]
  outputBinding:
    glob: "out/*.png"
baseCommand: /usr/local/bin/inspect_solutions.py
arguments:
- valueFrom: out
  position: 2

hints:
  DockerRequirement:
    dockerPull: git.astron.nl:5000/ssw-ksp/solar-im-compressing:latest

requirements:
  - class: InlineJavascriptRequirement

