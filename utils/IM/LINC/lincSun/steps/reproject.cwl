class: CommandLineTool
cwlVersion: 'v1.2'
hints:
- class: DockerRequirement
  dockerPull: git.astron.nl:5000/ssw-ksp/solar-im-compressing:latest
requirements:
- class: NetworkAccess
  networkAccess: True
baseCommand: 
 - reproject.py

arguments:
- position: 2
  valueFrom: 'out'
inputs:
- id: fits_files
  type: File[]
  inputBinding:
    position: 1


outputs: 
- id: preview_video
  type: File
  outputBinding:
    glob: out/*.mp4
- id: reprojected_images
  type: File[]
  outputBinding:
    glob: out/*.fits