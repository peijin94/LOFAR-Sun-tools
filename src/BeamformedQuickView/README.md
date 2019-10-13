# LOFAR data processing tool

## example 

```python
from lofarSun.lofarData import LofarDataBF

lofar_bf = LofarDataBF()
lofar_bf.load_sav("path/to/data.sav")
[X,Y,data_bf] = lofar_bf.bf_image_by_idx(30,100)
```

![demo](https://raw.githubusercontent.com/Pjer-zhang/LOFAR_Solar/master/src/img/demo.gif)