class: CommandLineTool
cwlVersion: v1.2
id: make_parset
label: define_parset
inputs:
  - id: raw_data
    type: boolean?
    default: false
  - id: demix
    type: boolean?
    default: false
  - id: filter_baselines
    type: string?
    default: '[CR]S*&'
  - id: memoryperc
    type: int?
    default: 15
  - id: baselines_to_flag
    type: string[]?
    default: []
  - id: elevation_to_flag
    type: string?
    default: '0deg..15deg'
  - id: min_amplitude_to_flag
    type: float?
    default: 1e-30
  - id: timestep
    type: int?
    default: 1
  - id: freqstep
    type: int?
    default: 16
 
outputs:
  - id: output
    type: File
    outputBinding:
      glob: DP3.parset
baseCommand:
  - cp
arguments:
  - prefix: ''
    shellQuote: false
    position: 0
    valueFrom: input.parset
  - prefix: ''
    shellQuote: false
    position: 0
    valueFrom: DP3.parset
requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: input.parset
        entry: |+
          steps                               =  [avg]
          #
          flagedge.type                       =   preflagger
          flagedge.chan                       =   [0..nchan/32-1,31*nchan/32..nchan-1]
          #
          aoflag.type                         =   aoflagger
          aoflag.memoryperc                   =   $(inputs.memoryperc)
          aoflag.keepstatistics               =   false
          #
          avg.type                            =   average
          avg.timestep                        =   $(inputs.timestep)
          avg.freqstep                        =   $(inputs.freqstep)
          
