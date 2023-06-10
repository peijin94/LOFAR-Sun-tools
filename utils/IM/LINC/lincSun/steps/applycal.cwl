#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.msin)
        writable: true
inputs:
- id: msin
  type: Directory
  inputBinding:
    prefix: msin=
    separate: false
- id: solutions
  type: File
outputs: 
- id: msout
  type: Directory
  outputBinding:
    glob: CORRECTED_$(inputs.msin.basename)
 
baseCommand: DP3
arguments:
- steps=[apply_phase, apply_amp, applybeam]
- msin.datacolumn=DATA
- applybeam.updateweights=true
- apply_phase.updateweights=true
- apply_phase.correction=phase000
- apply_phase.solset=sol001
- apply_phase.type=applycal
- apply_phase.parmdb=$(inputs.solutions.path)
- apply_amp.updateweights=true
- apply_amp.solset=sol001
- apply_amp.correction=amplitude000
- apply_amp.parmdb=$(inputs.solutions.path)
- apply_amp.type=applycal
- msout=CORRECTED_$(inputs.msin.basename)

hints:
- class: DockerRequirement
  dockerPull: astronrd/linc:latest
