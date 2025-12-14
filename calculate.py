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

def calculate_chart(lat, lon, dob, tob, timezone_str):
    """Returns full chart JSON"""
    # Convert to UTC
    local_tz = pytz.timezone(timezone_str)
    dt_local = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    dt_local = local_tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
    hour_decimal = dt_utc.hour + dt_utc.minute / 60

    jd = swe.julday(year, month, day, hour_decimal)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }

    planets = {}
    for name, pid in planet_ids.items():
        res, ret = swe.calc_ut(jd, pid)
        deg = res[0] % 360   # first element is the longitude in degrees
        planets[name] = {"degree": round(deg, 2), "sign": get_zodiac_sign_from_degree(deg)}

    # Add Ketu
    rahu_deg = planets["Rahu"]["degree"]
    ketu_deg = (rahu_deg + 180) % 360
    planets["Ketu"] = {"degree": round(ketu_deg, 2), "sign": get_zodiac_sign_from_degree(ketu_deg)}

    asc_deg = swe.houses(jd, lat, lon)[0][0]
    asc_sign = get_zodiac_sign_from_degree(asc_deg)

    # Whole sign houses
    for name, pdata in planets.items():
        pdata["house"] = degree_to_house_whole_sign(pdata["degree"], asc_deg)

    chart_json = {
        "latitude": lat,
        "longitude": lon,
        "timezone": timezone_str,
        "ascendant": asc_sign,
        "planets": planets
    }

    return chart_json

# ------------------ CHART SUMMARIZER ------------------

def summarize_chart(chart_json: dict) -> str:
    """Convert full chart to key insights for LLM"""
    asc = chart_json["ascendant"]
    planets = chart_json["planets"]

    dominant = max(planets.items(), key=lambda x: x[1]["house"])[0]

    summary = (
        f"Ascendant: {asc}. "
        f"Sun in {planets['Sun']['sign']}, Moon in {planets['Moon']['sign']}. "
        f"Dominant planet: {dominant}. "
        f"Current focus: life path and personal growth."
    )

    return summary
