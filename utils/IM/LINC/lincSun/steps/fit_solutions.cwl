#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
inputs: 
- id: solution_file
  type: File
outputs: 
- id: solution_file
  type: File
  outputBinding: 
    glob: "*.h5"
baseCommand: /usr/local/bin/interpolate_solutions.py
arguments:
- $(inputs.solution_file.basename)
- sol000
- sol001

hints:
  DockerRequirement:
    dockerPull: git.astron.nl:5000/ssw-ksp/solar-im-compressing:latest

requirements:
  InitialWorkDirRequirement:
    listing: 
      - entry: $(inputs.solution_file)
        writable: true

        