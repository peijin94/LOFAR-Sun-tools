
"""
A script to convert between the J2000 and the sun.
"""

from sunpy.coordinates.sun import sky_position as sun_position
import sunpy.coordinates.sun as sun_coord
import numpy as np

def j2000xy(RA,DEC,t_sun):
    [RA_sun, DEC_sun] = sun_position(t_sun,False)
    rotate_angel = sun_coord.P(t_sun)

    # shift the center and transfer into arcsec
    x_shift = -(RA  - RA_sun.degree)  * 3600
    y_shift = (DEC - DEC_sun.degree) * 3600

    # rotate xy according to the position angle
    xx = x_shift * np.cos(-rotate_angel.rad) - y_shift * np.sin(-rotate_angel.rad)
    yy = x_shift * np.sin(-rotate_angel.rad) + y_shift * np.cos(-rotate_angel.rad)
    return [xx,yy]

