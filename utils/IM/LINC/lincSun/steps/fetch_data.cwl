id: fetchdata
label: fetch_data
class: CommandLineTool
cwlVersion: v1.2
inputs: 
  - id: surl_link
    type: string
    inputBinding:
      position: 0
outputs: 
  - id: uncompressed
    type: Directory
    outputBinding:
      glob: 'out/*'
baseCommand: 
 - 'bash'
 - 'fetch.sh'
doc: 'Untar a compressed file'
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entryname: 'fetch.sh' 
        entry: |
          #!/bin/bash
          mkdir out
          cd out
          if [[ "$1" == *"lta-head.lofar.psnc.pl"* ]]; then
              cd ..
              wget --no-check-certificate --read-timeout=5 --timeout 5 https://lta-download.lofar.psnc.pl/lofigrid/SRMFifoGet.py\?surl\=$1
              cd out
          else
              gfal-copy $1 ..
          fi
          tar -xvf ../*.tar
    
