#!/usr/bin/env python

'''
########################################################################

		File:
		solar_pipe.py

	Description:
		This is a Python wrapper around the Default Preprocessing Pipeline
		(DPPP) and WSCLean commands required to produce solar images (fits
		files) from interferometric data, i.e. measurement sets (MS).

	Disclaimer:

		THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
		"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
		LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
		FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
		COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
		SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
		LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
		USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
		ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
		OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
		OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
		SUCH DAMAGE.

	Notes:
		Each LOFAR solar imaging observation may require fine tuning
		of the parset files and how the MSs are reduced. The template
		parsets here will produce an image, but they are generic and
		may not produce the best results.

 	Examples:
		solar_pipe.py --calfolder /path/calms/ --skymodel /path/taurus_1.sourcedb
			--calsource TauAGG --sunfolder /path/sunms/ 
			--time0 20190331_135300 --time1 20190331_135600
	
	Testing:

	 Author:
	   Eoin Carley, Dublin Institute for Advanced Studies
	   eoin.carley@dias.ie

########################################################################
'''

import os
import glob
import numpy as np
import casacore.tables as ct
import datetime
import time
from astropy.time import Time
import argparse

pipet0 = datetime.datetime.utcnow()

def parset_templates(parselect):
	
	# Parset templates for DPPP.

	# The autoweight and average for the Solar MS
	# No flagging is done here.
	awavg = """
	msin={inms}
	msin.autoweight=true
	msout={outms}
	numthreads=4
	steps=[averager]
	averager.timestep=100
	averager.freqstep=1
	"""

	# The autoweight and average for the Calibrator MS
	awavgflg = """
	msin={inms}
	msin.autoweight=true
	msout={outms}
	numthreads=4
	steps=[aoflagger,averager]
	averager.timestep=100
	averager.freqstep=16
	"""

	# The complex gain prediction parset for the Calibrator MS
	# A ready-made skymodel must be supplied.
	predict = """
	msin={inms}
	msout=.
	steps=[gaincal]
	gaincal.usebeammodel=True
	gaincal.solint=4
	gaincal.sources={calsrc}
	gaincal.sourcedb={calmodel}
	gaincal.onebeamperpatch=True
	gaincal.caltype=diagonal
	"""

	applycal = """
	msin={inms}
	msout=.
	msin.datacolumn=DATA
	msout.datacolumn=CORR_NO_BEAM
	numthreads=4
	steps=[applycal]
	applycal.type=applycal
	applycal.parmdb={gainsols}
	applybeam.updateweights=True
	"""

	applybeam = """
	msin={inms}
	msout=.
	msin.datacolumn=CORR_NO_BEAM
	msout.datacolumn=CORRECTED_DATA
	steps=[applybeam]
	applybeam.updateweights=True
	"""
	
	parsets = {'awavg':awavg, 'awavgflg':awavgflg, 'predict':predict, 'applycal':applycal, 'applybeam':applybeam}

	return parsets[parselect]


