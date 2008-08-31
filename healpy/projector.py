"""This module provides classes for some spherical projection.
To be used when calling SphereProjAxes class.

SphericalProj : a virtual class (do nothing). Just a template for derived 
                (useful) classes

GnomonicProj : Gnomonic projection
"""

import rotator as R
import numpy as npy

pi = npy.pi
dtor = npy.pi/180.

class SphericalProj(object):
    """
    This class defines functions for spherical projection.
    
    This class contains class method for spherical projection computation. It 
    should not be instanciated. It should be inherited from and methods should
    be overloaded for desirated projection.
    """

    name = "None"
    
    def __init__(self, rot=None, coord=None, flipconv=None, **kwds):
        self.rotator  = R.Rotator(rot=rot,  coord=None, eulertype='ZYX')
        self.coordsys = R.Rotator(coord=coord).coordout
        self.coordsysstr = R.Rotator(coord=coord).coordoutstr
        self.set_flip(flipconv)
        self.set_proj_plane_info(**kwds)

    def set_proj_plane_info(self, **kwds):
        allNone = True
        for v in kwds.values():
            if v is not None: allNone = False
        if not allNone:
            self._arrayinfo = dict(kwds)
        else:
            self._arrayinfo = None

    def get_proj_plane_info(self):
        return self._arrayinfo
    arrayinfo = property(get_proj_plane_info,
                         doc="Dictionary with information on the projection array")

    def __eq__(self, a):
        if type(a) is not type(self): return False
        return ( (self.rotator == a.rotator) and
                 (self.coordsys == a.coordsys ) )
    
    def ang2xy(self, theta, phi=None, lonlat=False, direct=False):
        """From angular direction to position in the projection plane (%s).

        Input:
          - theta: if phi is None, theta[0] contains theta, theta[1] contains phi
          - phi  : if phi is not None, theta,phi are direction
          - lonlat: if True, angle are assumed in degree, and longitude, latitude
          - flipconv is either 'astro' or 'geo'. None will be default.
        Return:
          - x, y: position in %s plane.
        """
        pass
    
    def vec2xy(self, vx, vy=None, vz=None, direct=False):
        """From unit vector direction to position in the projection plane (%s).

        Input:
          - vx: if vy and vz are None, vx[0],vx[1],vx[2] defines the unit vector.
          - vy,vz: if defined, vx,vy,vz define the unit vector
          - lonlat: if True, angle are assumed in degree, and longitude, latitude
          - flipconv is either 'astro' or 'geo'. None will be default.

        Return:
          - x, y: position in %s plane.
        """
        pass
    
    def xy2ang(self, x, y=None, lonlat=False, direct=False):
        """From position in the projection plane to angular direction (%s).

        Input:
          - x : if y is None, x[0], x[1] define the position in %s plane.
          - y : if defined, x,y define the position in projection plane.
          - lonlat: if True, angle are assumed in degree, and longitude, latitude
          - flipconv is either 'astro' or 'geo'. None will be default.

        Return:
          - theta, phi : angular direction.
        """
        pass

    def xy2vec(self, x, y=None, direct=False):
        """From position in the projection plane to unit vector direction (%s).

        Input:
          - x : if y is None, x[0], x[1] define the position in %s plane.
          - y : if defined, x,y define the position in projection plane.
          - lonlat: if True, angle are assumed in degree, and longitude, latitude
          - flipconv is either 'astro' or 'geo'. None will be default.

        Return:
          - theta, phi : angular direction.
        """
        pass
    
    def xy2ij(self, x, y=None):
        """From position in the projection plane to image array index (%s).

        Input:
          - x : if y is None, x[0], x[1] define the position in %s plane.
          - y : if defined, x,y define the position in projection plane.
          - projinfo : additional projection information.

        Return:
          - i,j : image array indices.
        """
        pass
    
    def ij2xy(self, i=None, j=None):
        """From image array indices to position in projection plane (%s).

        Input:
          - if i and j are None, generate arrays of i and j as input
          - i : if j is None, i[0], j[1] define array indices in %s image.
          - j : if defined, i,j define array indices in image.
          - projinfo : additional projection information.

        Return:
          - x,y : position in projection plane.
        """
        pass

    def projmap(self, map, vec2pix_func,rot=None,coord=None):
        """Create an array containing the projection of the map.

        Input:
          - vec2pix_func: a function taking theta,phi and returning pixel number
          - map: an array containing the spherical map to project,
                 the pixellisation is described by ang2pix_func
        Return:
          - a 2D array with the projection of the map.

        Note: the Projector must contain information on the array.
        """
        x,y = self.ij2xy()
        if npy.__version__ >= '1.1':
            if ( type(x) is npy.ma.core.MaskedArray
                 and x.mask is not npy.ma.nomask ):
                w = (x.mask == False)
            else:
                w = slice(None)
        else:
            if type(x) is npy.ma.array and x.mask is not npy.ma.nomask:
                w = (x.mask == False)
            else:
                w = slice(None)
        img=npy.zeros(x.shape,npy.float64)-npy.inf
        vec = self.xy2vec(npy.asarray(x[w]),npy.asarray(y[w]))
        vec = (R.Rotator(rot=rot,coord=self.mkcoord(coord))).I(vec)
        pix=vec2pix_func(vec[0],vec[1],vec[2])
        img[w] = map[pix]
        return img
        
    def set_flip(self, flipconv):
        """flipconv is either 'astro' or 'geo'. None will be default.
        
        With 'astro', east if is toward left and west toward right. 
        It is the opposite for 'geo'
        """
        if flipconv is None:
            flipconv = 'astro'  # default
        if    flipconv == 'astro': self._flip = -1
        elif  flipconv == 'geo':   self._flip = 1
        else: raise ValueError("flipconv must be 'astro', 'geo' or None for default.")
        
    def get_extent(self):
        """Get the extension of the projection plane.

        Return:
          extent = (left,right,bottom,top)
        """
        pass

    def get_fov(self):
        """Get the field of view in degree of the plane of projection

        Return:
          fov: the diameter in radian of the field of view
        """
        return 2.*pi

    def get_center(self,lonlat=False):
        """Get the center of the projection.

        Input:
          - lonlat : if True, will return longitude and latitude in degree,
                     otherwise, theta and phi in radian
        Return:
          - theta,phi or lonlat depending on lonlat keyword
        """
        lon, lat = npy.asarray(self.rotator.rots[0][0:2])*180/pi
        if lonlat: return lon,lat
        else: return pi/2.-lat*dtor, lon*dtor

    def mkcoord(self,coord):
        if self.coordsys is None:
            return (coord,coord)
        elif coord is None:
            return (self.coordsys,self.coordsys)
        elif type(coord) is str:
            return (coord,self.coordsys)
        else:
            return (tuple(coord)[0],self.coordsys)
        
            
