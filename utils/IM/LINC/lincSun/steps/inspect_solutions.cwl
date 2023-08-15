#!/usr/bin/env cwl-runner

class: Workflow
cwlVersion: v1.2

requirements: 
  - class: MultipleInputFeatureRequirement

inputs:
- id: solution_file
  type: File
- id: soltab
  type: string
  default: sol000
- id: refant
  type: string?
  default: 'CS001HBA0'

outputs:
  - id: inspection
    outputSource:
      - losoto_plot_P3/output_plots
      - losoto_plot_A3/output_plots
    type: File[]
    linkMerge: merge_flattened

steps:
  - id: losoto_plot_P3
    in:
      - id: input_h5parm
        source: solution_file
      - id: soltab
        source: soltab
        default: sol000/phaseOrig
      - id: axesInPlot
        default:
          - time
          - freq
      - id: axisInTable
        default: ant
      - id: minmax
        default:
          - -3.14
          - 3.14
      - id: plotFlag
        default: true
      - id: refAnt
        source: refant
      - id: prefix
        default: polalign_ph_
    out:
      - id: output_plots
      - id: logfile
      - id: parset
    run: LoSoTo.Plot.cwl
    label: losoto_plot
  - id: losoto_plot_A3
    in:
      - id: input_h5parm
        source: solution_file
      - id: soltab
        default: sol000/amplitude000
      - id: axesInPlot
        default:
          - time
          - freq
      - id: axisInTable
        default: ant
      - id: plotFlag
        default: true
      - id: prefix
        default: polalign_amp_
    out:
      - id: output_plots
      - id: logfile
      - id: parset
    run: LoSoTo.Plot.cwl
    label: losoto_plot_A3

