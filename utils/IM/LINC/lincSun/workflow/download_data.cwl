class: Workflow
cwlVersion: v1.2

inputs:
- id: msin
  type: string[]
outputs:
- id: msout
  type: Directory[]
  outputSource:
  - fetch_data/uncompressed

requirements:
- class: ScatterFeatureRequirement    

steps:
- id: fetch_data
  scatter:
  - surl_link
  in: 
    - id: surl_link
      source: msin
  out:
  - uncompressed
  run: ../steps/fetch_data.cwl