from dataclasses import dataclass
import oracledb.connection as dbc
import oracledb.dbobject as dbo


class SDOGeometryTooLargeError(Exception):
    """An SDO_GEOMETRY has a limit of 1048575 data points"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    @staticmethod
    def get_limit() -> int:
        """Get the limit of data points allowed in an SDO_GEOMETRY"""
        return 1048575


@dataclass 
class SDOPointType:
    """Represents the SDO_POINT_TYPE component 
       of an SDO_GEOMETRY type
    """
    x: float = None 
    y: float = None 
    z: float = None

    def __str__(self) -> str:
        return f'{self.x}, {self.y}, {self.z}'


@dataclass
class SDOGeometry:

    # Class scope variables 
    geometry_type: int = None
    srid: int = None
    point: SDOPointType = None 
    element_info: list = None 
    ordinates: list = None 

    def __call__(self, *args, **kwds) -> dbo.DbObject:
        """Fetch the SDO_GEOMETRY object
        
        The first parameter passed in the arguments must be 
        an oracledb database connection
        """
        # The first argument passed in must be an Oracle connection
        if type(args[0]) != dbc.Connection:
            raise AttributeError('The first argument must be an Oracle connection')
        # Get the connection from the first index of the array 
        conn = args[0]
        # Create the SDO_GEOMETRY using the connection 
        sdo_geometry_type = conn.gettype('SDO_GEOMETRY')
        # The variable declared next is the geometry object
        sdo_geometry = sdo_geometry_type.newobject()
        # Set the geometry type and SRID
        sdo_geometry.SDO_GTYPE = self.geometry_type 
        sdo_geometry.SDO_SRID = self.srid
        # If there is an X and Y
        if self.point is not None and self.point.x is not None and self.point.y is not None:
            # Create the point type
            sdo_point_type = conn.gettype('SDO_POINT_TYPE')
            sdo_geometry.SDO_POINT = sdo_point_type.newobject()
            setattr(sdo_geometry.SDO_POINT, 'X', self.point.x)
            setattr(sdo_geometry.SDO_POINT, 'Y', self.point.y)
            setattr(sdo_geometry.SDO_POINT, 'Z', self.point.z)
        else:
            # Otherwise is a 1d + geometry 
            sdo_elem_info_type = conn.gettype('SDO_ELEM_INFO_ARRAY')
            sdo_ordinates_type = conn.gettype('SDO_ORDINATE_ARRAY')
            sdo_geometry.SDO_ELEM_INFO = sdo_elem_info_type.newobject()
            # The element information may be None
            if self.element_info is not None:
                sdo_geometry.SDO_ELEM_INFO.extend(self.element_info)
            sdo_geometry.SDO_ORDINATES = sdo_ordinates_type.newobject()
            # The ordinates may be None 
            if self.ordinates is not None:
                sdo_geometry.SDO_ORDINATES.extend(self.ordinates)
        # Return the geometry 
        return sdo_geometry
        
    def __str__(self) -> str:
        """String representation of the class"""
        print(self.element_info)
        return f"""
SDO_GEOMETRY (
    SDO_GTYPE: {self.geometry_type},
    SDO_SRID:  {self.srid}, 
    SDO_POINT: ({self.point}),
    SDO_ELEM_INFO: ({','.join([str(x) for x in self.element_info]) if self.element_info is not None else None}),
    SDO_ORDINATES: ( < not printed > )
)
        """


class OracleJSONGeometryReader:
    """Read an Oracle JSON geometry
    
    This class provides a method for reading a geometry 
    encoded in Oracle's JSON geometry and converting it 
    to SDO_GEOMETRY.
    """

    def to_sdo_geometry(self, data) -> SDOGeometry:
        """Read an Oracle JSON geometry
        
        Keyword arguments:
        data - This must be a JSON encoded object
        """
        # New SDOGeometry
        sdo_geometry = SDOGeometry()
        # The SRID is obtained from the srid attribute 
        sdo_geometry.srid = data['srid']
        # Only dealing with geometrycollection and polygon for now
        if list(data.keys())[1] == 'geometrycollection':
            # The geometry type is 2007
            sdo_geometry.geometry_type = 2007
            # Initialize the element info and ordinates
            sdo_geometry.element_info = []
            sdo_geometry.ordinates = []
            # There will be a number of polygons in the multipolygon
            for g in data['geometrycollection']['geometries']:
                # Process the polygon 
                sdo_geometry = self.__polygon(
                    sdo_geometry, 
                    g['polygon']
                )
        elif list(data.keys())[1] == 'polygon':
            # The geometry type must be set here
            sdo_geometry.geometry_type = 2003
            # Initialize the element info and ordinates
            sdo_geometry.element_info = []
            sdo_geometry.ordinates = []
            # Call the method that processes the polygon.
            sdo_geometry = self.__polygon(sdo_geometry, data['polygon'])
        # Instantiate the object
        return sdo_geometry

    def __polygon(self, sdo_geometry: SDOGeometry, data):
        # A polygon has an outer ring and, optionally, 
        # several inner rings. The SDO_ETYPE will start 
        # at 1003 and then become 2003
        sdo_etype = 1003
        # For each of the lines in the boundary
        for b in data['boundary']:
            # Add the data to the elem info
            sdo_geometry.element_info.append(len(sdo_geometry.ordinates) + 1)
            sdo_geometry.element_info.append(sdo_etype)
            sdo_geometry.element_info.append(1)
            sdo_etype = 2003
            # Get the datapoints for the line which is an array 
            # of point arrays
            datapoints = b['line']['datapoints']
            # But we want a straight list
            sdo_geometry.ordinates.extend([x for a in datapoints for x in a])
            # If the length of the offset is greater than 1048575 then
            # raise an exception. A geometry this large can't be inserted
            if len(sdo_geometry.ordinates) > SDOGeometryTooLargeError.get_limit():
                raise SDOGeometryTooLargeError(f'The geometry has too many points {len(sdo_geometry.ordinates)}')
        return sdo_geometry
    

if __name__ == '__main__':
    # The code in this section will only run if 
    # the module is executed directly - ie with 
    # > python.exe sdo.py

    # Instantiate an object of type SDOGeometry like this
    sdo_geometry = SDOGeometry()
    # The object has variables which are defined in the class
    # tempate above. The SRID of the object is set like this:
    sdo_geometry.srid = 4326
    # The geometry type (SDO_GTYPE) is set like this:
    sdo_geometry.geometry_type = 2001 
    # This is a point and the point variable of the class must 
    # be an SDO_POINT_TYPE. In this code, the SDO_POINT_TYPE is 
    # represented by another class - called SDOPointType
    sdo_geometry.point = SDOPointType()
    sdo_geometry.point.x = -65.16848362783729
    sdo_geometry.point.y = 44.88479897442648

    # The SDOGeometry class implements the __str__ dunder method
    # This method is called when the class is cast to a string. This 
    # happens when the print() function is called on the class. The 
    # __str__ dunder method can be used to control how the class is 
    # printed and, in this case, we want to see the contents of the 
    # class represented as though it is an SDO_GEOMETRY constructor.
    print(sdo_geometry)
