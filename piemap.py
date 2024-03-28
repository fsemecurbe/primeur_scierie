import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.affinity import rotate

def pie(center, quantity, radius):
    circle = Point(center).buffer(radius,quadsegs=100).boundary
    circle = rotate(circle,90, origin='centroid')
    x,y = circle.xy
    x = np.array(x)
    y = np.array(y)
    indice = np.floor(np.cumsum(quantity)/np.sum(quantity) * x.shape).astype(int)
    indice = np.concatenate([[0], indice, [x.shape[0]]])
    geometry = []
    quantity = []
    for i in range(indice.shape[0]-2):
        try:
            coordonnes = [[xt,yt]  for xt,yt in zip(x[indice[i:(i+2)][0]:(indice[i:(i+2)][1]+1)],y[indice[i:(i+2)][0]:(indice[i:(i+2)][1]+1)])]
            coordonnes = np.append(coordonnes,np.array(center, ndmin=2),axis=0)
            geometry.append(Polygon(coordonnes))
            quantity.append(i)
        except Exception:
            pass
        
    return(gpd.GeoDataFrame(geometry=geometry, data={'quantity':quantity}))  

def piemap(data, vars_quantity, vars_coords=None, l=None):
    """
    Create a pie map
 
    Parameters
    ----------
    data : pandas dataframe or geopandas spatial dataframe 
           
    vars_quantity : a list of variables with the stock variables to do the pie
                   
    vars_coords : if data is pandas dataframe (no geometry columns), vars_coords is a list with the colnames with the coordinates 
 
    l : float. to adapt the size of pie. By default, l is performed to allow the all area of the pie to be just 1/5 of the environnement area.  
 
    Returns
    -------
    Spatial Dataframe
        
    """
    if vars_coords is None:
        coords = np.array([[x,y]  for x, y in zip(data.centroid.x, data.centroid.y)])
        area = data.geometry.unary_union.convex_hull.area
    else:
        coords=data[vars_coords].to_numpy()
        area = Polygon(coords).convex_hull.area
        
    q = data[vars_quantity].sum(1).to_numpy()
    
    if l is None:
        l = area/(5*np.sum(q))
         
    radius = (q*l/np.pi)**0.5  
    quantity = data[vars_quantity].to_numpy()
    
    sdf = []
    for nrow in range(0,data.shape[0]):
            center_n = coords[nrow,:]
            quantity_n = quantity[nrow,:]
            radius_n = radius[nrow]
            sdf.append(pie(center_n, quantity_n, radius_n))
    
    sdf = pd.concat(sdf)
    return(sdf)

def main():
    test = pd.DataFrame({'x':np.random.default_rng().uniform(0,100000,10),
                     'y':np.random.default_rng().uniform(0,100000,10),
                     'q1':np.random.default_rng().uniform(0,100,10),
                     'q2':np.random.default_rng().uniform(0,500,10),
                     'q3':np.random.default_rng().uniform(0,500,10)
                    })
    test = gpd.GeoDataFrame(test, geometry=gpd.points_from_xy(test.x, test.y))
    test_pie = piemap(test,vars_quantity=['q1','q2','q3'])
    test_pie.plot('quantity')

if __name__ == "__main__":
    main()