from calculate import calculate_chart

def summarize_relationship(chart_a: dict, chart_b: dict) -> str:
    """
    Convert two charts into a relationship-focused summary for LLM
    """
    a_asc = chart_a["ascendant"]
    b_asc = chart_b["ascendant"]

    a_moon = chart_a["planets"]["Moon"]["sign"]
    b_moon = chart_b["planets"]["Moon"]["sign"]

    a_venus = chart_a["planets"]["Venus"]["sign"]
    b_venus = chart_b["planets"]["Venus"]["sign"]

    summary = (
        f"Person A Ascendant: {a_asc}, Moon: {a_moon}, Venus: {a_venus}. "
        f"Person B Ascendant: {b_asc}, Moon: {b_moon}, Venus: {b_venus}. "
        "Analyze emotional, romantic, and long-term compatibility."
    )

    return summary
