from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Pnt
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Display.SimpleGui import init_display

# Import existing shape functions from provided scripts
from draw_i_section import create_i_section  # Function to create I-section
from draw_rectangular_prism import create_rectangular_prism  # Function to create rectangular shapes

def create_column(height, flange_thickness, web_thickness):
    """Creates a vertical column using the I-section profile."""
    return create_i_section(height, flange_thickness, web_thickness)

def create_rafter(length, angle, flange_thickness, web_thickness):
    """Creates an inclined rafter using the I-section profile."""
    rafter = create_i_section(length, flange_thickness, web_thickness)
    
    # Rotate rafter to the specified angle
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Vec(1, 0, 0), angle)
    rafter = BRepBuilderAPI_Transform(rafter, trsf, True).Shape()
    return rafter

def create_purlin(length, width, height):
    """Creates a horizontal purlin using a rectangular box shape."""
    return create_rectangular_prism(length, width, height)

def create_portal_frame():
    """Creates a 3D model of a portal frame with columns, rafters, and purlins."""
    # Define frame parameters
    column_height = 6000.0
    rafter_length = 5000.0
    purlin_length = 4000.0
    purlin_width = 100.0
    purlin_height = 50.0
    flange_thickness = 10.0
    web_thickness = 6.0
    angle = 30  # in degrees
    
    # Create columns
    column1 = create_column(column_height, flange_thickness, web_thickness)
    column2 = create_column(column_height, flange_thickness, web_thickness)
    
    # Position second column
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(6000, 0, 0))  # Column spacing
    column2 = BRepBuilderAPI_Transform(column2, trsf, True).Shape()
    
    # Create rafters
    rafter1 = create_rafter(rafter_length, angle, flange_thickness, web_thickness)
    rafter2 = create_rafter(rafter_length, -angle, flange_thickness, web_thickness)
    
    # Position rafters
    trsf.SetTranslation(gp_Vec(0, 0, column_height))
    rafter1 = BRepBuilderAPI_Transform(rafter1, trsf, True).Shape()
    rafter2 = BRepBuilderAPI_Transform(rafter2, trsf, True).Shape()
    
    # Create purlin
    purlin = create_purlin(purlin_length, purlin_width, purlin_height)
    
    # Position purlin at the midpoint
    trsf.SetTranslation(gp_Vec(3000, 0, column_height + 1000))
    purlin = BRepBuilderAPI_Transform(purlin, trsf, True).Shape()
    
    # Fuse all components
    frame = BRepAlgoAPI_Fuse(column1, column2).Shape()
    frame = BRepAlgoAPI_Fuse(frame, rafter1).Shape()
    frame = BRepAlgoAPI_Fuse(frame, rafter2).Shape()
    frame = BRepAlgoAPI_Fuse(frame, purlin).Shape()
    
    return frame

def display_portal_frame():
    """Displays the generated portal frame model."""
    display, start_display, add_menu, add_function_to_menu = init_display()
    frame = create_portal_frame()
    display.DisplayShape(frame, update=True)
    display.FitAll()
    start_display()

if __name__ == "__main__":
    display_portal_frame()
