cwlVersion: 'v1.2'
class: 'CommandLineTool'
hints: 
- class: DockerRequirement
  dockerPull: astronrd/linc:latest
requirements:
- class: InlineJavascriptRequirement
- class: InitialWorkDirRequirement
  listing:
    - entryname: script.py
      entry: |
        import sys
        import json
        from casacore.tables import table
        main_table=table(sys.argv[1])
        antenna_table=table(sys.argv[1] + '/ANTENNA')
        samples_dt = $(inputs.sample_size_in_s)
        n_antenna = antenna_table.nrows()
        n_baselines = n_antenna * (n_antenna + 1) // 2
        n_times = main_table.nrows() // n_baselines
        start_time = main_table.getcell('TIME', 0)
        end_time = main_table.getcell('TIME', n_times - 1)
        delta_t = main_table.getcell('TIME', n_baselines) - start_time
        n_samples_per_dt = int(samples_dt / delta_t)
        samples = int(n_times / (samples_dt / delta_t))
        real_dt = n_times // samples * delta_t
        out = {
            'start_time': start_time,
            'end_time': end_time,
            'n_time_samples': n_times,
            'n_visibilities': main_table.nrows(),
            'n_samples_per_dt': n_samples_per_dt,
            'delta_t': real_dt,
            'samples': samples
        }
        with open('results.json', 'w') as f_out:
          json.dump(out, f_out, indent=4)

baseCommand:
  - python3
  - script.py
inputs: 
  - id: msin
    type: Directory
    inputBinding: 
      position: 1
  - id: sample_size_in_s
    default: 60
    type: int
    
outputs: 
  - id: start_time
    type: float
    outputBinding: 
      glob: results.json
      loadContents: true
      outputEval: $(JSON.parse(self[0].contents)['start_time'])
  - id: end_time
    type: float
    outputBinding: 
      glob: results.json
      loadContents: true
      outputEval: $(JSON.parse(self[0].contents)['end_time'])
  - id: n_time_samples
    type: int
    outputBinding: 
      glob: results.json
      loadContents: true
      outputEval: $(JSON.parse(self[0].contents)['n_time_samples'])
  - id: delta_t
    type: float
    outputBinding: 
      glob: results.json
      loadContents: true
      outputEval: $(JSON.parse(self[0].contents)['delta_t'])
  - id: samples
    type: int
    outputBinding: 
      glob: results.json
      loadContents: true
      outputEval: $(JSON.parse(self[0].contents)['samples'])
  - id: n_visibilities
    type: int
    outputBinding: 
      glob: results.json
      loadContents: true
      outputEval: $(JSON.parse(self[0].contents)['n_visibilities'])
