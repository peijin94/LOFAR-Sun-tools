#!/usr/bin/env python3

import time
import lofarSun.BF.bftools as bftools
from lofarSun.BF.lofarJ2000xySun import j2000xy
from lofarSun.BF.RFIconvFlag import *
import gc
import matplotlib.pyplot as plt
from astropy.io import fits as fits
import torch
import numpy as np
import matplotlib.dates as mdates
import matplotlib
import h5py
import matplotlib.image as mpimg
import io,os,json
import base64
from argparse import ArgumentParser
import datetime
DESCRIPTION = '''
Split and down sample the dynamic spectrum of LOFAR observation

Input  :  Huge hdf5 file of LOFAR Tied array beam formed observation
Output :  Small fits file with json and png quickview

(by Peijin.Zhang & Pietro Zucca 2019.08)
'''

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

matplotlib.use('agg')

lofar_logo_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAURklEQVR4nLx6CXRcZfn3733vMlsmy2RfmrXpkhRo0i0tXUEE2gKloqiAyidLLShyPi0qKggeFzzfUT9BAY8i8BeqgEilKxQotWu6pk26ZN8nyWSZzH6393/eOzNJppRS6HLPnHbyzr33fX7P/jzvIzLGcJkvppn/URB64S8jFxUAAwi0UYSboY3wLyzCl6kNYiokF0QX5NzEJzQTxmdHIl441ROoMUAEjHyAY7eAmHCizCHmh8oQnLCVIWkm/6ReA/tUEJMApvM7PpNALghAVHqEkIRVORdanOiJ0mUKyCBCgxjez3+SHXBUIXM1Mm6FtTiOH59WGp9VhRjDBLrjSExua8Po/wukdMipIBL/2QhDHULEDV89Rg8j3AktHFU3E0kaMlYjfy2c1YhKg4uCXBIAsZsZI5Qyxnw+nyRJNptt7NeoNPThYWOkm0UC0CKcFMlKLE7qzKTJaURiMHrh3Y2+DfBsRcQTE5RkQebtKPoR16uYNM5LFJ8GABvnS3DUf+DwIXefmxDicrmys7NLSkocDocpGfheXBM5/B9iccDQERUNFYlso84smlEq5lVKU64RJ1US0QfPBrT/f3j3x94rpaLw+yh8hNsSF4VwEQDE1MOko6ujy6+FhA6/erindM21Pp+vsfF0a1sbY8zpdJaXl1dUTAdI4K2fh3e/RByuGAAwDt7QYWhMU2CoRJRpWoFUcb2l+jYxrwTezWh8DN5aCIABpC3G1D/CXmn6qE+w0nMCSFT07hNtJ7uafFQZfW6/oy08/bVvVhSWg6Czs7O2tlYURUEQkp1JVy9aoux5OfDmE8SRGgcQ2yvKBv5OZkBTmBIkFps0eZF12YNSUSXcf0bjI9yEuCjSMe15bhufZBLC448/fnbiDUYoCQQCDcfruwbdLb/eIgri3FuWTSstt0Nuf+Z9dxnt9vZlpLmyc3KysrKam5tzcnL8Pl9KZl4yVYKH3yaClOiGEJeGuSiIRLYDgu4+FTn0ujHQJlasIWX3cUMPNIGE0PdPHjpS5p/bHj4GADdTEhry19fX93sHPS09A+u2eErFXlvQTi1F8yu6X9qrNA5qS/JaTzSlp2dkZmUmJycfO3Zs+vRp6ZmZItMiB9+awHoCasbdM+iIKqdsI1TUOo8oh9+gznKx6gkQHUMfQqDwbAYVkbo0LofzAxDl/UhdR9Oftlfddd2U8vLi3IKOp3dAFnxXJrUcP6XLpHhBZcdTmzLTs7RZGS0nG3OzcrJzc4aHhn0+X/nkMkNTIntfZWqIUIGzXNeYEoIShK5wNRIkjoedAcMONaIc3cD8Hmn+k8RRhv63QAmG3oNgQerieMw+HwlwzSd77nxWHQkV37lAVzRLsr1v5yn/7tPVa1YGRK2loZGVJBcUF3f+8u0kwR6enjLgGyotKklKcTY3NU+ZMoVKVjF/hmXuF201X7HMXi1fuVyetljImUJtqdBVw+eBEiKCCEFMgEEFItu1lv1aa60078ckYx7XIkow+C6shXDOOqscPgKAxSLrsR+9AYKye5dSgT9jyXQ2/HVTStC2YN1tI4PDnU3t4qyc4isrun/zjvrfzoDFsGYlJwk2ySZnZWczKggZRUJavun7s4S0fCG7XCqbZ7lquWXWLWLJHCJKxlAnC4wQUTZpYuOqa03S+5q0xvfluT8grivRux6CAM8WpC2Dtci0B3JOAGZ01Alrfm3PyKEWY16O4LI5rHbn5OzQqZFj6ze4nNlz7vr88NBQZ0u7ZVZezdpVSkN/8JV6979r7SnJFTctIMRkgWHEkyHzw4yYqkhWIaNIrvycZcb1POr2nuS+SLJizBkyg8gOY6hTa91lWfAYsbnQvwlEg3cHcu6CYE2IR2cCMH/Sg0rP6baA1z+683h/z3BLbtjT6Xalu8puntP39omGv292ZmbNuv1az/BQe0OzPCl1/sOrHcundLgiM++53u5wsGh2dOYnasSEE8oMjsSeKk9bIpVfbQy06v1NHMMYa6MYPK16/wnLoiehdmD0CNRhaAPIWHWGU0oAwHMBkNpv/TU1J73irmtOP/MBax3MvnragC1yuu5kakHmlXdc4950vOHljWJImHH7Eo/i62pqy0rPyJ9aemq4syAnz+l0niW9S5AwmYiEpuRYqldB19TmvdztTsRgceiddYRapLlPoH899CH4jnCvai+faAwTbMJ0nepIsPXFXcFur+C0TF+3IhQZ1Z89evXU6qTMlPc2bes0hm/Y8XjJdQv2PfW33Qt/7aoPEYYTPa2RcLggNcvlcn0C9WcgoUJUp+03/t+k1U/wID1RxXWNOFzB7b9X2xsw4wUeoQG0/gBMnWg2H7UB0vj0uyG3t/juhTkLpg192Nq+v1ZsVmoeWjUU8J44VJc1uWDm2hWOlPSujYfd/9pNt/QEatuEoH7VTQtlu/W8SD9TIIBhiAVXCK4C9fg2jmpMxSkluq53HbZcvY6obfAegeKGrQRJVWOKNBEAV1ZfKNBX1zqw9VBvqiaWuSq/cHX/hhNt+2r1eu/s+5YPhL2tDY2FxUX5Syon378sc/ZUKoqDYrD0G4szi/OYYZwv+xNBcFIMTcybTixJSsN2ItsQT3shWY3BNmJPl2beh64/wdAQaULO3aBSFGcMANMNQknn6/tHD3VMu+eapj++GzrW11VohJ20+svXDr/T1LZ3f3hXb/E1V3YTnxII5WflCknW1Ir87FurTjtHcwvz01NdIOetP2dBQWHoYlGVMdKjtR8exwBGiKi7661z1xDSj5H9UAeQXAV7RdQSEuJC03Pvdb1Wmzw5p/KRW5WuHtf6Tnd719FQ+5LN64rmz2nds7d+1Z/tb3d0t3ZELHExG4ZDFzNdGeddgZwDA7dsx4ofCBnFTA3HzDQmhM5w7WsoeohHcUbQ+wLiBVRMAvw71/7t/ftOlt61qOCWat+Rvq6NO7O11IFcGNm2hQ/eiiDp++/J0MFGsqNfGfBZ7FZlxD98onvS9NKMnCzEq5kLA2DwssGRptRtJpJlTAgg1PB2WmoeJIFdPNXT+pB1O0QXYMRVyAzAvZvr+o6fUDsDRV+uyVs5c/R4f/u/d9hOK/32cO68qWUr5+bfXA0meo909H1wqOmF991b6wtvrMqdVR5Nny5YBKYiMUPILtea9+pDnTxOm96GCJLh7RVLFwvZeXD/C0YE9slIngemx41Y5xT4Gt0DH5wcbuhgfi3/pqri2+frXr13w351W3O4ezS1MMtVXZyxdBpbmDfzmytKvrzoikdvTZtZxNhFoj56McNMiiymEOIRmlJE/MTikKu+hK5noGuQnMj8IreQaEHDjVigg3ubtsz/SdrUotHG3sLb58776/2CVRzY03js8Tc6tx0QIDnyXWX/Z9mMR1dRixjf7qJSH1cGFvZ5n77NGO6BKJsrlKkhIbs85cHXybElGNwNRyFm10FMGa/Iol/eXfDkaHvP7Ke+dvjRV3VNm/G9W/KWzxwN+SPegNgVInYxf8VMKotMM0zvR3CBen/WyzBAqf+Nn0T2rSf2CWWdHkn+9jZR+wtOPgZJwKxaJFUlRmJCqn/7VV9vX+v63TfW/mLK/dc1Pf/e7jufkYaU0iVXFd5RM+nW2VTmOTARKRHoJaEe0ZyMyVMXIVpORC8qMCWk9zfCOcMEqSPUlNDY4i7VYOk1kxc9+9DRX/3z1B+2XvnkbVf8dDV0AwJlhsGDOYFJ96Uhe5wU7hOF3KnEmgw9IXHQB5oxtZonQAYQPP2Rzhzlnrjs/qWl9yxRvUE9pAg22aSecXgXoRV7vgg4LUnpNCnNGOqBJMdblFT3tEBaCSkJET8infFkjum8YDOzXG6VmkYok112wSoyXYNhXGQz/WT6ze6FxUGcmSzaNo0Zt8BG3SBOyBkcktm/MCUwsX9EhfFkmxAiXD62J1ymL6JRCx7rsXIz8IOJEJL4n3rABKANo/dvUEeRtoA5lkYO/MN8hkQBMDUiFc8Si6rO6BFdBgSc8TyQIaEpZKg8lYi2XM1zBhHaCFp/CH8EZV9j+QuCG3/JwgFQkb+Cisw/aFv+fROAcT6Nvot3mUTrWhzM2LIAwmJHJCY9IqgNlhyo3WAKRJmm5BnUA1GKtgn4bbp6GekeI5QDYKFRM0GKL5qlJqBBD/I/qd00YjEFNIljCndSWSJWJ9MVHkoMnX8Y032esTderstMDtSw4fPEdCFKgKERRwYQgGr2tMVUEwC1Qcrgd0T6QVXiSOeCi1LLGATR8Lo5notxnnXe9JsA/EPMP0gSekeGkF4CtReql1NoKYi7UVsp/1ftBwLUVcirnjgCIsrGQKs+3Bl9/rIhMGNWixHyJgRjgGZNRrgNukm4vTwOwDqZE6x4EW6RCmeNGz2XgGQEhrSOo2OMuVz0Q2ncBU0ZlzwzIEpi5mQEGvgNlMI2BsBZHWvMD74jFs4aP5iIXoQoJ3fg8pkBdx5Mi6hNe8ZrGkKYpgjpJUJWPjzvmAdT2bCWxgEkz4Mli38ZfJ+6sml6MdMiMXK54du1xl3GcHesr3+pL4NvoTXv092nINliOxIKNSRMqiJyAN5aDsA5F1I6mEFN0aTBfhWnb2QXoR658gaoofGSVJAMnydS+xo3jMugRSbjwntfhcESlJlArlwO7w4oPr6SsigKN5rXAVlf5AFC9cPztnzFSmKxj2uRYRCLI7z/NWOkN1ryXULqTXenNu1RTn1IrI6oNDgkTaGuQrm8Bt0vcQOQHUhfYT5A44cOrhthSeW3djwj5hSKpTVMCcYNiEGUjdGB4LtPx1qCl+oyWa4rwS3/z9wlzn9CmeK3zPwCEXvh2cpT5pT5sE+LFvvmMT8zuE91reRL3oMI7LItXouxNNCsHogtOXLgX8qxrdyvGdoloZ/nYDS4/Vmt/Sh3JDFRE+gadbgsNXei60/QwpzI7LsRd+txHgPIfyCaO6DpMWlytTRlMQuPxlYQiwmBf/9Mdzfy6JhwendRqNdAReX4ttD7zxJb8vj7qcBCXsu8O4UUHe1/5CqQNAUZN0fZHwdAzCZrcg1cN/AfBrdj9B37jY8SQRjXeGYqUsjr+/tDxkiPKYeLh8GkXm07EHj9R+aRR3ydEKhhIWOSbdm30fxTnjKDoeAhnk4zA4mDCaYQSh6DIHJkJx4U80qti+9lgWG+EttGJ7JdH2gZ/dsaY6gzjuHCTIIx/hIqqs37/C9/m6kRLt4xMyOUqX77iscJ6tHxLNd+53Tk3D3G/gkAokJwzkHON/gX/2m0fM92/cNicRVPCccUydCJ1an3NY4+/3W1ZV+sk/wZRcFihQcVIgff9L34LSMcgGgZl7nAk3nLvDvkK5bh+NdNb8lQ8guevMXZf8ZBt8G5qQ7g4CxEerkLm7VF16tHn17BImFemBrxV1OBBwoq2Zbea11yD4mWHaYJnle0jh43mUwx/IOhbb8P7/8nkawm78e2EFnYK+VXONe+SdoeRtvvOMHZX0LlP844oUk8qY+OJ3jewrFV/CYhDTWH1HaP74W7QKWEDcyAwMI+sXCmbem98ozrxitXFnfeCd0LNt5jM9eZEoocfDO88wXd00bsKeaDEzookaCQ7Epeu5Eq/0HdnRAI5HzMruUZhJkJfQyAMQwt69D6G54gWaehZn+k/kDg7w9wDKI8QWEIKGWRAMCkompL1c3S1MU0NfcTBaD3NysN7ymHN2juUxAtnPcTlVAQWdhPHSnJ970u2Jpx4HOgZkdn5iakff6jEyAfnZWIs7B+Nfo3cGYlVWPOB8rJOv8rDzBV5QFSnxAHTGnyqKerNCVHLJgh5s8Q8iuEjCIi2cyTYAZDYyGf3t+kdTeYn+PcN0hW8xDASIiMVGShEcGV7/zmK4K9A7XXAiHoBqb8jjufs81+nHXYwzQR3Y+6FRjeyRccV2D2O5rb639lrT7QTuyp46oyBsMM+EwNc3aKMpFtRLRCMLmlqUyLsEiQu0tBHAd2xhvAWGBIKl+YdMdzVP8Qh1eDRKAZKHkEpb/6uMmVj5lWiRqKOoRjN2Fkt5m+5uOqNwx6VeDNdcrRjURyQLKcyb/oiWo052P6uFqfeczKEut0vs4iAQLDuvh++w0Pw/0MTn6H67lmoPi7KPvtOWZWzjFuY3Bb0YZR/xWegXBWSpj8FAq+GzmyNbT1V7qnnViSTMfHPibDI/HCDmcPF1HSlRDUoFhUZV/+U6m0DCceQM9Lsfqk5McoefLcEzfnHngyMRhhNH4X3c9xluhA+rWY/gfDKA3veTGy92VjqJtrs2Qz3QtLcCZn3zA+nWho3HIMTcyZall4v6V6BfFvRsODCHfwjYgdU36P3HviB68f650/cWLLiPmsnj+jeR3UEXOAUkL+GpT+0AinKnWbIgfW670NnJFUNPVePHtAiApKU3i1xHRic4rF8yyzvypPX0C0OjT+2Mw0TR45r8C053lqcx4DgOczM8eiRwwInEDT9zG0MYZLTEbeHSj8FqRKbaBXbdimtu0z+huNUTcn0dATtMaMuES20bRJQtZUqXyxNGWRkGqD/79o+y08W2I3CzLy1qL0CQjOizYzF0cRf13fq2j/OfwNUWicZyk1yF6FrFUQJzFF0If79ZFeFvRC8fPchhAi2Yg1idrTaFoeTUkhQhDherhfx8Am+Jti/KVmTVL8MyTPSdjuogFA3L3y5CcI9/+g53n4D2JsKIVHvUlIqkDaQtgKzUHjFBALf8oIct1TPVyGw7sRaIYyiLF0RpSRdh0KvgPX53Gp50YxkTdMw/B29L2MkQ8R6cRYcJs4bowJi2Pr0X9FCts0pK9E9leQNDN2E2OftoP22SZ3WUKvV/PCuxMjOxGoQ/AUNA/0gBkiJu5jmr6QDDkXjkokVSF1KaebWsyfjWj7/9NTckHT62N524SN1SEo3VD6eVarjYKFze6lHWIa5CyeilnyeT48/o7PPvYdvf43AAD//yvju0WgtYfMAAAAAElFTkSuQmCC'
idols_logo_base64 = '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77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+Cjx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDQuNC4wLUV4aXYyIj4KIDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgIHhtbG5zOmlwdGNFeHQ9Imh0dHA6Ly9pcHRjLm9yZy9zdGQvSXB0YzR4bXBFeHQvMjAwOC0wMi0yOS8iCiAgICB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIKICAgIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiCiAgICB4bWxuczpwbHVzPSJodHRwOi8vbnMudXNlcGx1cy5vcmcvbGRmL3htcC8xLjAvIgogICAgeG1sbnM6R0lNUD0iaHR0cDovL3d3dy5naW1wLm9yZy94bXAvIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iCiAgIHhtcE1NOkRvY3VtZW50SUQ9ImdpbXA6ZG9jaWQ6Z2ltcDphZmNhOTY3Zi0wZGE0LTQwNzEtYmYyMi04ZGJkNGI0NWUzZDgiCiAgIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6ZmE2MzUxMWEtYzM0Mi00MDc3LTgwZGQtOTFkODEyMzMwZjQ1IgogICB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6YWRlZWRhNGEtMDU0OS00ZGJkLWExMzQtNDVlMjZmNTkzNTg0IgogICBHSU1QOkFQST0iMi4wIgogICBHSU1QOlBsYXRmb3JtPSJMaW51eCIKICAgR0lNUDpUaW1lU3RhbXA9IjE2NjQzNzQ0MTI3ODEwNzciCiAgIEdJTVA6VmVyc2lvbj0iMi4xMC4xOCIKICAgZGM6Rm9ybWF0PSJpbWFnZS9wbmciCiAgIGV4aWY6UGl4ZWxYRGltZW5zaW9uPSI4NTAiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIzNTAiCiAgIHhtcDpDcmVhdG9yVG9vbD0iR0lNUCAyLjEwIj4KICAgPGlwdGNFeHQ6TG9jYXRpb25DcmVhdGVkPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6TG9jYXRpb25DcmVhdGVkPgogICA8aXB0Y0V4dDpMb2NhdGlvblNob3duPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6TG9jYXRpb25TaG93bj4KICAgPGlwdGNFeHQ6QXJ0d29ya09yT2JqZWN0PgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6QXJ0d29ya09yT2JqZWN0PgogICA8aXB0Y0V4dDpSZWdpc3RyeUlkPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6UmVnaXN0cnlJZD4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZDAyODJiYmItN2VlZC00ZWEyLThjNjYtMTY1MGJlZjM1NGFjIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKExpbnV4KSIKICAgICAgc3RFdnQ6d2hlbj0iKzAyOjAwIi8+CiAgICA8L3JkZjpTZXE+CiAgIDwveG1wTU06SGlzdG9yeT4KICAgPHBsdXM6SW1hZ2VTdXBwbGllcj4KICAgIDxyZGY6U2VxLz4KICAgPC9wbHVzOkltYWdlU3VwcGxpZXI+CiAgIDxwbHVzOkltYWdlQ3JlYXRvcj4KICAgIDxyZGY6U2VxLz4KICAgPC9wbHVzOkltYWdlQ3JlYXRvcj4KICAgPHBsdXM6Q29weXJpZ2h0T3duZXI+CiAgICA8cmRmOlNlcS8+CiAgIDwvcGx1czpDb3B5cmlnaHRPd25lcj4KICAgPHBsdXM6TGljZW5zb3I+CiAgICA8cmRmOlNlcS8+CiAgIDwvcGx1czpMaWNlbnNvcj4KICAgPGV4aWY6VXNlckNvbW1lbnQ+CiAgICA8cmRmOkFsdD4KICAgICA8cmRmOmxpIHhtbDpsYW5nPSJ4LWRlZmF1bHQiPlNjcmVlbnNob3Q8L3JkZjpsaT4KICAgIDwvcmRmOkFsdD4KICAgPC9leGlmOlVzZXJDb21tZW50PgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+cyPnDwAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAAWJQAAFiUBSVIk8AAAAAd0SU1FB+YJHA4NIJ9Iq+YAAByVSURBVHja7Zx5sGXHXd8/3X22u9+3z1vmzbzZNItGq2XLlrwgg1cMKgwkIRASiqoUS1KBqlSokCKuVAiVUCErBFPEpmxsCAYTYoRdtmxLMpJsa5A00uzzZubt+3q3c885veSP+zTWaGak0QYz9vSt+269vuec16/729/+/b6/X7dwzjlulu/ZIm92wU0A3Cw3AXCz3ATAzXITADfL917xboRGuhd+OgdCgrOdz+uoiJsAePMG38R16s99HVObx+vZTm50P165H+HlEFJd5S63hRxHx9O1VxgyAUIgtj5v7KF8jcC93nUABzTPfIvWqccRWITygYxw5BainXegStsQ0t+62OGw4AzOZmAznE3Bpp3fnemwCICQnftkgJDB1qcPUiGQr5phbjLAm4YAhwpChLPIQgEXFZFSojfmiU+vEe19F151BwKHswZnE5xu4nQDl9VwWaPzNnEHCM4AAiF8UCHCyyH9EsIvIfwywivgVB4hfYRQL2KGmzbA3xFHCVS5B+l5CCXBJuAsQoFL67SOfY5o7wfxKkOAxmUb2PYKrr2MTVax8Sq6toJeX8e2m9i2xrYVMh8R9BfxKt2oUg8i6EZGvcioDxn2QFABlQfpdYDwvQoAZzR6YQJM1pkNDmS1D1XuueL1ZnMFW1t92QFFKkSQQ5WqiDD/io1UxW68ah8mXoGgjBIWf/guvGIvyfRfk0x8EdtzCFUqY9MVbHOWdP4sevU86fQZUClOS1zmIaMMU5MkJwOcA39I4/V3E+7ZQ7RzL15lBJkfQuaHkVEfwi+DDLdsjWtgA2twWbvDMn4E8vUbqy6NMasLuCzZWhQFeD6qqx+ZK725NkA2eQJ/+y3wImMrmzqF6hpAlrouHfzVeVAeqtLzCp1kcVmCbdaxcR2MRgQ5vIHRyzrsBQ8gmX2e9tlvQBgilaJw+4/iTIKNV0mmH8a2xnFGYtua+Pg3EXlNNHYLeu1ZXNth0xRVtOg1QTCkyZY84uMBsmxQRYtrC0QkCUZvI3/gTlRlF6q4A1kYRgbdCJV7WRAIIL3wPDJXRvhBp9VZG5cm+KP7X9Pg6IVJXNJCFMqoah/CC17U2RpTW8XW10FIvMExhOe/CQCYOYM/su/Shi1NU/vdf0jXr3wZEUTfuXbuHP7Q7teGcpOh584jvABvcOxSe95ZMCnxma+SrZxEhHn86k5sexUUuKwGTJBMnqT5zGn8bQav9wC24RGfOY0/6BDCgbT4fQavJBDKkswpkgsKvSyROYsIHMJzuLRM6T33E+25Da+0B1kcRYW9oPJXBYEA9Nw43tCeS+rbzzyCSxNyb3v/tfeFzsgmT+KP7EWEuWuyk9JzRwl2Hb5kor65QlC6vkVJl03X10ZFysfffguqexvpuaNgzcWHOqPRjRW8nlGEJ8Auode/jWnN4ZJ1TH2eZGaFdHYZr0fgVQSYGbzuM+QOaPIHFeGYI9ojUaUQWRQ4KVBVQ/EeS/EdKcW3a8JdGhkKzEaLtU89TOPZR9Gbp7CNSWyyhjPtDhhfJbDTZx96FTdYsskTBLsPX9vgv2An9QxR++yvdzSS68oIdA6XxJc0VvjBVZEqwhzB2GHS888R7LoNpER6AbIyTLZh8Xr2ky09ioiSjiaUtWlfeBbXOoHXBSLcQqJqIAsBUZfE6z4MbhXbmsVhkUEOv1uTrVlUyeL3lzGtPLKwgCpnqG6LqQnaR5/ExZbSvRKEj3rBM1DhmyZEZTPj+DsPXZFlbKuObdYRnocsdV1C+UIp9OnPY+q/iCp3Xz8AsPU1Nn7z+75DNkKCX0aN3Etw6AGi2+5HRC8xBKXEH7uV9jNfI7zrvR3DUQj86nZkVATbxGVHEH6TZKpOcv4M5feO4EVNsvVNEA5dcziTIXwJ5hzOthBhiF+w6KZFFas4G4NIEcJgsxquoUCAqlhcIhA+NL7+NKpcoHA4h/DyIEOk9F4iHr2xXo9Qlw6LbbdoPvRxsqN/+B2Ryy8THP4xwrvfj799L86YTnt0ej26gZLCT/5vVKV3i+Usrt3ELM1Q//x/JnrHRwl2HnzJkuDhjR6g/czXie564IWuQHgeweCtxGfGcfUp4tPfJrcfwoEB9OY5ZEngEk04nEcVNBBg26vIKETmCqiCD7KFTVoIsY4I92CbM2Ac4fY8eq1GtizxRyxmDWTZUv/6N/D7+xFBBeGXcCrsgIE31j3UK3OonsHL6ltf+yOyo5/Gv/tnyd3zQWSpgjMGs7FCeuKbtJ/8c2TP6JbL5F2PAACvdwTVM3Bp5a5byd37AdKJk+iFSbxtOy69p2+Y9pN/gd17B7LY1RF6dBO9Nk62Nk5y4SlElOD1eLROPofJNLKoKOzZgUsnEV4R0y4iwi5UsYL0YoQ3jG6cIOipYJzGxkskSylBH0hPg1D4vSE2zcjmNEJCNgv1Jx7H/8EhVpMSSS7AqoRi6NHbVX3jVsu4huwduhwYZx7FP/yTlH7o5y5hHVXtI9h5ANduEh95GDX6ALJYvT4B8HIl2HkAPXcelyaIILz0u8Pvof3UV8h/34/hXIbTTSAjmThBtCtHMHQPZOfJmvPQMBgLuFVkvowQBYwOyeIuzEqNqL8fp4v45WFMcxFnfLxSHq9YJN2I0XWLyyJU1yDxZpuVvT9D+rZDyLDI8pNfYHxikMrheygUClhneOLxR/nQO+8hCgNyUfQG0P+V7QpRGiQ4eN9VlxwRFcjf/8Nw/w/fuEqgNzhGNn36Mp/Z376H5ud+hdw7fwhcAlmd9tQpXLqC3syjKhNgVvGKEhl4BL7CxE3CwtuxySJ+MYcqDCJlL8nCSbxSA6FCrOlFehLnIlS+C989jgx7yDa3oVWFp5OfZddtt5FTksW5Gc527WV9qsah8lkKuRCp2wxV88y2oLWyyVilQdcbYDBfqeTe+9PY9aXvcil4SyG8rNoLkD23kM1PoPq6sLpBcu4ZVNEhZIJtL6CKfUh/AqcFp7+Z0j/qGKikOEKytXn8rn5gjKBP4YzGuRS/shdshrVthHcQ4WUgz1K3vbjCh6kvTHEhaVPKRYxuH2H4vnu5MDGBT0qy2WD//v0sLS+xPHMBayytoI+u12kSqGo/ZmMZVe17CUMeROeKZNNn8Ef2vKEeyPUVCxDiirF+1TeGWZxE9RSwcY1s8Xm8PgHCB6fxSpZsI2J1MWZ6wzK8T2DTJcDDr+wH54PqRsgCJl1DyAQogVvB2SImXiUzCac2/j1dQ3eTz+e5//s1Tzz8EEIXiVvdaK1ZXpwnH0Uoz2N9ZZGsHdNbquCkR6b167YJZamro7K+BAAA3sAozmiy2XGwDm9wJ8IPv7sAIPNlbKuOLFResgb2YldncW4fem0ZPIOqgIgyZOThXBMhU1zg84EfKXZctbAPKOFcBVwBEy8AOUwc41eHsGmG8Heg/BbpylfQ3gAzs3VSOwnWIEzK2I4drK0uY3VKfXOTt7/1rayurVKvNwh8n/X1DXJ5TRTlaNQ2aSMpvt4+KFSw9fXLZPYXPCN/ZB84h16cxLVbeEO7LlFjX71/dj0RQBDg0uSKy4CtLSOswdRr4MBsCFQuQigP6Q8Q9N/C8P49qOIYMtwGogvhD4KsIPO7cEYipEQGZaQfgVA4J7CJwCvdQS5yvH3nX9FqTBJ4GaM7Bxnc3k+QCzh37hxGa+qNGrXaJo1GjUxrSqUCadYmdQ3aukUYBq+7D1TPIGZzGRs3XpYpvW078XcewKzOo+cvfHcA4KpSsnO4tIkDdKOBywDpkGEZWagg/B0Ify/C6waXR3rbESJEyD5k0IUQOfzKKEKF+NXdqNwwDofTnUQRZyUy2kW1lLE//385fuwI87PzrK+uMdDfT7lSplKtAILR7aMMDg7SajUZGBigUa9hjCYz2RuWFOKP7EPPXejQ/ctPGbzBMWRXP9nEiRsfAC5NEOHldObadVA+QgiwDhcLROQR7vx7qKgEIoezFkQRiLBZE6sb2GwdlxhMu4YzOWSQQwY+VmcImSeoVPDyXaj8blTl/aholMG97+a9h4+ysDBJpVKlUq3SP9DPysoKSdImDEN83ydNM4wx+J6PTjMSnb6hymCw+zCu1aTxpU+iV+ZefhCjAt62nSSnj9zYALBxHZm7fBW1tWVkkMcJhQgiZMHhlfPYeBbnXIfSsymcyYA2zqY43UbICPwuhLQ4u4bVDtNqYuNFpKcRwVCHSTwfU/82Np1Drz1Ej/84B8qf5/ixZ7HWUSwVqVQraK1ZWV0hn88ThgH1ep0wjBBOkC/k3/D+CPbeTv6dHyV5+qvU//S3yKbPXJ0LojzCC0jPHr2RlwB3RRfHLo0jKp3cP1WsYppgNi165Qgy2AfePpAWQYZuTiBUiAyqgMO250jXp8g2mshwH6o0ivSroMqkq2cxcYyJF3FmFfQy1qwj8yNsK32TMfFpTp06jhCC7t4e0jQlTVOEkIRhyObmJvlcDp0ZnHBX9eNfn1FYpvC+nyL/Az9Ndv4YtT/+jasyQrDrVuJHP43L0hsUABdDwC/CRNLCLHwL1TMM0sfvHUAGDtOooRuT2PgoNn0OoXIgMwQam8whZA5EFcgRdO3B2TVcegGXzOGcRWAQUuB0immN40wZmxVQURkQyKDMUPl5Bjb/gPFzZ/F9n4HBAeI4ZnNjg0KhgHOQzxfYWFtHSEE7Td+0rlGVHvLv/hFKD/5zsvGjZDNnr6gkyr5dpOefv/EAoJem8fq2X1afTp7e0gJGEDLE7xkGUSIYGcHUwTQ20RtfJ11pY9s1ZNiDsw2sBZu1cDYj21wkqI6CcMigH5Wr4qwEF6PyJWRQQKgFnK3jzCpC9eF0BactO3qOUZn5OJOTE+TyecrVCnE7Jssy8vlcBwy5PMJBZsyb7ylFBXL3fhCsviLjyGI3eu7cjQUAl8S4LEHkCpcD4OhXEVEf3rZRhAyQQYVw7/vI5tfwqoexbR9BQrYxC8rHuRghUzCr2PYqKj+Cs6tAC+GFmPg8NlnAmQ1sOofL5nDWImih8gVgL7p+EtOc6iwl+Qp7Rhex3/hdFhbm6e7pBiHY2NigWCjSbDUJwwjpJEr+7XWnyFew7Su4iiaD9AZaAmxtDb04iT+85wqsMEP2/B/h3/OPECoA6YFfIH/rvWQLMcmFRUwjxsYKr6g7MXFrQChk4MA9jV7/KkHv3fi97we7Ca6B0/Ngp5BBBmYSGRhs0kQWbkOGeXStzNIxg81yGBNhWpI9wxn61J+wtrbKtsEBjDG04haBH6CkIkszpHx9XoDZXNny6V/ZlnBxo5Mb8dJnrExfj0bgls+dpbg0wdTWyGbOkk2fxunsykmT1tD64sdBSKK7v7+TKCEUQhWIRg8hi3eTziyQLddJlwXZssFszmLaG9g0w2aLqJxEBicgewzhRciwDHq2M+t1AyFrIB0uO4/X9U4wPjatIcMuesb6cWmD9tlZkulJ8nvv4dDeCnrtGK04ptrdxdraGsVSCXC06s2Om/q6JsMKqm+YbPIkemnqqkBw7ebFJJlL6rMEc/5hROHaM4XfdClYFCqU/9lfdtC5vghSIaM8/vDulw1qNL/2f9DnHiJ84F+jugcu4lXIABF2Uf6+f8DK7z+DiDqp3rLgqD8tKN0ToXJtbJLiTA2Vi3DZPLbxFKb+BVDbOptBvG6c20DlKpjGJNny57B6BaG6kVEe4Rv0QhspBEZUUMUuMMscHt3Nc5MrlLq2USqXqNVqWGPIB1d2A4Odh5CFCtnUiZedh/7ofnAd1dPfcRCXxGRTpzsJHkbjnEBgwfM6+ZMjey97SnLyCC7dwHsViblvPgCUh9e//dq5Qme0Hv4MyRP/HW/PRzpx7pdEDIVXIL/3TvL3fpTk9J/R+BtL/rAjt88AMXiHILuAy2JcECAk6I1PgF0AKsjoAKb5HDJU2PY8zoZkNQOZxrTnAA+XZZ3dQb5G2Rwum8G11zG1Be664/t5+rlTlKsVFmbnqVaqLK+sXL79EFC9Q6grJHlcMnCnjtB++muovu9cJ8Lcq0ont81N4i/9JrL7Vvwd+/+OloDXw4DOkU6cpPb7v9QZ/Ft+hNKP/yt4Sa67EBIhQ0TQRdcHfgKCWxHWoVccyaRGr2XYxjg2rqFyRVwKQoGQ5Y6MHP812eKnMO3ncS7F6SKYo0ADh+xEDJsWdES2lpFOCmxSBRsi1ADZ0uNgNXff9RY21tbpHehjs7ZJuVyinSSvOQra/utPvQ4BrUH9j38d15gi96Ffuiyn8PUBwF5hHbL2qrP9kgzgazBksrnzxN/6Epv/6+dpfOInsCsnyP3gb1D++79yebLoFsqEUAgvh1ceoe+n/yXOjKLXQAYFsiVF62wdZD/CVwTDv4jwqzi3jswNoRsh2VqKXjekq3lsOsX82ZT1jZg0bROv54lG7kLXujGbEqcOUH7PPwZb6ewuspJsYwEB3POWt9JqNIlyEWmaEqjXFg92aRvXWkV1D5GOH7083f5lbKt04gS1j/88ZvIrRD/wa4T77nx12HuljSG2VSd5/huY1UWQAtduoce/jts4SfVXn7xsa1J69hnaT/3l1enAGFzSwC4/i4tXOtcJiRp5F8GdHyI8dO8lcvBVG+dsJ0Usq5MsnGH5E/8B5Gly+wbQa4v4gxJZMnhFhde9E5v2E586gT/Yj4xAegqnM8KhdxKvPAKtBexGDfwqejElPpsR7b4Tr7qbYPQuVKEbp9cxtRlk+QD5fe9HCIlzjqeOPEWr2STfWOX2XdsRr1IRbB95CLc+QfVffBrb2KTxhd9GDezG33kIr38YERU7s9pZXJZ2vIWZcZJnvoiZfBgR9pD7yL8luu3+V08+17I93DZrtI8+1rE+XwhHDuwkPPjWK16fnj2KXjj/MrKWh/AjZL6ErPbh9QxeZba/gkPkLM5pbNZAb06z/qVPkp56COE5RMHhdUuctfi9JWRBYmoxfl8eZ31svI6MBC6x+H27yZanSKc1Nna4zKCGfpDqez6Cyg/irI/wcqDrtCceweu7i9yOe19EiJYjR57iwvkLfPDOA7hHfh9Xm95Kbrm2dTF8+z8hf/+DF/+v9PxxkucfJXvuTwCN8CrgMly6tiUACWT/3QR3/hDRHe9GFsqvbfW5Ec4H4BVBYHAmxqYb1J9+ks3/90lU/tzWWQESf7CjDQjPIsMcCIGNNcmkxu+3CKUwDTAbEIztp3D3g+R23o6IepF+tTP4QuHSOu3Jb5Hb/QB6axVcWlpifn6eNEl47LHHqNVqlEplvKCTKPqLv/ALdIKYnf9EvlpX0Rr02lJnD2CWdNzhqICq9CBfxQaQ714AvKAzONOJBpomJl6ncewpmt/6MmbpcRACWRLIwCDU1g7zZMsEkhbhS1TvOwgGxwiGx8jtue/iWQFCBhfPCdCb06jSEMeOn+DRRx7BGINzDiEEWmuklKysrNDf30+73SaKIoaGhlhfXyeOYz784Q+zd+/e66p/v0sAcCkbYDOciXEmJltdIJmfIF2axtaXcUkTZx2qWEDkevD7B4mGRvHKvQiV7ySH5LsvGfgX7BmbxQgvYnFhgVqtxqlTp2i324yPjxMEAY1Gg2KxSBzHHDx4EKUU1lruu+8+VldX2b17N9EbkT5+EwCvcIdznU2cF4+KSXFObwVQDBf32AsJwts6GsbvfAp12cC/XFleXqa2ucn6+jpRFBEEAc899xwPPvggQggajQbVavW67d/vQgBc4W7X2U/nLqnfAgFv0CFRW90ohCDLMnzf50Yo8vKAxOqr3mJ8bWJFExs3Lw32LM5u+cEJenkOF7euqC299O3iJq6xecXvLn1vvYRECIW8+PaQwoe4DUnS+f7iC8zyPLbeeb7dWOk8yznM4ix2bblTv7mGWZrtnAjSauCSGCEEZnUB9aKETlvfxKwtv3YIa42tb2JbjY7Wv7HyMt5aHdtqYFavfROJ+tjHPvaxF1c0/uzjeMO7MMvzuCRGFoqkE2dwWYJrx5jVRYRSZFPnkJVuzOI0enm+k6q8NIeqdpNNjneyUoRAz09hG3Wy8WOYhSlkvohZmgOjaX7+t4ne8gDZzAStL36G9re/grfjAC5L0AvTyHwBW1vvdHI73gJJE7OySDY/hQxC9PI8qtJNNn0OszyPLHdhFqbRS/OAwyzPoypdpBNnwXRi6HphGttqkJ58GrO6hD+8E5elZOdPIvIFan/wG/i7DqHKXdQ/+9+I7nwnjS9/Dj03SXL0cUQQET/2EDZu4o/sovGFP0RPnyPYdxub//OXSc8cx995EJkvsvE7v4qNY7xtw+jFWWx9E1XuIps+j91cRXgetrGJnp1EVboxm2vo+SlUtRN2xmQ0/uz30Itz2LhJ/NXPER5+e6etuULnPIELp7Fxk+Tok9iladpHHkEUu1DVHvTiDGZzHeH7ZDPnkcUy4kWC1RU1w2zyLNmF0+jxI4Tv+tEOusMcdmMVb3gHjc/+R9TwftJzJ8hOPE5w+3tonT0KUqFvuYP0+SewGwvk3vdTZGeewyxPEd7zPly7Sf2z/5Xg9vuxtY1Lgya334/XP0T76cdIn/or1PAt6IP3kh1/Etm3HW9wlPYTD0G7QfiOj+CylMbfPIIa2YNdX6b55/+D/If/Ken4cbITTxDcej/xVCfaGNz6NtJjT2JXpsl98Gc6YJw9TXjHuy9KzY2/+AO8sYO0PvWfEBhU+dK8fH3+GNWf+3e4pE3tT38PISR66jT2jndglyewJsPpH8clTdhcQuQ6ukb0rgfJzh0nnb5AevJvwGiybaOY5Vmcsfg79pIcfZzwLQ+QzU9S/8SvoUYOopfehj+0E9XT38mKmj6JvnAUNXQLjb/4ZOeInS8voLaN4Y0doP25/0Lwlg/gjETPnqX9VIhZX6H98GcgzBPceh92c5Vgx75rCwYFh+7BbiyB1shiBRFG2M01/O27iBHIvhG8oVHM3Djhbfd2BHejsa0msjqAGtqFCEL8A28BL+j4rPkCmech8iV4CQD01Bmyc8cJ9t9BFuRRg2N4g9tBa7ILx5H770JW+pA7DiDzJczaEgQhMl/C6QwR5JGFImZ5FlntIzz8VkSUwzZquFYdWe1HbduB8EOCQ/eQYpGVbkR5a8u6TpGFUue8ouo25BYAXFwjmziDrPbRfuZx9PI8/q6D6ImTVH7yl4mPfgsRlXBGk545hqoO4MKtWeYstraOXZ3Fro0icwWc1p0JFRU7UT5rEGEOWSh31D4/h9q2E69vENvcRFa6UUO7EWEOff4Y/u6DpMe/jerehuobwqwuddrtBchqLzKXx7/lrXgjuzp/p9SDN7wHWelGdvdfdgbTZUZgNt2hCZSH2VghGBmjffJZVLGMiPKorl5so0Y2fY5g32HM8gLewBBmc6Nzpl+li3TiNCLM4fVtw2UZttnoPFMKXKuJWV9GVvtwaUywYy+2WSedOocqVfBHxtALM+ilWcIDd+J0hmvHqGoPydljCCnxBkZwOuvYFRurBLccZvN3/g3Ruz9KuP829MIMqm8Q2+gcQKW6ekjPn0Lking9/ThrsPUaMl9A+EFnv327RXL6efyxfdiNNfzRTkg1GT+BkAp/+xjJiacRUZ5w32Gy2Qn84Z1kMxc6QLUGvbKES9sd9vC8DtVPnsW2WzhjMTPj+LsOEuw5SHL2+NYWr+3YZg2zPE944A7M2gp6cYbwwJ0XD5sy66sgZWdJLlZAQHrmefztuxG5POnZ48hCCdXVC0p1+jvKIaI8enEG147xt+/CZWnnmhvJC7hWa18vzOBt237dttA2aiB4zZLt96wbeLP8LbuBN8v3Vvn/0OEfV4iL9D4AAAAASUVORK5CYII='


