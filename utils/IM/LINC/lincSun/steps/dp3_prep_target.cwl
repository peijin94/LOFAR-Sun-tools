class: CommandLineTool
cwlVersion: v1.2
id: dp3
baseCommand:
  - DP3
inputs:
  - id: max_dp3_threads
    type: int?
    inputBinding:
      position: 0
      prefix: numthreads=
      separate: false
  - id: parset
    type: File?
    inputBinding:
      position: -1
  - id: msin
    type: Directory?
    inputBinding:
      position: 0
      prefix: msin=
      separate: false
    doc: Input Measurement Set
  - id: solutions
    type: File?
    doc: Input Solution Set
  - id: msout_name
    default: "."
    type: string?
    inputBinding:
      position: 0
      prefix: msout=
      separate: false
    doc: Output Measurement Set
  - id: autoweight
    default: false
    type: boolean?
    inputBinding:
      position: 0
      prefix: 'msin.autoweight=True'
  - id: baseline
    default: ''
    type: string?
    inputBinding:
      position: 0
      prefix: 'msin.baseline='
      separate: false
  - id: output_column
    default: DATA
    type: string?
    inputBinding:
      position: 0
      prefix: 'msout.datacolumn='
      separate: false
  - id: input_column
    default: DATA
    type: string?
    inputBinding:
      position: 0
      prefix: 'msin.datacolumn='
      separate: false
  - id: writefullresflag
    type: boolean?
    default: false
    inputBinding:
      prefix: msout.writefullresflag=True
  - id: overwrite
    type: boolean?
    default: false
    inputBinding:
      prefix: msout.overwrite=True
  - id: storagemanager
    type: string?
    default: ""
    inputBinding:
      prefix: msout.storagemanager=
      separate: false
  - id: databitrate
    type: int?
    default: 0
    inputBinding:
      prefix: msout.storagemanager.databitrate=
      separate: false
  - id: apply_tec_correction
    type: boolean?
    default: false
    inputBinding:
      position: 0
      prefix: 'applytec.parmdb='
      separate: false
      valueFrom: $(inputs.solutions.path)
  - id: apply_rm_correction
    type: boolean?
    default: true
    inputBinding:
      position: 0
      prefix: 'applyRM.parmdb='
      separate: false
      valueFrom: $(inputs.solutions.path)
  - id: apply_phase_correction
    type: boolean?
    default: false
    inputBinding:
      position: 0
      prefix: 'applyphase.parmdb='
      separate: false
      valueFrom: $(inputs.solutions.path)
  - id: apply_clock_correction
    type: boolean?
    default: true
    inputBinding:
      position: 0
      prefix: 'applyclock.parmdb='
      separate: false
      valueFrom: $(inputs.solutions.path)
  - id: skymodel
    type:
      - File
      - Directory
    inputBinding:
        position: 0
        prefix: demix.skymodel=
        separate: false
  - id: save2json1
    default: true
    type: boolean?
    inputBinding:
      position: 0
      prefix: count1.savetojson=True
  - id: jsonfilename1
    type: string?
    default: 'out1.json'
    inputBinding:
      prefix: count1.jsonfilename=
      separate: false
  - id: save2json2
    default: true
    type: boolean?
    inputBinding:
      position: 0
      prefix: count2.savetojson=True
  - id: jsonfilename2
    type: string?
    default: 'out2.json'
    inputBinding:
      prefix: count2.jsonfilename=
      separate: false
arguments:
  - applyPA.parmdb=$(inputs.solutions.path)
  - applybandpass.parmdb=$(inputs.solutions.path)
outputs:
  - id: msout
    doc: Output Measurement Set
    type: Directory
    outputBinding:
      glob: '$(inputs.msout_name=="." ? inputs.msin.basename : inputs.msout_name)'
  - id: flagged_fraction_dict_initial
    type: string
    outputBinding:
        loadContents: true
        glob: $(inputs.jsonfilename1)
        outputEval: $(JSON.parse(self[0].contents).flagged_fraction_dict)
  - id: flagged_fraction_dict_prep
    type: string
    outputBinding:
        loadContents: true
        glob: $(inputs.jsonfilename2)
        outputEval: $(JSON.parse(self[0].contents).flagged_fraction_dict)
  - id: logfile
    type: File[]
    outputBinding:
      glob: 'DP3*.log'
hints:
  - class: DockerRequirement
    dockerPull: astronrd/linc
stdout: DP3.log
stderr: DP3_err.log
requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 4