def run_wsclean(ms, wstemp, t0, t1):
	
	# ms: Name of measurement set on which WSCLEAN is to be run
	# wstemp: Name of the template file for the WSCLEAN command
	# t0, t1: start and end time of interest.

	clean_start = datetime.datetime.utcnow()
	
	# The following finds the time indices of interested.
	obst0 = Time(ct.table(ms+"/OBSERVATION").getcol('LOFAR_OBSERVATION_START')[0]/(3600*24),format="mjd")
	obst0 = obst0.datetime
	obst1 = Time(ct.table(ms+"/OBSERVATION").getcol('LOFAR_OBSERVATION_END')[0]/(3600*24),format="mjd")
	obst1 = obst1.datetime
	obs_duration = (obst1 - obst0).total_seconds()
	print('Observation duration: %s (s)' %(obs_duration))
	dt = ct.table(ms).getcol("EXPOSURE")[0]
	num_samples = int(ct.table(ms+"/POINTING").getcol("INTERVAL")[0]/dt)	
	times = [obst0 + datetime.timedelta(seconds=dt*i) for i in range(0, num_samples)]
	timestamps = [time.mktime(t.timetuple()) for t in times] 
	timestamps = np.array(timestamps)
	t0 = time.mktime(t0.timetuple())
	t1 = time.mktime(t1.timetuple())
	t0ind = np.where(timestamps >= t0)[0][0]
	t1ind = np.where(timestamps <= t1)[0][-1]
	numstep = t1ind - t0ind
	
	# Make the folder where the fits files are generated
	freq = str(int(round(ct.table(ms+"/SPECTRAL_WINDOW").getcol('CHAN_FREQ')[0][0]/1e6)))
	fits_name = ms.split('/')[-1][0:-11]+freq+'MHz'
	outfolder = 'fits_'+freq+'MHz'
	os.system('mkdir -p '+outfolder)

	# Build the WSCLEAN command from the template.
	f = open(wstemp, 'r')
	wsc_cmd = f.readlines()
	wsc_cmd = wsc_cmd[0]#.split("\"")[1]	
	wsc_cmd = wsc_cmd.replace('{inms}', ms).replace('{outfits}', fits_name).replace('{outfolder}', outfolder)
	wsc_cmd = wsc_cmd.replace('{ind0}', str(t0ind)).replace('{ind1}', str(t1ind)).replace('{numint}', str(numstep))
	pfile = open('wsclean_cmd', "w")
	pfile.write(wsc_cmd)
	pfile.close()

	# Execute WSCLEAN.
	os.system('chmod u+x wsclean_cmd')
	os.system('./wsclean_cmd')
	
	totalproctime = (datetime.datetime.utcnow() - clean_start).total_seconds()
	print('Total WSClean time for %s images is %s (s): ' % (str(numstep), str(totalproctime)) )

	return outfolder

def list_sun_calib(sunfolder, calfolder):

	# This function finds the calinbrator MS to match the solar MS, 
	# based on an observation frequency match.

	sunms = np.sort(glob.glob(sunfolder+'*uv.MS'))
	calms = np.sort(glob.glob(calfolder+'*uv.MS'))
	
	sunf0 = np.array([])
	calf0 = np.array([])

	for ms in calms:
                calf0 = np.append(calf0, ct.table(ms+"/SPECTRAL_WINDOW").getcol('CHAN_FREQ')[0][0] )
	
	cali = np.array([], dtype=int)
	for ms in sunms:
		sunf0 = ct.table(ms+"/SPECTRAL_WINDOW").getcol('CHAN_FREQ')[0][0]
		cali = np.append(cali, np.where(calf0 == sunf0))

	calms = calms[cali]
	suncal = list(zip(sunms, calms))	
	print('     Sun       Calibrator     ')
	for i in range(0,len(sunms)): print(suncal[i][0], suncal[i][1])

	return suncal

def write_parset(parset, name, parset_dir='.', run=False):
	pfile = open(parset_dir+name, "w")   
	pfile.write(parset)
	pfile.close()
	
	if run: os.system('DPPP '+parset_dir+name)