def parse_args():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('beamformed_dataset',
                        help='Input BeamFormed dataproduct')
    parser.add_argument('output_directory', help='output directory')

    # time and frequency compression ratio
    parser.add_argument(
        '--t_c_ratio', help='compression ratio of the time', type=int, default=24)
    parser.add_argument(
        '--f_c_ratio', help='compression ratio of the frequency', type=int, default=8)

    # flip the frequency axis
    parser.add_argument('--flip_freq', help='flip the frequency axis (set to upper start)', default=False,
                        action='store_true')

    parser.add_argument('--minutes_per_chunk',
                        help='time chunks in minutes', type=int, default=15)
    parser.add_argument(
        '--num_chunks', help='number of output chunks, -1 means to the end', type=int, default=-1)
    parser.add_argument('--chop_off', help='chop every **interger** 15 minutes [00:15,00:30,00:45....], default True',
                        action='store_false')
    parser.add_argument('--averaging', help='use averaging to downsize, otherwise use sampling', default=True,
                        action='store_true')
    parser.add_argument('--flagging', help='flag data before averaging', default=False,
                        action='store_true')
    parser.add_argument('--t_idx_cut', help='length of t-index for convolution, \
        8192 means about 195MB for 6400 channels', type=int, default=256)

    # file names and directory
    parser.add_argument('--target_directory', help='use long directory name, (e.g. out/sun/xxx.fits)',
                        default=False, action='store_true')
    parser.add_argument('--date_directory', help='use long directory name, (e.g. out/2020/12/12/xxx.fits)',
                        default=False, action='store_true')
    parser.add_argument('--simple_fname', help='use simple file name, for daily summary, format YYYYMMDD_hh (e.g. 20201212_02.fits)',
                        default=False, action='store_true')
    parser.add_argument('--add_ksp_logo', help='showing ksp logo',
                        default=False, action='store_true')
    parser.add_argument('--add_idols_logo', help='showing idols logo',
                        default=False, action='store_true')

    return parser.parse_args()


