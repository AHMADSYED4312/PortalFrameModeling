from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Display.SimpleGui import init_display

def create_i_section(width, depth, flange_thickness, web_thickness, length):
    '''
    Creates an I-section CAD model with specified dimensions.
    '''
    web_height = depth - 2 * flange_thickness

    # Create the bottom flange
    bottom_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()

    # Create the top flange
    top_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, depth - flange_thickness)) # Move to the top
    top_flange = BRepBuilderAPI_Transform(top_flange, trsf, True).Shape()

    # Create the web
    web = BRepPrimAPI_MakeBox(length, web_thickness, web_height).Shape()
    trsf.SetTranslation(gp_Vec(0, (width - web_thickness) / 2, flange_thickness)) # Center web
    web = BRepBuilderAPI_Transform(web, trsf, True).Shape()

    # Fuse the components
    i_section = BRepAlgoAPI_Fuse(bottom_flange, top_flange).Shape()
    i_section = BRepAlgoAPI_Fuse(i_section, web).Shape()

    return i_section

def create_lacing_member(start_point, end_point, width=100.0, thickness=8.0):
    
    #Creates a lacing member (flat bar) between two I-sections.
    length = ((end_point.X() - start_point.X())**2 + (end_point.Z() - start_point.Z())**2) ** 0.5
    lacing = BRepPrimAPI_MakeBox(length, width, thickness).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(start_point.X(), start_point.Y(), start_point.Z()))
    lacing = BRepBuilderAPI_Transform(lacing, trsf, True).Shape()
    return lacing

def create_column():
    '''
    Creates a laced compound column consisting of two I-sections, plates, and diagonal lacing
    members.'''
    column_height = 6000.0 # 6000 mm or 20 feet
    i_section_width = 100.0
    i_section_depth = 200.0
    flange_thickness = 10.0

    web_thickness = 6.0
    spacing = 450.0 # Distance between the two I-sections
    lacing_spacing = 450.0 # Spacing for lacing members

    # Create two I-sections
    ismb1 = create_i_section(i_section_width, i_section_depth, flange_thickness, web_thickness,
    column_height)
    ismb2 = create_i_section(i_section_width, i_section_depth, flange_thickness, web_thickness,
    column_height)

    # Position the second I-section
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(spacing, 0, 0))
    ismb2 = BRepBuilderAPI_Transform(ismb2, trsf, True).Shape()

    # Create top and bottom plates (430mm x 300mm x 10mm)
    top_plate = BRepPrimAPI_MakeBox(430, 300, 10).Shape()
    trsf.SetTranslation(gp_Vec(-215, -150, column_height))
    top_plate = BRepBuilderAPI_Transform(top_plate, trsf, True).Shape()

    bottom_plate = BRepPrimAPI_MakeBox(430, 300, 10).Shape()
    trsf.SetTranslation(gp_Vec(-215, -150, 0))
    bottom_plate = BRepBuilderAPI_Transform(bottom_plate, trsf, True).Shape()

    # Add diagonal lacing members
    lacing_members = []
    for i in range(0, int(column_height), int(lacing_spacing)):
        start1 = gp_Pnt(-spacing / 2, 0, i)
        end1 = gp_Pnt(spacing / 2, 0, i + lacing_spacing)
        lacing_members.append(create_lacing_member(start1, end1))

        start2 = gp_Pnt(spacing / 2, 0, i)
        end2 = gp_Pnt(-spacing / 2, 0, i + lacing_spacing)
        lacing_members.append(create_lacing_member(start2, end2))

    # Fuse all parts together
    column = BRepAlgoAPI_Fuse(ismb1, ismb2).Shape()
    column = BRepAlgoAPI_Fuse(column, top_plate).Shape()
    column = BRepAlgoAPI_Fuse(column, bottom_plate).Shape()

    for lacing in lacing_members:
        column = BRepAlgoAPI_Fuse(column, lacing).Shape()

    return column

def display_column():
    display, start_display, add_menu, add_function_to_menu = init_display()
    column = create_column()
    display.DisplayShape(column, update=True)
    display.FitAll()
    start_display()

if __name__ == "__main__":
    display_column()