class GnomonicProj(SphericalProj):
    """This class provides class methods for Gnomonic projection.
    """
    
    name = "Gnomonic"

    def __init__(self, rot=None, coord=None, xsize=None, ysize=None, reso=None,
                 **kwds):
        super(GnomonicProj,self).__init__(rot=rot, coord=coord,
                                          xsize=xsize, ysize=ysize,reso=reso,
                                          **kwds)

    def set_proj_plane_info(self, xsize=200,ysize=None,reso=1.5):
        if xsize is None: xsize=200
        if ysize is None: ysize=xsize
        if reso is None: reso=1.5
        super(GnomonicProj,self).set_proj_plane_info(xsize=xsize,
                                                     ysize=ysize,reso=reso)
    
    def vec2xy(self, vx, vy=None, vz=None, direct=False):
        if not direct: vec = self.rotator(vx,vy,vz)
        elif vy is None and vz is None: vec=vx
        elif vy is not None and vz is not None: vec=vx,vy,vz
        else: raise ValueError("vy and vz must be both defined or both not defined")
        flip = self._flip
        mask = (npy.asarray(vec[0])<=0.)
        w = npy.where(mask == False)
        if not mask.any(): mask=npy.ma.nomask
        if not hasattr(vec[0],'__len__'):
            if mask is not npy.ma.nomask:
                x = npy.nan
                y = npy.nan
            else:
                x = flip*vec[1]/vec[0]
                y = vec[2]/vec[0]
        else:
            x = npy.zeros(vec[0].shape)+npy.nan
            y = npy.zeros(vec[0].shape)+npy.nan
            x[w] = flip*vec[1][w]/vec[0][w]
            y[w] = vec[2][w]/vec[0][w]
        return x,y
    vec2xy.__doc__ = SphericalProj.ang2xy.__doc__ % (name,name)

    def xy2vec(self, x, y=None, direct=False):
        flip = self._flip
        if y is None:
            x,y = x
        x,y=npy.asarray(x),npy.asarray(y)
        rm1=1./npy.sqrt(1.+x**2+y**2)
        vec = (rm1,flip*rm1*x,rm1*y)
        if not direct:
            return self.rotator.I(vec)
        else:
            return vec
    xy2vec.__doc__ = SphericalProj.xy2vec.__doc__ % (name,name)

    def ang2xy(self, theta, phi=None, lonlat=False, direct=False):
        vec=R.dir2vec(theta,phi,lonlat=lonlat)
        return self.vec2xy(vec,direct=direct)
    ang2xy.__doc__ = SphericalProj.ang2xy.__doc__ % (name,name)
    
    def xy2ang(self, x, y=None, lonlat=False, direct=False):
        return R.vec2dir(self.xy2vec(x,y,direct=direct),lonlat=lonlat)
    xy2ang.__doc__ = SphericalProj.xy2ang.__doc__ % (name,name)


    def xy2ij(self, x, y=None):
        if self.arrayinfo is None:
            raise TypeError("No projection plane array information defined for "
                            "this projector")
        xsize,ysize = self.arrayinfo['xsize'],self.arrayinfo['ysize']
        reso = self.arrayinfo['reso']
        if y is None: x,y = x
        dx = reso/60. * dtor
        xc,yc = 0.5*(xsize-1), 0.5*(ysize-1)
        j = npy.around(xc+x/dx).astype(long)
        i = npy.around(yc-y/dx).astype(long)
        return i,j
    xy2ij.__doc__ = SphericalProj.xy2ij.__doc__ % (name,name)

    def ij2xy(self, i=None, j=None):
        if self.arrayinfo is None:
            raise TypeError("No projection plane array information defined for "
                            "this projector")
        xsize,ysize = self.arrayinfo['xsize'],self.arrayinfo['ysize']
        reso = self.arrayinfo['reso']
        dx = reso/60. * dtor
        xc,yc = 0.5*(xsize-1), 0.5*(ysize-1)
        if i is None and j is None:
            idx=npy.outer(npy.ones(xsize),npy.arange(ysize))
            x=(idx-xc) * dx   # astro= '-' sign, geo '+' sign
            idx=npy.outer(npy.arange(xsize),npy.ones(ysize))
            y=(yc-idx)*dx #(idx-yc) * dx
        elif i is not None and j is not None:
            x=(npy.asarray(j)-xc) * dx
            y=(yc-npy.asarray(i)) * dx #(asarray(i)-yc) * dx
        elif i is not None and j is None:
            i, j = i
            x=(npy.asarray(j)-xc) * dx
            y=(yc-npy.asarray(i)) * dx #(i-yc) * dx
        else:
            raise TypeError("Wrong parameters")
        return x,y
    ij2xy.__doc__ = SphericalProj.ij2xy.__doc__ % (name,name)

    def get_extent(self):
        xsize,ysize = self.arrayinfo['xsize'],self.arrayinfo['ysize']
        left,top = self.ij2xy(0,0)
        right,bottom = self.ij2xy(xsize-1,ysize-1)
        return (left,right,bottom,top)

    def get_fov(self):
        vx,vy,vz = self.xy2vec(self.ij2xy(0,0), direct=True)
        a = npy.arccos(vx)
        return 2.*a

