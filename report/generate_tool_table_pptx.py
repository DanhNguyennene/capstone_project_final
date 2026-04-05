#!/usr/bin/env python3
"""
Generate PowerPoint slide with Agent Tool Access table
Usage: python generate_tool_table_pptx.py
Output: tool_access_table.pptx
"""

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor
except ImportError:
    print("Error: python-pptx not installed")
    print("Install with: pip install python-pptx")
    exit(1)

def create_tool_table_slide():
    """Create PowerPoint with agent tool access table"""
    
    # Create presentation
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Add blank slide
    blank_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(blank_layout)
    
    # Add title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "Agent Tool Access Matrix"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(32)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 58, 138)  # Blue-900
    title_para.alignment = PP_ALIGN.CENTER
    
    # Table data
    headers = ["Tool", "Main Agent", "Analysis Sub", "Action Sub", "Safety", "Purpose"]
    data = [
        ["squeue/sacct/sinfo", "❌", "✅", "✅", "✅ Safe", "Query cluster state"],
        ["run_analysis", "❌", "✅", "❌", "✅ Safe", "Predefined diagnostics"],
        ["web_search", "❌", "✅", "✅", "✅ Safe", "Documentation lookup"],
        ["srun/salloc", "❌", "❌", "✅", "✅ Safe", "Interactive execution"],
        ["scancel/sbatch", "❌", "❌", "✅", "⚠️ Dangerous", "Job lifecycle control"],
        ["scontrol_*", "❌", "❌", "✅", "⚠️ Dangerous", "Job/cluster modification"],
        ["sacctmgr_*", "❌", "❌", "✅", "⚠️ Dangerous", "Account management"],
        ["generate_chart", "✅", "❌", "❌", "✅ Safe", "Visualization"],
        ["confirm/cancel", "✅", "❌", "❌", "🔐 Protected", "Confirmation flow"],
    ]
    
    # Create table
    rows = len(data) + 1  # +1 for header
    cols = len(headers)
    
    table = slide.shapes.add_table(
        rows, cols, 
        Inches(0.5), Inches(1.2), 
        Inches(9), Inches(5.5)
    ).table
    
    # Set column widths
    col_widths = [Inches(1.8), Inches(1.2), Inches(1.3), Inches(1.2), Inches(1.5), Inches(2)]
    for i, width in enumerate(col_widths):
        table.columns[i].width = width
    
    # Header row
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        
        # Header styling
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 58, 138)  # Blue-900
        
        para = cell.text_frame.paragraphs[0]
        para.font.size = Pt(11)
        para.font.bold = True
        para.font.color.rgb = RGBColor(255, 255, 255)  # White
        para.alignment = PP_ALIGN.CENTER
    
    # Data rows
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, cell_text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = cell_text
            
            # Cell styling based on content
            if "⚠️ Dangerous" in cell_text:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(254, 226, 226)  # Red-100
            elif "✅ Safe" in cell_text:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(220, 252, 231)  # Green-100
            elif "🔐 Protected" in cell_text:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(254, 243, 199)  # Yellow-100
            elif row_idx % 2 == 0:
                # Alternate row shading
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)  # Slate-50
            
            # Text styling
            para = cell.text_frame.paragraphs[0]
            para.font.size = Pt(10)
            
            # Center align for agent columns
            if col_idx in [1, 2, 3, 4]:  # Agent columns + Safety
                para.alignment = PP_ALIGN.CENTER
            
            # Bold for tool names
            if col_idx == 0:
                para.font.bold = True
    
    # Add legend
    legend_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.9), Inches(9), Inches(0.4))
    legend_frame = legend_box.text_frame
    legend_frame.text = "Legend: ✅ = Has Access, ❌ = No Access | Safety: ✅ Safe (Execute immediately) | ⚠️ Dangerous (Needs confirmation) | 🔐 Protected (User control)"
    legend_para = legend_frame.paragraphs[0]
    legend_para.font.size = Pt(9)
    legend_para.font.color.rgb = RGBColor(75, 85, 99)  # Gray-600
    legend_para.alignment = PP_ALIGN.CENTER
    
    # Save presentation
    output_file = "tool_access_table.pptx"
    prs.save(output_file)
    print(f"✅ PowerPoint created: {output_file}")
    print(f"📊 Table: {len(data)} tools x {len(headers)} columns")
    return output_file

if __name__ == "__main__":
    create_tool_table_slide()
