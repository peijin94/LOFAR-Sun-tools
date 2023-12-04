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

affiliations:
 - name: Center for Solar-Terrestrial Research, New Jersey Institute of Technology, Newark, NJ, USA
   index: 1
 - name: Cooperative Programs for the Advancement of Earth System Science, University Corporation for Atmospheric Research, Boulder, CO, USA
   index: 2
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

# Modules

## Dynamic spectrum (beamformed data)

`lofarSun.BF` 

The RFI flagging [@zhang:2023]

## Interferometric imaging

`lofarSun.IM`

Uses the result of lincSun, and do the post processings

## Command-Line Interface tools

`lofarSun.cli`

Some useful tools to do interactive inspections for the data processing


# Acknowledgements

We acknowledge contributions from ASTRON and LOFAR SSWKSP for building LOFAR data processing pipeline and operating the observation.

# References