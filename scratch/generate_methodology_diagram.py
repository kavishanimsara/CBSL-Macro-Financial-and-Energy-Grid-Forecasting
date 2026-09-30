import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_methodology_diagram():
    # Set up figure
    fig, ax = plt.subplots(figsize=(18, 11), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Main Title
    plt.text(50, 96, "CBSL Macro-Financial & Energy Grid Forecasting Framework", 
             ha='center', va='center', fontsize=20, fontweight='bold', color='#1E293B', family='sans-serif')
    plt.text(50, 93, "End-to-End Methodological Architecture & Multi-Track Pipeline", 
             ha='center', va='center', fontsize=12, fontweight='medium', color='#64748B', style='italic', family='sans-serif')

    # Colors
    c_blue_bg, c_blue_border, c_blue_txt = '#E3F2FD', '#1565C0', '#0D47A1'
    c_purple_bg, c_purple_border, c_purple_txt = '#F3E5F5', '#7B1FA2', '#4A148C'
    c_orange_bg, c_orange_border, c_orange_txt = '#FFF3E0', '#E65100', '#BF360C'
    c_green_bg, c_green_border, c_green_txt = '#E8F5E9', '#2E7D32', '#1B5E20'
    c_amber_bg, c_amber_border, c_amber_txt = '#FFF8E1', '#F57F17', '#E65100'

    # Helper box drawer
    def draw_box(x, y, w, h, bg_color, border_color, title, subtitle, bullets, radius=0.015):
        box = patches.FancyBboxPatch((x, y), w, h,
                                    boxstyle=f"round,pad=0.3,rounding_size=1.2",
                                    ec=border_color, fc=bg_color, lw=2, zorder=2)
        ax.add_patch(box)
        
        # Title header box
        header_box = patches.FancyBboxPatch((x, y + h - 2.8), w, 2.8,
                                           boxstyle="round,pad=0,rounding_size=0.8",
                                           ec=border_color, fc=border_color, lw=0, zorder=3)
        ax.add_patch(header_box)
        
        plt.text(x + w/2, y + h - 1.4, title, ha='center', va='center', 
                 fontsize=11, fontweight='bold', color='#FFFFFF', zorder=4, family='sans-serif')
        
        if subtitle:
            plt.text(x + w/2, y + h - 4.2, subtitle, ha='center', va='center', 
                     fontsize=9.5, fontweight='bold', color=border_color, zorder=4, family='sans-serif')
            start_y = y + h - 6.2
        else:
            start_y = y + h - 4.2

        for i, line in enumerate(bullets):
            plt.text(x + 1.2, start_y - (i * 2.2), line, ha='left', va='center', 
                     fontsize=8.5, color='#334155', zorder=4, family='sans-serif')

    # Helper Arrow Drawer
    def draw_arrow(x1, y1, x2, y2, label=""):
        arrow = patches.FancyArrowPatch((x1, y1), (x2, y2),
                                        arrowstyle='->,head_width=0.4,head_length=0.6',
                                        connectionstyle="arc3,rad=0",
                                        ec='#475569', fc='#475569', lw=2, zorder=5)
        ax.add_patch(arrow)
        if label:
            mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
            plt.text(mid_x, mid_y + 1.2, label, ha='center', va='center', 
                     fontsize=8, fontweight='bold', color='#475569', 
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1),
                     zorder=6)

    # -------------------------------------------------------------------------
    # PHASE 1: DATA INGESTION (Top Row)
    # -------------------------------------------------------------------------
    draw_box(4, 73, 88, 16, c_blue_bg, c_blue_border, 
             "PHASE 1: MULTI-SOURCE DATA INGESTION LAYER", 
             "Primary Raw Data Collections (2018 – 2024)", [
                 "• CBSL Reports: Inflation Indices (CCPI Headline/Core), SDFR/SLFR Policy Rates, Broad Money (M2b), 3M T-Bills",
                 "• CEB Grid Operations: System Peak Demand (MW), Daily Gross Energy Generation (Hydro, Thermal, Solar, Wind)",
                 "• External Trade & CSE Equities: Trade Balance, Remittances, Tourist Arrivals, ASPI Index, Brent Oil & Singapore Gasoil"
             ])

    draw_arrow(48, 73, 48, 66, "Raw Time-Series Inflow")

    # -------------------------------------------------------------------------
    # PHASE 2: PREPROCESSING & STATIONARITY (Middle-Top Row)
    # -------------------------------------------------------------------------
    draw_box(4, 49, 88, 17, c_purple_bg, c_purple_border, 
             "PHASE 2: DATA CLEANING, ANOMALY REPAIR & STATIONARITY DIAGNOSTICS", 
             "Automated PDF Table Parsing & ADF Unit Root Diagnostics", [
                 "• PDF OCR Engine: Automated table extraction via pdfplumber & regular expression regex string parsing routines",
                 "• Anomaly Repair: Outlier detection using Z-score boundaries (|Z| > 3.5) & missing data linear spline interpolation",
                 "• ADF Stationarity Test: Evaluates unit root H0: γ=0; non-stationary series I(1) converted via 1st Difference Log Δln(Yt)"
             ])

    draw_arrow(48, 49, 48, 42, "Clean Stationarity-Verified Datasets")

    # -------------------------------------------------------------------------
    # PHASE 3: ZERO-LOOKAHEAD FEATURE PIPELINE (Middle Row)
    # -------------------------------------------------------------------------
    draw_box(4, 27, 88, 15, c_orange_bg, c_orange_border, 
             "PHASE 3: ZERO-LOOKAHEAD FEATURE ENGINEERING PIPELINE", 
             "Strict Temporal Alignment & Leakage Prevention", [
                 "• Autoregressive Lags: Construct past lag features (t-1, t-2, ..., t-6) strictly avoiding future lookahead bias",
                 "• Past-Only Rolling Statistics: Computes past 3-month rolling averages, standard deviations, and 6-month peak maximums",
                 "• Exogenous Alignment: Synchronizes policy rate corridor shifts and international energy import benchmark prices"
             ])

    draw_arrow(48, 27, 48, 20, "Stationary Feature Matrix (X, y)")

    # -------------------------------------------------------------------------
    # PHASE 4: 4 MODELING TRACKS (Bottom-Middle Row - 4 Side-by-Side Boxes)
    # -------------------------------------------------------------------------
    box_w = 20.5
    gap = 2.0
    start_x = 4.0
    y_p4 = 4.0
    h_p4 = 15.0

    # Track 1
    draw_box(start_x, y_p4, box_w, h_p4, c_green_bg, c_green_border,
             "TRACK 1: MACRO", "CCPI Inflation Rate", [
                 "• Model: SARIMAX + Ridge",
                 "• Spec: (1,1,1)(1,1,1)s=12",
                 "• Exog: SDFR, SLFR, M2b",
                 "• Score: RMSE = 0.84%"
             ])

    # Track 2
    draw_box(start_x + box_w + gap, y_p4, box_w, h_p4, c_green_bg, c_green_border,
             "TRACK 2: ENERGY", "Peak Load (MW)", [
                 "• Model: Delta-Lasso + XGB",
                 "• Feature Selection: L1 α=0.015",
                 "• Generation Mix: Hydro/Thermal",
                 "• Score: MAE = 38.4 MW"
             ])

    # Track 3
    draw_box(start_x + (box_w + gap)*2, y_p4, box_w, h_p4, c_green_bg, c_green_border,
             "TRACK 3: EXTERNAL", "Official Reserves", [
                 "• Model: VAR(3) + LSTM",
                 "• Spec: 64 Units | Dropout 0.2",
                 "• Exog: Remittances & Brent",
                 "• Score: MAPE = 2.15%"
             ])

    # Track 4
    draw_box(start_x + (box_w + gap)*3, y_p4, box_w, h_p4, c_green_bg, c_green_border,
             "TRACK 4: EQUITY", "ASPI Trend Direction", [
                 "• Model: GARCH(1,1) + RF",
                 "• Volatility: Conditional σt²",
                 "• Classifier: 250 Trees",
                 "• Score: Accuracy = 81.06%"
             ])

    # Arrows connecting Phase 3 to all 4 Tracks
    for i in range(4):
        tx = start_x + i*(box_w + gap) + box_w/2
        draw_arrow(tx, 27, tx, 19)

    # Footer Metadata
    plt.text(50, 1.2, "Generated for Capstone Project II | Department of Data Science | CBSL Macro-Financial & Energy Grid Analytics Platform",
             ha='center', va='center', fontsize=8, color='#94A3B8', style='italic', family='sans-serif')

    plt.tight_layout()
    
    # Paths to save
    workspace_dir = r"d:\university life\Semester IV\Capstone Project in Data Science II\CBSL Macro-Financial and Energy Grid Forecasting"
    artifact_dir = r"C:\Users\kavisha\.gemini\antigravity\brain\b509d57c-9cd9-4c4a-a32f-83963c335d2d"

    png_path_ws = os.path.join(workspace_dir, "methodology_diagram.png")
    svg_path_ws = os.path.join(workspace_dir, "methodology_diagram.svg")
    
    png_path_art = os.path.join(artifact_dir, "methodology_diagram.png")
    svg_path_art = os.path.join(artifact_dir, "methodology_diagram.svg")

    fig.savefig(png_path_ws, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    fig.savefig(svg_path_ws, format='svg', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')

    fig.savefig(png_path_art, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    fig.savefig(svg_path_art, format='svg', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')

    plt.close(fig)
    print("SUCCESSFULLY GENERATED DIAGRAM IMAGES!")
    print("Workspace PNG:", png_path_ws)
    print("Workspace SVG:", svg_path_ws)
    print("Artifact PNG:", png_path_art)
    print("Artifact SVG:", svg_path_art)

if __name__ == "__main__":
    draw_methodology_diagram()
