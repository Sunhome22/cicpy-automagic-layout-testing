#*
# A test on how the mag function in cicpy can be used to convert .sch to .mag
#*

import cicpy.cic as cic

if __name__ == '__main__':
    cic.mag(ctx=None, lib="design/jnw_bkle_sky130a", libdir="../jnw_bkle_sky130a/", cell="jnw_bkle")
