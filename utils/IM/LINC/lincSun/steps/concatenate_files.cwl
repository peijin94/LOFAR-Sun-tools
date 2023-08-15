class: CommandLineTool
cwlVersion: v1.2
id: concatfiles
baseCommand:
  - bash 
  - bulk_rename.sh
inputs:
  - id: file_list
    type: File[]
    inputBinding:
      position: 0
  - id: file_prefix
    type: string
  - id: file_suffix
    type: string?
    default: log
  - id: execute
    type: boolean?
    default: true
outputs:
  - id: output
    type: File
    outputBinding:
      glob: "$(inputs.file_prefix).$(inputs.file_suffix)"
label: concatfiles
requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entryname: bulk_rename.sh
        entry: |
          #!/bin/bash
          set -e
          FILE_LIST=("\${@}")
          FILE_PREFIX=$(inputs.file_prefix)
          FILE_SUFFIX=$(inputs.file_suffix === null ? '' : inputs.file_suffix)
          cat "\${FILE_LIST[@]}" > $FILE_PREFIX.$FILE_SUFFIX
        writable: false
  - class: InlineJavascriptRequirement