def compress_h5(fname_DS,
                out_dir,
                t_c_ratio,
                t_idx_cut,
                f_c_ratio,
                minutes_per_chunk,
                num_chunks,
                chop_off,
                averaging,
                flagging,
                target_directory,
                date_directory,
                simple_fname,
                add_ksp_logo,
                add_idols_logo,
                flip_freq):
    """
    fname_DS: relative (or absolute) directory+fname to the .h5
    out_dir: relative (or absolute) directory+fname to the .h5
    """
    minutes_per_chunk = datetime.timedelta(minutes=minutes_per_chunk)
    h5_absolute = os.path.abspath(fname_DS)
    h5_dir = os.path.dirname(h5_absolute)
    h5_fname = os.path.basename(h5_absolute)
    out_dir = os.path.abspath(out_dir)
    os.chdir(h5_dir)
    f = h5py.File(h5_fname, 'r')

    (dataset_uri, coordinates_uri, beam_key, stokes_key, pointing_ra, pointing_dec, tsamp, 
        project_id, obs_id, antenna_set_name, telescop_name, target_name, t_idx_count, f_idx_count,
        t_start_bf, t_end_bf, freq, t_all)= bftools.h5_fetch_meta(f)

    print('Beam:', beam_key)
    print('Stokes:', stokes_key)
    print('data shape [t,f]:', t_idx_count, f_idx_count)
    
    if chop_off:
        t_start_chunk = t_start_bf.replace(minute=int(np.ceil(t_start_bf.minute / 15.0) * 15),
                                           second=0, microsecond=0)
    else:
        t_start_chunk = t_start_bf

    if num_chunks == -1:
        chunk_num = int(
            np.max([np.floor((t_end_bf - t_start_chunk) / minutes_per_chunk), 1]))
    else:
        chunk_num = num_chunks

    f_fits = bftools.avg_1d(freq, f_c_ratio)
    os.makedirs(out_dir, exist_ok=True)

    net = RFIconv(device=device)
    agg_factor = [1.66, 1.66, 0.45, 0.45]

    start_time = time.time()
    for idx_cur in range(chunk_num):
        # select the time
        t_start_fits = t_start_chunk + idx_cur * 1.0 * minutes_per_chunk
        t_end_fits = np.min(
            [t_end_bf - datetime.timedelta(seconds=10), t_start_chunk + (idx_cur + 1) * 1.0 * minutes_per_chunk])

        t_ratio_start = (mdates.date2num(t_start_fits)
                         - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                           - mdates.date2num(t_start_bf))
        t_ratio_end = (mdates.date2num(t_end_fits)
                       - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                         - mdates.date2num(t_start_bf))

        print('processing chunk', idx_cur + 1, 'of', chunk_num,
              ', ratio range:', t_ratio_start, t_ratio_end)

        # get pointing x y according to starting time
        pointing_x, pointing_y = j2000xy(
            pointing_ra, pointing_dec, t_start_fits)

        # downsample by time ratio
        data_fits, t_fits = bftools.downsample_h5_seg_by_time_ratio(
            f[dataset_uri], t_all, t_ratio_start, t_ratio_end, t_idx_count,
            t_c_ratio, f_c_ratio, averaging, flagging, t_idx_cut, agg_factor, device)

        # t_fits = np.linspace(mdates.date2num(t_start_fits), mdates.date2num(t_end_fits), data_fits.shape[0])
        full_hdu = bftools.cook_fits_spectr_hdu(data_fits, t_fits, f_fits, t_start_fits, t_end_fits, stokes_key,
                                 antenna_set_name, telescop_name, target_name,
                                 pointing_ra, pointing_dec, pointing_x, pointing_y)

        fname = t_start_fits.strftime(
            r"LOFAR_%Y%m%d_%H%M%S_") + antenna_set_name+"_S"+stokes_key.strip()[-1]  # + '.fits'

        obj_name = "sun" if ('sun' in target_name) else "nts"

        real_out_dir = out_dir
        if target_directory:
            real_out_dir = os.path.join(out_dir, obj_name)
        if date_directory:
            real_out_dir = os.path.join(
                real_out_dir, t_start_fits.strftime(r"%Y/%m/%d"))

        os.makedirs(real_out_dir, exist_ok=True)
        if simple_fname:
            fname = t_start_fits.strftime(
                r"%Y%m%d_%H")+"_S"+stokes_key.strip()[-1]  # + '.fits'

        out_path_fits = os.path.join(real_out_dir, fname + '.fits')
        out_path_png = os.path.join(real_out_dir, fname + '.png')
        out_path_json = os.path.join(real_out_dir, fname + '.json')

        full_hdu.writeto(out_path_fits, overwrite=True)
        fig = plt.figure(figsize=(7, 4.5), dpi=160)

        main_width, main_height = 0.81, 0.81
        ax = fig.add_axes([0.08, 0.105, main_width, main_height])

        if ('0' not in stokes_key.lower()):  # QUV
            cmap = "bwr"
            data_fits_new = (data_fits)/np.nanmax(np.abs(data_fits))
            # scale vmax and vmin
            freq_safe0, freq_safe1 = int(
                0.27 * f_fits.shape[0]), int(0.99 * f_fits.shape[0])
            data_safe_arr = data_fits_new[:, freq_safe0:freq_safe1].ravel()
            data_safe = np.sort(data_safe_arr)[int(
                data_safe_arr.shape[0] * 0.02):int(data_safe_arr.shape[0] * 0.98)]
            vmin, vmax = [-0.9*np.nanmax(data_safe), 0.9*np.nanmax(data_safe)]

        else: # stokes I
            cmap = "inferno"
            data_fits_new = (data_fits / np.nanmean(
                np.sort(data_fits, 0)[
                    int(data_fits.shape[0] * 0.1):int(data_fits.shape[0] * 0.3), :], 0))-1
            # scale vmax and vmin
            freq_safe0, freq_safe1 = int(
                0.27 * f_fits.shape[0]), int(0.99 * f_fits.shape[0])
            data_safe_arr = data_fits_new[:, freq_safe0:freq_safe1].ravel()
            data_safe = np.sort(data_safe_arr)[int(
                data_safe_arr.shape[0] * 0.02):int(data_safe_arr.shape[0] * 0.98)]
            vmin, vmax = [(np.nanmean(data_safe) - 2 * np.nanstd(data_safe)),
                          (np.nanmean(data_safe) + 2 * np.nanstd(data_safe)+0.9*np.nanmax(data_safe))]

        freq_origin = 'upper' if flip_freq else 'lower'
        freq_range = [f_fits[-1],f_fits[0]] if flip_freq else [f_fits[0],f_fits[-1]]
        im = ax.imshow(data_fits_new.T, aspect='auto', origin=freq_origin, vmax=vmax, vmin=vmin,
                        extent=[mdates.date2num(t_start_fits), mdates.date2num(t_end_fits), 
                        freq_range[0],freq_range[1]], cmap=cmap)

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_xlabel('Time (UT)')
        ax.set_ylabel('Frequency (MHz)')
        ax.set_title(t_start_fits.strftime("%Y/%m/%d") + ' LOFAR ' +
                     antenna_set_name + ' ' + stokes_key)

        if add_idols_logo:
            ax_logo1 = fig.add_axes([0.08, 0.92, 0.12, 0.07])
            img1 = mpimg.imread(io.BytesIO(base64.b64decode(idols_logo_base64)), format='png')
            ax_logo1.imshow(img1)
            ax_logo1.axis('off')

        if add_ksp_logo:
            ax_logo2 = fig.add_axes([0.01, 0.915, 0.07, 0.08])
            img2 = mpimg.imread(io.BytesIO(base64.b64decode(lofar_logo_base64)), format='png')
            ax_logo2.imshow(img2)
            ax_logo2.axis('off')

        # add colorbar
        ax_cbar = fig.add_axes([0.895, 0.105, 0.03, main_height])
        cbar = plt.colorbar(im, cax=ax_cbar, orientation='vertical')
        cbar.formatter.set_powerlimits((0, 0))
        ax_cbar.text(0.4, 0.5, r'$\rm (I-I_{B0})/I_{B0}$', color='w', ha='center', va='center', rotation=270,
                     transform=ax_cbar.transAxes, fontsize=12)

        fig.savefig(out_path_png)
        plt.close('all')

        lofar_json_dict = {'telescope': telescop_name, 'instrume': antenna_set_name,
                           'projectID': project_id, 'obsID': obs_id,
                           'source': fname_DS, 'date': t_start_fits.strftime("%Y-%m-%d"),
                           'ra': pointing_ra, 'dec': pointing_dec,
                           'x': pointing_x,   'y': pointing_y,
                           'time': t_start_fits.strftime("%H:%M:%S.%f"),
                           'event': {"no_detection": True, "type": "none", "level": "none"}, 'n_freq': len(f_fits),
                           'n_time': len(t_fits), 'freq_range': [np.nanmin(f_fits), np.nanmax(f_fits)],
                           'time_range': [t_start_fits.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                          t_end_fits.strftime("%Y-%m-%d %H:%M:%S.%f")]}

        with open(out_path_json, 'w') as fp:
            json.dump(lofar_json_dict, fp)

        gc.collect()

    print("--- %s seconds ---" % (time.time() - start_time))


def main():
    args = parse_args()
    compress_h5(args.beamformed_dataset,
                args.output_directory,
                args.t_c_ratio,
                args.t_idx_cut,
                args.f_c_ratio,
                args.minutes_per_chunk,
                args.num_chunks,
                args.chop_off,
                args.averaging,
                args.flagging,
                args.target_directory,
                args.date_directory,
                args.simple_fname,
                args.add_ksp_logo,
                args.add_idols_logo,
                args.flip_freq)


#if __name__ == '__main__':
#    main()
