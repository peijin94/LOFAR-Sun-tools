class: Workflow
cwlVersion: v1.2
id: dp3_prep_cal
label: dp3_prep_cal
inputs:
  - id: max_dp3_threads
    type: int?
    default: 10
  - id: baselines_to_flag
    type: string[]?
    default: []
  - id: elevation_to_flag
    type: string?
    default: '0deg..15deg'
  - id: min_amplitude_to_flag
    type: float?
    default: 1e-30
  - id: memoryperc
    type: int?
    default: 20
  - id: raw_data
    type: boolean?
    default: false
  - id: demix
    type: boolean?
    default: false
  - id: msin
    type: Directory
  - id: msin_baseline
    type: string?
    default: '*&'
  - id: timestep
    type: int?
    default: 1
  - id: freqstep
    type: int?
    default: 16
outputs:
  - id: msout
    outputSource:
      - dp3_execute/msout
    type: Directory
  - id: logfile
    outputSource:
      - save_logfiles/dir
    type: Directory
steps:
  - id: define_parset
    in:
      - id: raw_data
        source: raw_data
      - id: demix
        source: demix
      - id: filter_baselines
        source: msin_baseline
      - id: memoryperc
        source: memoryperc
      - id: baselines_to_flag
        source:
          - baselines_to_flag
      - id: elevation_to_flag
        source: elevation_to_flag
      - id: min_amplitude_to_flag
        source: min_amplitude_to_flag
      - id: timestep
        source: timestep
      - id: freqstep
        source: freqstep
    out:
      - id: output
    run: ../steps/dp3_make_parset_cal.cwl
    label: make_parset
  - id: dp3_execute
    in:
      - id: max_dp3_threads
        source: max_dp3_threads
      - id: parset
        source: define_parset/output
      - id: msin
        source: msin
      - id: msout_name
        source: msin
        valueFrom: $("out_"+inputs.msin.basename)
      - id: autoweight
        source: raw_data
      - id: baseline
        source: msin_baseline
      - id: output_column
        default: DATA
      - id: input_column
        default: DATA
      - id: storagemanager
        default: Dysco
      - id: databitrate
        default: 0
    out:
      - id: msout
      - id: logfile
    run: ../steps/dp3_prep_cal.cwl
    label: DP3.Execute

  - id: save_logfiles
    in:
      - id: files
        linkMerge: merge_flattened
        source:
          - dp3_execute/logfile
      - id: sub_directory_name
        default: logs
    out:
      - id: dir
    run: ./../steps/collectfiles.cwl
    label: save_logfiles
    scatter: files
  
#  - id: concat_logfiles_dp3
#    in:
#      - id: file_list
#        source:
#          - dp3_execute/logfile
#      - id: file_prefix
#        default: dp3
#    out:
#      - id: output
#    run: ../steps/concatenate_files.cwl
#    label: concat_logfiles_dp3
#    scatter: file_list
requirements:
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement
