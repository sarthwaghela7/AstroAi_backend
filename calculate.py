import swisseph as swe
from datetime import datetime
import pytz

# ------------------ ASTRO CALCULATIONS ------------------

def get_zodiac_sign_from_degree(deg):
    signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    return signs[int(deg // 30)]

def degree_to_house_whole_sign(planet_deg, asc_deg):
    return int(((planet_deg - asc_deg) % 360) // 30) + 1

def calculate_chart(lat, lon, date_str, time_str, timezone_str):
    """
    Universal function to calculate any chart (Birth or Transit)
    date_str: 'YYYY-MM-DD', time_str: 'HH:MM'
    """
    local_tz = pytz.timezone(timezone_str)
    dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_local = local_tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }

    planets = {}
    for name, pid in planet_ids.items():
        res, _ = swe.calc_ut(jd, pid)
        deg = res[0] % 360
        planets[name] = {"degree": round(deg, 2), "sign": get_zodiac_sign_from_degree(deg)}

    # Add Ketu (Exactly 180 degrees from Rahu)
    rahu_deg = planets["Rahu"]["degree"]
    ketu_deg = (rahu_deg + 180) % 360
    planets["Ketu"] = {"degree": round(ketu_deg, 2), "sign": get_zodiac_sign_from_degree(ketu_deg)}

    # Calculate Ascendant
    res_houses = swe.houses(jd, lat, lon)
    asc_deg = res_houses[0][0]
    asc_sign = get_zodiac_sign_from_degree(asc_deg)

    # Assign Houses (Whole Sign System)
    for name, pdata in planets.items():
        pdata["house"] = degree_to_house_whole_sign(pdata["degree"], asc_deg)

    return {
        "ascendant": asc_sign,
        "asc_degree": round(asc_deg, 2),
        "planets": planets
    }

# ------------------ TRANSIT LOGIC ------------------

def get_current_transit_chart(lat, lon, timezone_str, user_current_iso_time=None):
    """
    Calculates where planets are RIGHT NOW in the user's local sky.
    user_current_iso_time: ISO string from frontend (e.g., '2025-06-25T22:10:00')
    """
    if user_current_iso_time:
        # Use exact time from user's device
        dt_obj = datetime.fromisoformat(user_current_iso_time)
    else:
        # Fallback to current server time if frontend doesn't provide it
        dt_obj = datetime.now(pytz.timezone(timezone_str))
        
    date_str = dt_obj.strftime("%Y-%m-%d")
    time_str = dt_obj.strftime("%H:%M")
    
    return calculate_chart(lat, lon, date_str, time_str, timezone_str)

# ------------------ ADVANCED SUMMARIZER ------------------

def summarize_chart_with_transits(natal_chart: dict, transit_chart: dict = None) -> str:
    """
    Combines Birth Chart and Current Transit for a powerful LLM insight.
    """
    n_asc = natal_chart["ascendant"]
    n_planets = natal_chart["planets"]

    summary = (
        f"USER NATAL CHART -> Ascendant: {n_asc}. "
        f"Sun: {n_planets['Sun']['sign']}, Moon: {n_planets['Moon']['sign']}, "
        f"Mars: {n_planets['Mars']['sign']}, Venus: {n_planets['Venus']['sign']}. "
    )

    if transit_chart:
        t_planets = transit_chart["planets"]
        summary += (
            f"\nCURRENT TRANSITS (SKY TODAY) -> "
            f"Moon: {t_planets['Moon']['sign']}, Mars: {t_planets['Mars']['sign']}, "
            f"Rahu: {t_planets['Rahu']['sign']}, Saturn: {t_planets['Saturn']['sign']}. "
            f"Instruction: Check if current Mars or Rahu is clashing with natal Moon or 7th house."
        )

    return summary