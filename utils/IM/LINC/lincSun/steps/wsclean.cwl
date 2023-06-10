#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

inputs:
- id: msin
  type: Directory
  inputBinding:
    position: 2
- id: n_intervals
  type: int
outputs:
- id: outputImages
  type: File[]
  outputBinding:
    glob: '*image.fits'
- id: outputPSF
  type: File[]
  outputBinding:
    glob: '*psf.fits'
- id: outputModel
  type: File[]
  outputBinding:
    glob: '*model.fits'
- id: outputDirty
  type: File[]
  outputBinding:
    glob: '*dirty.fits'


baseCommand: 
 - bash
 - script.sh

successCodes:
  - 0
  - 11
  - 139 
hints:
- class: DockerRequirement
  dockerPull: astronrd/linc:latest
- class: ResourceRequirement
  coresMin: 10
requirements:
- class: InlineJavascriptRequirement
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.msin)
    writable: true
  - entryname: script.sh
    entry: |
      #!/bin/bash

      wsclean -j $(runtime.cores) \
            -mem 50 \
            -weight briggs 0.2 \
            -size 512 512 \
            -pol I \
            -multiscale \
            -data-column DATA \
            -niter 5000 \
            -no-reorder \
            -no-update-model-required \
            -mgain 0.8 \
            -scale 30asec \
            -maxuvw-m 3000 \
            -auto-mask 6 \
            -auto-threshold 2 \
            -fit-beam \
            -make-psf \
            -intervals-out $(inputs.n_intervals) \
            -name $(inputs.msin.basename.split('.')[0]) \
            $1
