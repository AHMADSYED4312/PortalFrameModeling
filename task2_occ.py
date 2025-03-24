from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Dir, gp_Ax1
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Extend.DataExchange import write_step_file
import ezdxf

# Define basic parameters
column_height = 6096  # 20 feet in mm
spacing = 450  # mm between I-sections
batten_width = 430  # mm
batten_depth = 300  # mm
batten_thickness = 10  # mm
lace_width = 100  # mm
lace_thickness = 8  # mm
lace_spacing = 450  # mm
bolt_radius = 10  # mm
bolt_height = 10  # mm

# Create I-Sections (ISMB 200 - Simplified)
def create_i_section(base_point):
    width = 200
    flange_thickness = 10
    web_thickness = 6
    web_height = 200
    
    # Web
    web = BRepPrimAPI_MakeBox(base_point, width, web_thickness, web_height).Shape()
    
    # Flanges
    top_flange = BRepPrimAPI_MakeBox(base_point.Translated(gp_Vec(0, -flange_thickness, web_height)), width, flange_thickness, 10).Shape()
    bottom_flange = BRepPrimAPI_MakeBox(base_point.Translated(gp_Vec(0, -flange_thickness, 0)), width, flange_thickness, 10).Shape()
    
    # Fuse parts
    return BRepAlgoAPI_Fuse(BRepAlgoAPI_Fuse(web, top_flange).Shape(), bottom_flange).Shape()

# Create two I-sections
base1 = gp_Pnt(0, 0, 0)
base2 = gp_Pnt(spacing, 0, 0)
i_section1 = create_i_section(base1)
i_section2 = create_i_section(base2)

# Create batten plates
top_batten = BRepPrimAPI_MakeBox(gp_Pnt(-10, -batten_thickness, column_height), batten_width, batten_thickness, batten_depth).Shape()
bottom_batten = BRepPrimAPI_MakeBox(gp_Pnt(-10, -batten_thickness, 0), batten_width, batten_thickness, batten_depth).Shape()

# Create diagonal laces
def create_lace(start_height):
    lace = BRepPrimAPI_MakeBox(gp_Pnt(0, -lace_thickness, start_height), spacing, lace_thickness, lace_width).Shape()
    # Rotate the lace to 45 degrees
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, start_height), gp_Dir(1, 0, 0)), 0.785)  # 45 degrees
    return BRepBuilderAPI_Transform(lace, trsf).Shape()

laces = [create_lace(i * lace_spacing) for i in range(1, int(column_height / lace_spacing))]

# Create bolts in top view
def create_bolt(position):
    axis = gp_Ax1(position, gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCylinder(position, bolt_radius, bolt_height).Shape()

bolts = [create_bolt(gp_Pnt(spacing / 2 - 75 + i * 150, 0, 0)) for i in range(3)]

# Assemble the column
compound = TopoDS_Compound()
builder = BRep_Builder()
builder.MakeCompound(compound)
for part in [i_section1, i_section2, top_batten, bottom_batten] + laces + bolts:
    builder.Add(compound, part)

# Export to STEP file
write_step_file(compound, "laced_column.step")

# Generate DXF for 2D drawing
def create_dxf():
    doc = ezdxf.new()
    msp = doc.modelspace()
    
    # Draw I-sections in top view
    msp.add_lwpolyline([(0, 0), (200, 0), (200, 6), (0, 6)], close=True)
    msp.add_lwpolyline([(450, 0), (650, 0), (650, 6), (450, 6)], close=True)
    
    # Draw battens
    msp.add_lwpolyline([(-10, -10), (430, -10), (430, 10), (-10, 10)], close=True)
    
    # Draw bolts
    for i in range(4):
        msp.add_circle((spacing / 2 - 75 + i * 150, 0), bolt_radius)
    
    # Save DXF file
    doc.saveas("laced_column.dxf")

create_dxf()