def runpipe(suncal, calsource, calmodel, t0, t1):

	# This runs each DPPPP parset file in sequence
	# First the calibrator, then the solar MS.
	# This is followed by a wsclean run.
	# The loop is over multiple measurement sets.

	parset_dir = './parset_pipe/'
	os.system('mkdir -p '+parset_dir)
	
	for mstuple in suncal:
		calavgpar = parset_templates('awavgflg')
		calpredict = parset_templates('predict')
		sunavgpar = parset_templates('awavg')
		sunapplycal = parset_templates('applycal')
		sunapplybeam = parset_templates('applybeam')
		
		sunms = mstuple[0]
		calms = mstuple[1]

		dt = ct.table(sunms).getcol("EXPOSURE")[0]
		num_samples = int(ct.table(sunms+"/POINTING").getcol("INTERVAL")[0]/dt)

		calnew = calms.split('.MS')[0]+'_awflgavg.MS'	
		sunnew = sunms.split('.MS')[0]+'_awavg.MS'
		gainsolutions = calnew +'/instrument/'

		# Process the calibrator MS
		calavgpar = calavgpar.replace('{inms}', calms).replace('{outms}', calnew)
		calpredict = calpredict.replace('{inms}', calnew).replace('{calsrc}', calsource).replace('{calmodel}', calmodel)
		write_parset(calavgpar, 'calavg.parset', parset_dir=parset_dir, run=True)
		write_parset(calpredict, 'calpredict.parset', parset_dir=parset_dir, run=True)

		# Process the solar MS
		sunavgpar = sunavgpar.replace('{inms}', sunms).replace('{outms}', sunnew)
		sunapplycal = sunapplycal.replace('{inms}', sunnew).replace('{gainsols}', gainsolutions)
		sunapplybeam = sunapplybeam.replace('{inms}', sunnew)
		write_parset(sunavgpar, 'sunavg.parset', parset_dir=parset_dir, run=True)
		write_parset(sunapplycal, 'suncal.parset', parset_dir=parset_dir, run=True)
		write_parset(sunapplybeam, 'sunbeam.parset', parset_dir=parset_dir, run=True)

		totalproctime = (datetime.datetime.utcnow() - pipet0).total_seconds()
		print('Raw MS time res: %s' %(dt))
		print('Raw MS number of time slots: %s' %(num_samples))
		print('Total DPPP calibrator and target processing time (s): '+str(totalproctime))
	
		# Runs wsclean on the calibrated solar MS between t0 and t1
		fits_folder = run_wsclean(sunnew, './wsclean.template', t0, t1)

def main():
	'''
	# Need to add the following as inputs, rather than hardcoded here.
	t0 = datetime.datetime(2019, 3, 31, 13, 53, 0)
	t1 = datetime.datetime(2019, 3, 31, 13, 56, 0)
	sunfolder = '/data/scratch/ecarley/EVENT_20190331/L699759/sun/'
	calfolder = '/data/scratch/ecarley/EVENT_20190331/L699755/taua/'
	calmodel = '/data/scratch/ecarley/skymodels/taurus_1.sourcedb'
	calsource = 'TauAGG'
	'''

	parser = argparse.ArgumentParser()
	parser.add_argument('--calfolder', default='/data/scratch/ecarley/EVENT_20190331/L699755/taua/', type = str)
	parser.add_argument('--calmodel', default='/data/scratch/ecarley/skymodels/taurus_1.sourcedb', type = str)
	parser.add_argument('--calsource', default='TauAGG', type = str)
	parser.add_argument('--sunfolder', default='/data/scratch/ecarley/EVENT_20190331/L699759/sun/', type = str)
	parser.add_argument('--time0', default='20190331_135300', type = str)
	parser.add_argument('--time1', default='20190331_135600', type = str)
	args = parser.parse_args()

	t0 = datetime.datetime.strptime(args.time0, '%Y%m%d_%H%M%S')
	t1 = datetime.datetime.strptime(args.time1, '%Y%m%d_%H%M%S')	

	print('Solar pipeline start time: %s' %(pipet0.strftime('%Y-%m-%d %H:%M:%S.%f'))  )
	# On a CEP3 compute node, if these module load commands are unrecognised, 
	# run mannually first in the terminal.
	os.system('module load lofar')
	os.system('module load dp3')
	os.system('module load wsclean')

	# Returns a list of solar raw MS and the associated calibrator MS
	suncaliblist = list_sun_calib(args.sunfolder, args.calfolder)

	# Returns an averaged and calibrated solar MS
	runpipe(suncaliblist, args.calsource, args.calmodel, t0, t1)
	

if __name__ == '__main__':
	main()

