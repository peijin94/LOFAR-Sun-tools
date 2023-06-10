
class: CommandLineTool
cwlVersion: v1.2
id: collectfiles
baseCommand:
  - bash
  - collect_files.sh
inputs:
  - id: start_directory
    type: Directory?
  - id: files
    type:
      - File
      - type: array
        items:
           - File
           - Directory
    inputBinding:
      position: 0
  - id: sub_directory_name
    type: string
outputs: 
  - id: dir
    type: Directory
    outputBinding:
        glob: |
          $(inputs.start_directory === null ? inputs.sub_directory_name: inputs.start_directory.basename)
label: CollectFiles
requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entryname: collect_files.sh
        entry: |
          #!/bin/bash
          set -e
          BASE_DIR="$(inputs.start_directory === null ? "" : inputs.start_directory.basename)"
          SUB_DIR="$(inputs.sub_directory_name)"
          if [ -z "$BASE_DIR" ]
          then
          OUTPUT_PATH=$SUB_DIR
          else
          OUTPUT_PATH=$BASE_DIR/$SUB_DIR
          fi
          echo $OUTPUT_PATH
          mkdir -p $OUTPUT_PATH
          cp -rL $* $OUTPUT_PATH
        writable: false
  - class: InlineJavascriptRequirement