class MollweideProj(SphericalProj):
    """This class provides class methods for Mollweide projection.
    """
    
    name = "Mollweide"
    __molldata = []

    def __init__(self, rot=None, coord=None, xsize=800, **kwds):
        self.__initialise_data()
        super(MollweideProj,self).__init__(rot=rot, coord=coord,
                                           xsize=xsize, **kwds)
        
    def set_proj_plane_info(self,xsize):
        super(MollweideProj,self).set_proj_plane_info(xsize=xsize)

    def vec2xy(self, vx, vy=None, vz=None, direct=False):
        if not direct:
            theta,phi=R.vec2dir(self.rotator(vx,vy,vz))
        else:
            theta,phi=R.vec2dir(vx,vy,vz)
        flip = self._flip
        X,Y = MollweideProj.__molldata
        # set phi in [-pi,pi]
        phi = (phi+pi)%(2*pi)-pi
        lat = pi/2. - theta
        A = MollweideProj.__lininterp(X,Y,lat)
        x = flip*2./pi * phi * npy.cos(A)
        y = npy.sin(A)
        return x,y
    vec2xy.__doc__ = SphericalProj.vec2xy.__doc__ % (name,name)

    def xy2vec(self, x, y=None, direct=False):
        flip = self._flip
        if y is None: x,y = x
        mask = (npy.asarray(x)**2/4.+npy.asarray(y)**2 > 1.)
        w=npy.where(mask == False)
        if not mask.any(): mask = npy.ma.nomask
        if not hasattr(x,'__len__'):
            if mask is not npy.ma.nomask:
                return npy.nan,npy.nan,npy.nan
            else:
                s = npy.sqrt((1-y)*(1+y))
                a = npy.arcsin(y)
                z = 2./pi * (a + y*s)
                phi = flip * pi/2. * x/npy.maximum(s,1.e-6)
                sz = npy.sqrt((1-z)*(1+z))
                vec = sz*npy.cos(phi),sz*npy.sin(phi),z
                if not direct:
                    return self.rotator.I(vec)
                else:
                    return vec
        else:
            vec = (npy.zeros(x.shape)+npy.nan,
                   npy.zeros(x.shape)+npy.nan,
                   npy.zeros(x.shape)+npy.nan)
            s = npy.sqrt((1-y[w])*(1+y[w]))
            a = npy.arcsin(y[w])
            vec[2][w] = 2./pi * (a + y[w]*s)
            phi = flip * pi/2. * x[w]/npy.maximum(s,1.e-6)
            sz = npy.sqrt((1-vec[2][w])*(1+vec[2][w]))
            vec[0][w] = sz*npy.cos(phi)
            vec[1][w] = sz*npy.sin(phi)
            if not direct:
                return self.rotator.I(vec)
            else:
                return vec
    xy2vec.__doc__ = SphericalProj.xy2vec.__doc__ % (name,name)

    def ang2xy(self, theta, phi=None, lonlat=False, direct=False):
        return self.vec2xy(R.dir2vec(theta,phi,lonlat=lonlat),direct=direct)
    ang2xy.__doc__ = SphericalProj.ang2xy.__doc__ % (name,name)
    
    def xy2ang(self, x, y=None, lonlat=False, direct=False):
        vec = self.xy2vec(x,y,direct=direct)
        return R.vec2dir(vec,lonlat=lonlat)
    xy2ang.__doc__ = SphericalProj.xy2ang.__doc__ % (name,name)


    def xy2ij(self, x, y=None):
        if self.arrayinfo is None:
            raise TypeError("No projection plane array information defined for "
                            "this projector")
        xsize = self.arrayinfo['xsize']
        ysize=xsize/2
        if y is None: x,y = x
        xc,yc = (xsize-1.)/2., (ysize-1.)/2.
        if hasattr(x,'__len__'):
            j = long(npy.around(x*xc/2.+xc))
            i = long(npy.around(yc-y*yc))
            mask = (x**2/4.+y**2>1.)
            if not mask.any(): mask=npy.ma.nomask
            j=npy.ma.array(j,mask=mask)
            i=npy.ma.array(i,mask=mask)
        else:
            if x**2/4.+y**2 > 1.:
                i,j=npy.nan,npy.nan
            else:
                j = npy.around(x*xc/2.+xc).astype(long)
                i = npy.around(yc-y*yc).astype(long)
        return i,j
    xy2ij.__doc__ = SphericalProj.xy2ij.__doc__ % (name,name)

    def ij2xy(self, i=None, j=None):
        if self.arrayinfo is None:
            raise TypeError("No projection plane array information defined for "
                            "this projector")
        xsize = self.arrayinfo['xsize']
        ysize=xsize/2
        xc,yc=(xsize-1.)/2.,(ysize-1.)/2.
        if i is None and j is None:
            idx = npy.outer(npy.arange(ysize),npy.ones(xsize))
            y = (yc-idx)/yc
            idx = npy.outer(npy.ones(ysize),npy.arange(xsize))
            x = 2.*(idx-xc)/xc
            mask = x**2/4.+y**2 > 1.
            if not mask.any(): mask=npy.ma.nomask
            x = npy.ma.array(x,mask=mask)
            y = npy.ma.array(y,mask=mask)
        elif i is not None and j is not None:
            y = (yc-npy.asarray(i))/yc
            x=2.*(npy.asarray(j)-xc)/xc
            if x**2/4.+y**2 > 1.: x,y=npy.nan,npy.nan
        elif i is not None and j is None:
            i,j = i
            y=(yc-npy.asarray(i))/yc
            x=2.*(npy.asarray(j)-xc)/xc
            if x**2/4.+y**2 > 1.: x,y=npy.nan,npy.nan
        else:
            raise TypeError("i and j must be both given or both not given")
        return x,y
    ij2xy.__doc__ = SphericalProj.ij2xy.__doc__ % (name,name)

    def get_extent(self):
        return (-2.0,2.0,-1.0,1.0)

    @staticmethod
    def __initialise_data():
        if len(MollweideProj.__molldata) == 0:
            X = (npy.arange(1.,180.,1.)-90.)*dtor
            Y = MollweideProj.__findRoot(MollweideProj.__fmoll,
                                         MollweideProj.__dfmoll,
                                         X.copy(),X,niter=10)
            X = npy.concatenate([-pi/2,X,pi/2],None)
            Y = npy.concatenate([-pi/2,Y,pi/2],None)
            MollweideProj.__molldata.append( X )
            MollweideProj.__molldata.append( Y )
        return

    @staticmethod
    def __findRoot(f, df, x0, argsf=None, argsdf=None, niter=100):
        x = x0
        niter = min(abs(niter),1000)
        i = 0
        while i < niter:
            dx = -f(x,argsf)/df(x,argsdf)
            x += dx
            i += 1
        return x

    @staticmethod
    def __fmoll(x,args):
        return 2.*x+npy.sin(2.*x)-pi*npy.sin(args)

    @staticmethod
    def __dfmoll(x,args):
        return 2.*(1.+npy.cos(2.*x))

    @staticmethod
    def __lininterp(X,Y,x):
        idx = X.searchsorted(x)
        y = Y[idx-1] + (Y[idx]-Y[idx-1])/(X[idx]-X[idx-1]) * (x-X[idx-1])
        return y
