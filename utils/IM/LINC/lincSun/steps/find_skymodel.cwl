#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
inputs:
- id: msin
  type: Directory[]
  inputBinding:
    position: 1
    itemSeparator: ","

- id: ATeam_skymodel
  type: File
  inputBinding:
    position: 2

outputs:
- id: skymodel_file
  type: File
  outputBinding:
    glob: 'calibrator.skymodel'
- id: target_source
  type: string
  outputBinding:
    glob: target_source
    loadContents: true
    outputEval: $(self[0].contents.trim())

baseCommand:
- python3
- script.py

hints:
  DockerRequirement:
    dockerPull: astronrd/linc
  NetworkAccess:
    networkAccess: false

stdout: target_source
requirements:
- class: InlineJavascriptRequirement
- class: InitialWorkDirRequirement
  listing:
  - entryname: script.py
    entry: |
      import sys
      from casacore.tables import table
      import os
      CAL_MAP_LBA = {
          'CasA': 'CasA_4_patch',
          'VirA': 'VirA_4_patch',
          'Tau': 'TauAGG',
          'Cyg': 'CygAGG'
      } # LBA
      CAL_MAP = {
          'CasA': 'CasA_4_patch',
          'VirA': 'VirA_4_patch',
          'Tau': 'TauAGG',
          'Cyg': 'CygAGG'
      } # LBA
      CAL_MAP = {
          'CasA': 'CasA',
          'VirA': 'VirA',
          'Tau': 'TauA',
          'Cyg': 'CygA'
      } # HBA
      
      os.system('cp '+sys.argv[2]+' $PWD/calibrator.skymodel')
      ms_in = table(sys.argv[1].split(",")[0] + '/POINTING', ack=False)
      print(CAL_MAP[ms_in[0]['NAME']])