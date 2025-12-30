from calculate import calculate_chart

def summarize_relationship(chart_a: dict, chart_b: dict) -> str:
    """
    Deep Synastry Analysis: Converts two charts into a high-detail 
    relationship summary for NAKSH.
    """
    # Person A Details
    a_name = chart_a.get("name", "Person A")
    a_asc = chart_a["ascendant"]
    a_moon = chart_a["planets"]["Moon"]["sign"]
    a_venus = chart_a["planets"]["Venus"]["sign"]
    a_mars = chart_a["planets"]["Mars"]["sign"]
    a_jupiter = chart_a["planets"]["Jupiter"]["sign"]

    # Person B Details
    b_name = chart_b.get("name", "Person B")
    b_asc = chart_b["ascendant"]
    b_moon = chart_b["planets"]["Moon"]["sign"]
    b_venus = chart_b["planets"]["Venus"]["sign"]
    b_mars = chart_b["planets"]["Mars"]["sign"]
    b_jupiter = chart_b["planets"]["Jupiter"]["sign"]

    # Complex relationship logic for the LLM
    summary = (
        f"SYNSTRY DATA:\n"
        f"1. {a_name}: Ascendant {a_asc}, Moon {a_moon}, Venus {a_venus}, Mars {a_mars}, Jupiter {a_jupiter}.\n"
        f"2. {b_name}: Ascendant {b_asc}, Moon {b_moon}, Venus {b_venus}, Mars {b_mars}, Jupiter {b_jupiter}.\n\n"
        f"INSTRUCTIONS FOR ANALYSIS:\n"
        f"- Compare Moon signs for 'Mann ka Mel' (emotional synchronization).\n"
        f"- Compare Venus and Mars for 'Chemistry & Attraction'. Check if Mars signs are in 'shashtashtak' (6-8 relationship) which causes ego fights.\n"
        f"- Check Jupiter for long-term stability and values.\n"
        f"- Look for any major clashes like one person's Saturn sitting on other's Moon."
    )

    return summary