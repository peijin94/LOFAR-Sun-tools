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
  - id: save2json
    default: false
    type: boolean?
    inputBinding:
      position: 0
      prefix: count.savetojson=True
  - id: jsonfilename
    type: string?
    default: 'out.json'
    inputBinding:
      prefix: count.jsonfilename=
      separate: false
outputs:
  - id: msout
    doc: Output Measurement Set
    type: Directory
    outputBinding:
      glob: '$(inputs.msout_name=="." ? inputs.msin.basename : inputs.msout_name)'
  - id: logfile
    type: File[]
    outputBinding:
      glob: 'DP3*.log'
hints:
  - class: DockerRequirement
    dockerPull: astronrd/linc
stdout: DP3_$(inputs.msin.basename).log
stderr: DP3_err_$(inputs.msin.basename).log
requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 8
