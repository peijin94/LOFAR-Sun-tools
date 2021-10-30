import os
import glob

for filename in glob.glob("*SB*.tar*"):
  outname=filename.split("%")[-1]
  os.rename(filename, outname)
  os.system('tar -xvf '+outname)
  os.system('rm -r '+outname )

  print outname+' untarred.'