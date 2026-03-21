COLORS = {
    "primary":    "#0A2342",
    "accent":     "#C9A84C",
    "gain":       "#1A7F4B",
    "loss":       "#B02020",
    "neutral":    "#5C7A99",
    "background": "#F4F6F9",
}

DIVERGING_SCALE = ["#B02020", "#E07070", "#CCCCCC", "#70C070", "#1A7F4B"]

IQRI_COLORS = {
    "Wage-Dependent":   "#B02020",
    "Mixed":            "#C9A84C",
    "Entrepreneurial":  "#5C7A99",
    "Investment-Led":   "#0A2342",
}

# Trend line colors per year
YEAR_COLORS = {
    2018: "#E07070",
    2019: "#C9A84C",
    2020: "#5C7A99",
    2021: "#70C070",
    2022: "#0A2342",
}

AGI_STUB_LABELS = {
    1: "Under $25K",
    2: "$25K–$50K",
    3: "$50K–$75K",
    4: "$75K–$100K",
    5: "$100K–$200K",
    6: "$200K+",
}

# Five-year window: 2018–2022
ANALYSIS_YEARS = [2018, 2019, 2020, 2021, 2022]
BASELINE_YEAR = 2018
LATEST_YEAR = 2022

IRS_URLS = {year: f"https://www.irs.gov/pub/irs-soi/{str(year)[2:]}zpallagi.csv"
            for year in ANALYSIS_YEARS}

LOAD_COLS = ["STATE", "zipcode", "agi_stub", "N1",
             "A00100", "A00200", "A00600", "A00900"]
