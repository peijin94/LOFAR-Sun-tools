#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.2
id: losoto_plot

doc: |
  This operation for LoSoTo implements basic plotting WEIGHT:
   flag-only compliant, no need for weight

requirements:
  InlineJavascriptRequirement:
    expressionLib:
      - { $include: utils.js}
  InitialWorkDirRequirement:
    listing:
      - entryname: 'parset.config'
        entry: $(get_losoto_config('PLOT').join('\n'))
      - entryname: $(inputs.input_h5parm.basename)
        entry: $(inputs.input_h5parm)
        writable: true
      - entryname: run_losoto_plot.sh
        entry: |
          #!/bin/bash
          set -e
          INPUT_H5PARM=$(inputs.input_h5parm.basename)
          DO_PLOTS=$(inputs.execute)
          if [ "$DO_PLOTS" = "true" ]; then
            losoto --verbose $INPUT_H5PARM parset.config
          else
            echo Skipped plotting 3rd order tec solutions
          fi


baseCommand: "bash"

arguments:
  - run_losoto_plot.sh

hints:
  DockerRequirement:
    dockerPull: astronrd/linc

inputs:
  - id: input_h5parm
    type: File
    #format: lofar:#H5Parm
  - id: execute
    type: boolean?
    default: true
  - id: soltab
    type: string
    doc: "Tabs to plot"


  - id: axesInPlot
    type: string[]?
    default: []
    doc: |
      1- or 2-element array which says the coordinates to plot (2 for 3D plots).
  - id: axisInTable
    type: string?
    doc: |
      the axis to plot on a page - e.g. ant to get all antenna's on one file.
  - id: axisInCol
    type: string?
    doc: |
      The axis to plot in different colours - e.g. pol to get correlations with
       different colors.
  - id: axisDiff
    type: string?
    doc: |
      This must be a len=2 axis and the plot will have the differential value
      - e.g. 'pol' to plot XX-YY.
  - id: NColFig
    type: int?
    doc: |
      Number of columns in a multi-table image. By default is automatically
      chosen.
  - id: figSize
    type: int[]
    default: [0,0]
    doc: |
      Size of the image [x,y], if one of the values is 0, then it is
      automatically chosen. By default automatic set.
  - id: markerSize
    type: int?
    default: 2
    doc: |
      Size of the markers in the 2D plot. By default 2.
  - id: minmax
    type: float[]?
    doc: |
      Min max value for the independent variable (0 means automatic).
  - id: time.minmaxstep
    type: float[]?
    doc: |
      Step size in time for subsequent plotting
  - id: log
    type: string?
    doc: |
      Use Log='XYZ' to set which axes to put in Log.
  - id: plotFlag
    type: boolean?
    default: false
    doc: Whether to plot also flags as red points in 2D plots.
  - id: doUnwrap
    type: boolean?
    default: false
    doc: Unwrap phases.
  - id: refAnt
    type: string?
    default: ''
    doc: |
      Reference antenna for phases. By default None.
  - id: soltabsToAdd
    type: string?
    doc: |
      Tables to “add” (e.g. 'sol000/tec000'), it works only for tec and clock
       to be added to phases.
  - id: makeAntPlot
    default: false
    type: boolean?
    doc: |
       Make a plot containing antenna coordinates in x,y and in color the value
        to plot, axesInPlot must be [ant].
  - id: makeMovie
    default: false
    type: boolean?
    doc: |
      Make a movie summing up all the produced plots.
  - id: prefix
    type: string?
    default: 'losoto.plot.'
    doc: |
      Prefix to add before the self-generated filename.
  - id: ncpu
    type: int?
    doc: Number of cpus, by default all available.

outputs:
  - id: output_plots
    type: File[]
    outputBinding:
      glob: "$(inputs.prefix)*.png"
  - id: logfile
    type: File[]
    outputBinding:
      glob: '$(inputs.input_h5parm.basename)-losoto*.log'
  - id: parset
    type: File
    outputBinding:
      glob: parset.config

stdout: $(inputs.input_h5parm.basename)-losoto.log
stderr: $(inputs.input_h5parm.basename)-losoto_err.log


$namespaces:
  lofar: https://git.astron.nl/eosc/ontologies/raw/master/schema/lofar.owl
$schemas:
  - https://git.astron.nl/eosc/ontologies/raw/master/schema/lofar.owl
