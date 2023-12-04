---
title: 'lofarSun a toolset for the solar radio imaging spectroscopy data processing of LOFAR'
tags:
  - Python
  - Radio interferometry
  - astronomy
  - Solar physics
authors:
  - name: Peijin Zhang
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: LOFAR SSWKSP
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 3

affiliations:
 - name: Center for Solar-Terrestrial Research, New Jersey Institute of Technology, Newark, NJ, USA
   index: 1
 - name: Cooperative Programs for the Advancement of Earth System Science, University Corporation for Atmospheric Research, Boulder, CO, USA
   index: 2
 - name: ASTRON – The Netherlands Institute for Radio Astronomy, Oude Hoogeveensedijk 4, 7991 18 PD Dwingeloo, The Netherlands
date: 02 December 2023
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
#aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
#aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

Low frequency radio observations of the Sun are a powerful tool for studying, monitoring and forecasting solar activity. The LOw Frequency ARray (LOFAR) is a new generation of radio interferometer that is capable of observing the Sun at frequencies below 240 MHz. The LOFAR Solar and Space Weather Key Science Project (KSP) is a community-based project that aims to develop and implement the data processing tools for the solar radio imaging spectroscopy data processing of LOFAR. 
We developed a set of Python tools, called `lofarSun`, dedicated for the solar radio imaging spectroscopy data processing of LOFAR. The lofarSun tools are designed to be modular and flexible, and can be easily adapted to other solar radio observations.

# Statement of need

The Low Frequency Array (LOFAR) [@vanHaarlem:2013], is an advanced radio telescope network primarily located in the Netherlands, with additional stations spread across Europe. 
This network is notable for its use of a large number of small antennas rather than a few large dishes, allowing it to operate at low radio frequencies. 
The cutting edge performance of LOFAR brings benefit in multiple science field in astromony, including solar and spaceweather studies.


ASTRON has developed a set of software for LOFAR data reduction, while most of which are dedicated for astromical observations.
To exploite the resolution power of LOFAR for solar and spaceweather studies, we build this toolset `lofarSun` based on the original LOFAR data processing procedures.

Documentation is available at [https://lofar-sun-tools.readthedocs.io/en/latest/](https://lofar-sun-tools.readthedocs.io/en/latest/)

# Data processing procedures

## Dynamic spectrum (beamformed data)

`lofarSun.BF` 

The RFI flagging uses a feature matching based method [@zhang:2023] available both on CPU and GPU

## Interferometric imaging

The preprocessing is based on the LINC pipeline [@GasperinCalib:2019]. Correcting the amplitude and phase of solar radio observation with the measurements of A-team sources reference the skymodel  [@GasperinAteam:2019].
The observaiton of solar interferometry is calibrated with A team sources. During observation, there are simutanously two beams, one pointing at the target (Sun), one pointing at the calibrator.

After pre-processing, the 2DiFFT and de-convolution is done with `WSClean` [@offringa2014wsclean], then we have the imaging in astromocal coordinates.

Then we do post processing with `lofarSun` on the images.
In this package, the corresponding module is
`lofarSun.IM`


## Command-Line Interface tools

`lofarSun.cli`

Some useful tools to do interactive inspections for the data processing


# Acknowledgements

LOFAR is the LOw Frequency ARray designed and constructed by ASTRON. It has observing, data processing, and data storage facilities in several countries, which are owned by various parties (each with their own funding sources), and are collectively operated by the ILT foundation under a joint scientific policy. The ILT resources have benefited from the following recent major funding sources: CNRS-INSU, Observatoire de Paris and
Universite d’Orleans, France; BMBF, MIWF-NRW, MPG, Germany; Science Foundation Ireland (SFI), Department of Business, Enterprise and Innovation
(DBEI), Ireland; NWO, The Netherlands; The Science and Technology Facilities
Council, UK; Ministry of Science and Higher Education, Poland; Istituto
Nazionale di Astrofisica (INAF). This research has made use of the University of
Hertfordshire high-performance computing facility (https://uhhpc.herts.ac.uk/) and the LOFAR-UK compute facility, located at the University of
Hertfordshire and supported by STFC (ST/P000096/1).

We acknowledge contributions from ASTRON and LOFAR SSWKSP for building LOFAR data processing pipeline and operating the observation.

# References