#usr/bin/python

#gives the aziumuth and elevation for galactic coordinates
#position is the MIT radome
from astropy.utils import iers
iers.conf.iers_auto_url = "ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all"
#"https://datacenter.iers.org/data/9/finals2000A.all"
from astropy.coordinates import SkyCoord
from astropy.coordinates import ICRS
from astropy.coordinates import GCRS
from astropy.coordinates import Galactic
from astropy.coordinates import Galactocentric
from astropy import units as u
from astropy.constants import c
from astropy.time import Time
from astroplan import Observer
#from astroplan import FixedTarget
#Mars = FixedTarget.from_name("mars")

#observer-specific coordinates
mitlat=42.3601*u.degree
mitlong=-71.0942*u.degree
radome_elevation=100*u.m #roughly 100m above sea level
time = Time.now()
#print time
#time =Time('2018-08-22 15:31:06')

#define an observer and an altaz frame
radome_observer=Observer(latitude=mitlat,longitude=mitlong, elevation=radome_elevation, name='radome', timezone='US/Eastern')
altaz_frame=radome_observer.altaz(time)
icrs_frame=ICRS()
galactic_frame=Galactic()

#print radome_observer.sun_altaz(time)

#convert frequencies fs to radial velocity in km/s at galactic coordinate l
#account for movement of the earth relative to the sun and the sun relative to galactic center
def freqs_to_vel(center_freq, fs, lcoord,bcoord):
    # Convert from earth reference frame to solar reference frame using
    # https://docs.astropy.org/en/stable/coordinates/velocities.html#radial-velocity-corrections
    # Then convert from solar reference frame to Galactic Standard of Rest using
    # https://docs.astropy.org/en/stable/generated/examples/coordinates/rv-to-gsr.html
    pos_gal = SkyCoord(l=lcoord*u.degree, b=bcoord*u.degree, frame='galactic')
    v_to_bary = pos_gal.radial_velocity_correction(kind='barycentric', obstime=get_time(), location=radome_observer.location)
    # Calculate the sun's velocity projected in the observing direction.
    v_sun = Galactocentric().galcen_v_sun.to_cartesian()
    cart_data = pos_gal.data.to_cartesian()
    unit_vector = cart_data / cart_data.norm()
    v_proj = v_sun.dot(unit_vector)

    def freq_to_vel(f):
        f = f * u.MHz
        v_local = f.to(u.km/u.s, u.doppler_radio(center_freq*u.MHz))
        v_bary = v_local + v_to_bary + v_local * v_to_bary / c
        # v_bary is now barycentric; now we need to remove the solar system motion as well
        return (v_bary + v_proj) / (u.km/u.s)
    return [freq_to_vel(f) for f in fs]

def update_altaz():
    time=Time.now()
    altaz_frame=radome_observer.altaz(time)
    return altaz_frame

def get_time():
    time=Time.now()
    return time

def gcrs_to_altaz(ra,dec):
    altaz_frame=update_altaz()
    gcrs_frame=update_GCRS()
    pos_gcrs=SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame=gcrs_frame)
    pos_altaz=pos_gcrs.transform_to(altaz_frame)
    return (pos_altaz.az.degree, pos_altaz.alt.degree)

def gal_to_altaz(lcoord,bcoord): #galactic coords in degrees
    altaz_frame=update_altaz()
    #define a galactic position
    pos_gal=SkyCoord(l=lcoord*u.degree, b=bcoord*u.degree, frame='galactic')
    #transform the galactic position to an altaz one
    pos_altaz=pos_gal.transform_to(altaz_frame)
    #print(pos_altaz.to_string())
    return (pos_altaz.az.degree, pos_altaz.alt.degree)

def radec_to_altaz(ra,dec):
    altaz_frame=update_altaz()
    pos_icrs=SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame=icrs_frame)
    pos_altaz=pos_icrs.transform_to(altaz_frame)
    return (pos_altaz.az.degree, pos_altaz.alt.degree)

def altaz_to_radec(az,el):
    altaz_frame=update_altaz() #so that our reported times are accurate
    #define the position
    pos_altaz=SkyCoord(az=az*u.degree, alt=el*u.degree, frame=altaz_frame)
    #transform to RA DEC
    pos_icrs=pos_altaz.transform_to(icrs_frame)
    return(pos_icrs.ra.degree, pos_icrs.dec.degree)


def altaz_to_gal(az, el):
    altaz_frame=update_altaz()
    pos_altaz=SkyCoord(az=az*u.degree, alt=el*u.degree, frame=altaz_frame)
    pos_gal=pos_altaz.transform_to(galactic_frame)
    return (pos_gal.l.degree, pos_gal.b.degree)


def get_sun_altaz():
    time=Time.now()    #print time
    pos=radome_observer.sun_altaz(time)
    return (pos.az.degree, pos.alt.degree)

def get_moon_altaz():
    time=Time.now()    #print time
    pos=radome_observer.moon_altaz(time)
    return (pos.az.degree, pos.alt.degree)

#def get_mars_altaz():
#    time=Time.now()    #print time
#    pos=radome_observer.altaz(time,Target=Mars)
 #   return (pos.az.degree, pos.alt.degree)
