import os, sys
import vtk

from vtk.util import numpy_support as ns
import numpy as np

class TagImageFromPolyDataSurface():
    def __init__(self, image):
        self.image = image
        
        self.octree = vtk.vtkOctreePointLocator()
        self.octree.SetDataSet(self.image)
        self.octree.BuildLocator()
        
        self.extents = [float()] * 6
        
        self.voi = vtk.vtkExtractVOI()
        self.selection = vtk.vtkSelectEnclosedPoints()
    
    def ConvertBoundsToExtents(self, polydata):
        bounds = np.asarray(polydata.GetBounds()).astype(int).tolist()
        
        pcoords = [float()] * 3
        x   = [bounds[0]-1, bounds[2]-1, bounds[4]-1]
        ijk = [bounds[1]+1, bounds[3]+1, bounds[5]+1]
        self.image.ComputeStructuredCoordinates(x, ijk, pcoords)
        
        self.extents[0] = ijk[0] + 1
        self.extents[2] = ijk[1] + 1
        self.extents[4] = ijk[2] + 1
        
        pcoords = [float()] * 3
        x   = [bounds[0]-1, bounds[2]-1, bounds[4]-1]
        ijk = [bounds[1]+1, bounds[3]+1, bounds[5]+1]
        self.image.ComputeStructuredCoordinates(ijk, x, pcoords)
        
        self.extents[1] = x[0] + 1
        self.extents[3] = x[1] + 1
        self.extents[5] = x[2] + 1
        
        print("Conversion: {0}".format(self.extents))
    
    def TagImage(self, polydata, tag_value):
        self.ConvertBoundsToExtents(polydata)
        
        self.voi.SetInputData(image)
        self.voi.SetVOI(self.extents)
        self.voi.Update()
        
        self.selection.SetSurfaceData(polydata)
        self.selection.SetInputData(self.voi.GetOutput())
        self.selection.Update()
        
        scalars = ns.vtk_to_numpy(self.image.GetPointData().GetScalars())
        scalars_name = self.image.GetPointData().GetScalars().GetName()
        
        num_points = self.selection.GetOutput().GetNumberOfPoints()
        for i in range(num_points):
            if self.selection.IsInside(i) == True:
                iD = self.octree.FindClosestPoint(self.selection.GetOutput().GetPoint(i))
                scalars[iD] = tag_value
        
        s = ns.numpy_to_vtk(scalars)
        s.SetName(scalars_name)
        
        self.image.GetPointData().SetScalars(s)
