import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Team 15 Environmental Justice Dashboard",
    page_icon="🌎",
    layout="wide",
)

st.markdown(
    """
    <h1 style='text-align: center; color: #00c8ff;'>
        Team 15 Environmental Justice Dashboard
    </h1>
    <p style='text-align: center; color: #d9d9d9; font-size: 18px;'>
        Interactive Analysis of the EJI 2024 New Mexico Dataset
    </p>
    <br>
    """,
    unsafe_allow_html=True
)
# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data(uploaded_file=None, default_path="datasets/EJI_2024_New_Mexico_CLEAN.csv"):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_csv(default_path)


st.sidebar.header("Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload cleaned CSV (optional)",
    type=["csv"],
    help="If you don't upload anything, the app will try to use 'EJI_2024_New_Mexico_CLEAN.csv' in this folder."
)

data = None
data_load_error = None

try:
    data = load_data(uploaded_file)
except Exception as e:
    data_load_error = str(e)

if data is None:
    st.error(
        "❌ Could not load data.\n\n"
        "Make sure you either:\n"
        "- Upload a cleaned CSV file in the sidebar, **or**\n"
        "- Have a file named `EJI_2024_New_Mexico_CLEAN.csv` in the same folder as `app.py`."
    )
    if data_load_error:
        with st.expander("Show error details"):
            st.code(data_load_error)
    st.stop()

# -----------------------------
# Abbreviation definitions dictionary
# -----------------------------
st.header("📘 Indicator Definitions")

# ---- 1. Base definitions for key columns that actually exist in your file ----
base_definitions = {
    # GEO / ID
    "STATEFP": "State FIPS code (2-digit code identifying the state).",
    "COUNTYFP": "County FIPS code (3-digit code identifying the county).",
    "TRACTCE": "Census tract code (6-digit identifier within the county).",
    "AFFGEOID": "Full Census geographic identifier used by the Census API.",
    "GEOID": "Full Census tract ID (STATEFP + COUNTYFP + TRACTCE).",
    "GEOID_2020": "2020 full Census tract ID.",
    "COUNTY": "County name.",
    "StateDesc": "State name (New Mexico).",
    "STATEABBR": "State abbreviation (NM).",
    "LOCATION": "Text description of the census tract location.",

    # Core EJI / domain scores
    "SPL_EJI": "State percentile ranking for the overall Environmental Justice Index (higher = more burdened).",
    "RPL_EJI": "National percentile ranking for the overall Environmental Justice Index (higher = more burdened).",
    "SPL_SER": "State percentile ranking for combined social and environmental risk.",
    "SPL_EJI_CBM": "State percentile for cumulative EJ burden (combined).",
    "RPL_EJI_CBM": "National percentile for cumulative EJ burden (combined).",

    # Social Vulnerability Metrics (SVM) domains
    "SPL_SVM": "State percentile for overall social vulnerability metrics domain.",
    "RPL_SVM": "National percentile for overall social vulnerability metrics domain.",
    "SPL_SVM_DOM1": "State percentile for Social Vulnerability Domain 1 (e.g., socioeconomic).",
    "SPL_SVM_DOM2": "State percentile for Social Vulnerability Domain 2 (e.g., household composition).",
    "SPL_SVM_DOM3": "State percentile for Social Vulnerability Domain 3 (e.g., minority status & language).",
    "SPL_SVM_DOM4": "State percentile for Social Vulnerability Domain 4 (e.g., housing & transportation).",

    # Environmental Burden Metrics (EBM) domains
    "SPL_EBM": "State percentile for overall environmental burden metrics domain.",
    "RPL_EBM": "National percentile for overall environmental burden metrics domain.",
    "SPL_EBM_DOM1": "State percentile for Environmental Domain 1 (e.g., air pollution).",
    "SPL_EBM_DOM2": "State percentile for Environmental Domain 2 (e.g., water or waste facilities).",
    "SPL_EBM_DOM3": "State percentile for Environmental Domain 3.",
    "SPL_EBM_DOM4": "State percentile for Environmental Domain 4.",
    "SPL_EBM_DOM5": "State percentile for Environmental Domain 5.",

    # Cumulative Burden Metrics (CBM) domains
    "SPL_CBM": "State percentile for overall cumulative burden metrics domain.",
    "RPL_CBM": "National percentile for overall cumulative burden metrics domain.",
    "SPL_CBM_DOM1": "State percentile for Cumulative Burden Domain 1.",
    "SPL_CBM_DOM2": "State percentile for Cumulative Burden Domain 2.",
    "SPL_CBM_DOM3": "State percentile for Cumulative Burden Domain 3.",
    "RPL_CBM_DOM1": "National percentile for Cumulative Burden Domain 1.",
    "RPL_CBM_DOM2": "National percentile for Cumulative Burden Domain 2.",
    "RPL_CBM_DOM3": "National percentile for Cumulative Burden Domain 3.",

    # Population counts
    "E_TOTPOP": "Estimated total population of the census tract.",
    "M_TOTPOP": "Margin of error for total population.",
    "E_DAYPOP": "Estimated daytime population (people present during the day).",

    # Social indicators
    "E_MINRTY": "Estimated number of minority (non-white) residents.",
    "EPL_MINRTY": "Percentile rank of minority population proportion (0–1 scale).",
    "E_POV200": "Estimated number of people at or below 200% of the poverty level.",
    "EPL_POV200": "Percentile rank of population at/under 200% poverty.",
    "E_NOHSDP": "Estimated number of adults (25+) without a high school diploma.",
    "EPL_NOHSDP": "Percentile rank for low educational attainment.",
    "E_UNEMP": "Estimated number of unemployed individuals (16+ in labor force).",
    "EPL_UNEMP": "Percentile rank for unemployment.",
    "E_RENTER": "Estimated number of renter-occupied housing units.",
    "EPL_RENTER": "Percentile rank for renter housing.",
    "E_HOUBDN": "Estimated number of households severely burdened by housing costs.",
    "EPL_HOUBDN": "Percentile rank for housing cost burden.",
    "E_UNINSUR": "Estimated number of people without health insurance.",
    "EPL_UNINSUR": "Percentile rank for lack of health insurance.",
    "E_NOINT": "Estimated number of households without internet access.",
    "EPL_NOINT": "Percentile rank for lack of internet access.",
    "E_AGE65": "Estimated number of people age 65 or older.",
    "EPL_AGE65": "Percentile rank for older adult population.",
    "E_AGE17": "Estimated number of people age 17 or younger.",
    "EPL_AGE17": "Percentile rank for child/youth population.",
    "E_DISABL": "Estimated number of people with a disability.",
    "EPL_DISABL": "Percentile rank for disability prevalence.",
    "E_LIMENG": "Estimated number of people who speak English less than 'very well'.",
    "EPL_LIMENG": "Percentile rank for limited English proficiency.",
    "E_MOBILE": "Estimated number of people living in mobile homes.",
    "EPL_MOBILE": "Percentile rank for mobile home housing.",
    "E_GROUPQ": "Estimated number of people in group quarters (e.g., dorms, prisons).",
    "EPL_GROUPQ": "Percentile rank for group quarters population.",

    # Race/ethnicity counts
    "AFAM": "Percent of population that is African American.",
    "E_AFAM": "Estimated number of African American residents.",
    "HISP": "Percent of population that is Hispanic/Latino.",
    "E_HISP": "Estimated number of Hispanic/Latino residents.",
    "ASIAN": "Percent of population that is Asian.",
    "E_ASIAN": "Estimated number of Asian residents.",
    "AIAN": "Percent of population that is American Indian/Alaska Native.",
    "E_AIAN": "Estimated number of American Indian/Alaska Native residents.",
    "NHPI": "Percent of population that is Native Hawaiian or Pacific Islander.",
    "E_NHPI": "Estimated number of Native Hawaiian/Pacific Islander residents.",
    "TWOMORE": "Percent of population identifying with two or more races.",
    "E_TWOMORE": "Estimated number of residents of two or more races.",
    "OTHERRACE": "Percent of population identifying as some other race.",
    "E_OTHERRACE": "Estimated number of residents of some other race.",

    # Tribal info
    "Tribe_PCT_Tract": "Percent of the tract area overlapping tribal lands.",
    "Tribe_Names": "Names of tribes associated with lands in or near the tract.",
    "Tribe_Flag": "Indicates whether the tract overlaps or is associated with tribal areas (1 = yes).",
}

# ---- 2. Pattern-based suffix meanings ----
suffix_descriptions = {
    "MINRTY": "minority population (non-white).",
    "POV200": "population at or below 200% of the poverty level.",
    "NOHSDP": "adults without a high school diploma.",
    "UNEMP": "unemployed individuals (16+ in the labor force).",
    "RENTER": "renter-occupied housing units.",
    "HOUBDN": "households with severe housing cost burden.",
    "UNINSUR": "people without health insurance.",
    "NOINT": "households without internet access.",
    "MOBILE": "people living in mobile homes.",
    "GROUPQ": "people living in group quarters.",
    "AGE65": "people age 65 or older.",
    "AGE17": "people age 17 or younger.",
    "DISABL": "people with a disability.",
    "LIMENG": "people who speak English less than very well.",
    "RFLD": "residential flooding risk.",
    "SWND": "strong wind hazard risk.",
    "TRND": "tornado hazard risk.",
    "ASTHMA": "asthma-related health burden.",
    "CANCER": "cancer-related health burden.",
    "CHD": "coronary heart disease burden.",
    "MHLTH": "mental health-related burden.",
    "DIABETES": "diabetes-related health burden.",
}

def get_indicator_definition(col: str) -> str:
    # 1. Exact match
    if col in base_definitions:
        return base_definitions[col]

    # 2. Prefix-based patterns
    prefixes = ["EPL_", "E_", "RPL_", "F_", "SPL_"]
    for prefix in prefixes:
        if col.startswith(prefix):
            suffix = col[len(prefix):]
            base_text = suffix_descriptions.get(suffix, suffix)
            if prefix == "E_":
                return f"Estimated count related to {base_text}"
            if prefix == "EPL_":
                return f"Percentile rank (0–1) for {base_text}"
            if prefix == "RPL_":
                return f"National percentile rank for {base_text}"
            if prefix == "F_":
                return f"Flag/reliability indicator for {base_text}"
            if prefix == "SPL_":
                return f"State percentile rank for {base_text}"

    # 3. Fallback
    return "Not yet defined (dataset-specific indicator)."

# ---- 3. Build and display definitions table for ALL columns ----

st.subheader("All Columns with Definitions")

# assuming your DataFrame is named `data`
col_list = list(data.columns)
rows = []

for col in col_list:
    rows.append({
        "Column Name": col,
        "Definition": get_indicator_definition(col)
    })

st.dataframe(pd.DataFrame(rows))

# -----------------------------
# Dataset overview
# -----------------------------
st.subheader("Dataset Overview")

st.write(f"**Rows:** {data.shape[0]} &nbsp;&nbsp; | &nbsp;&nbsp; **Columns:** {data.shape[1]}")
st.dataframe(data.head(), use_container_width=True)

with st.expander("Show summary statistics"):
    st.write("### Numeric Columns Summary")
    st.write(data.describe())

# --- Column info with definitions ---
with st.expander("Show column info with definitions"):
    col_info = pd.DataFrame({
        "Column": data.columns,
        "Data Type": [str(dtype) for dtype in data.dtypes],
        "Definition": [ABBREV_DEFS.get(col, "—") for col in data.columns]
    })
    st.table(col_info)

# --- Abbreviation reference section ---
st.subheader("Abbreviation Reference Guide")
st.write(
    "Some column names use abbreviations. Use this guide to understand what they mean."
)

with st.expander("Show abbreviation definitions"):
    for key, value in ABBREV_DEFS.items():
        st.markdown(f"**{key}** — {value}")

# -----------------------------
# Sidebar controls for plotting
# -----------------------------
st.sidebar.header("Plot Settings")

all_cols = data.columns.tolist()

plot_type = st.sidebar.selectbox(
    "Plot type",
    ["Line", "Scatter", "Bar", "Histogram", "Box"]
)

x_col = st.sidebar.selectbox(
    "X-axis",
    options=all_cols,
    index=0 if len(all_cols) > 0 else None
)

y_col = None
if plot_type in ["Line", "Scatter", "Bar", "Box"]:
    possible_y_cols = [c for c in all_cols if c != x_col]
    if possible_y_cols:
        y_col = st.sidebar.selectbox(
            "Y-axis",
            options=possible_y_cols,
            index=0
        )

color_col = st.sidebar.selectbox(
    "Color (optional)",
    options=["None"] + all_cols,
    index=0
)
if color_col == "None":
    color_col = None

# -----------------------------
# Optional filtering
# -----------------------------
st.sidebar.header("Filter Data (Optional)")
filter_col = st.sidebar.selectbox(
    "Column to filter on",
    options=["None"] + all_cols,
    index=0
)

filtered_data = data.copy()

if filter_col != "None":
    if pd.api.types.is_numeric_dtype(filtered_data[filter_col]):
        min_val = float(filtered_data[filter_col].min())
        max_val = float(filtered_data[filter_col].max())
        selected_range = st.sidebar.slider(
            f"Range for {filter_col}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        filtered_data = filtered_data[
            (filtered_data[filter_col] >= selected_range[0]) &
            (filtered_data[filter_col] <= selected_range[1])
        ]
    else:
        unique_vals = sorted(filtered_data[filter_col].dropna().unique().tolist())
        if len(unique_vals) > 50:
            st.sidebar.info(
                f"{filter_col} has many unique values ({len(unique_vals)}). "
                "You can still select a subset below."
            )
        selected_vals = st.sidebar.multiselect(
            f"Values for {filter_col}",
            options=unique_vals,
            default=unique_vals
        )
        filtered_data = filtered_data[filtered_data[filter_col].isin(selected_vals)]

# -----------------------------
# Plot section
# -----------------------------
st.subheader("Interactive Visualization")

if filtered_data.empty:
    st.warning("No data left after filtering. Adjust filters in the sidebar.")
else:
    fig = None

    if plot_type == "Line":
        if y_col is None:
            st.error("Please select a Y-axis column in the sidebar.")
        else:
            fig = px.line(
                filtered_data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{plot_type} Plot: {y_col} vs {x_col}"
            )

    elif plot_type == "Scatter":
        if y_col is None:
            st.error("Please select a Y-axis column in the sidebar.")
        else:
            fig = px.scatter(
                filtered_data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{plot_type} Plot: {y_col} vs {x_col}",
                hover_data=all_cols
            )

    elif plot_type == "Bar":
        if y_col is None:
            st.error("Please select a Y-axis column in the sidebar.")
        else:
            fig = px.bar(
                filtered_data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{plot_type} Plot: {y_col} vs {x_col}"
            )

    elif plot_type == "Histogram":
        fig = px.histogram(
            filtered_data,
            x=x_col,
            color=color_col,
            nbins=30,
            title=f"{plot_type} of {x_col}"
        )

    elif plot_type == "Box":
        fig = px.box(
            filtered_data,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"{plot_type} Plot"
        )

    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# MATLAB cleaning code display
# -----------------------------
st.subheader("MATLAB Cleaning Code Used")

st.write(
    """
    Below is the MATLAB script that was used to clean the **EJI 2024 New Mexico** dataset
    before loading it into this Streamlit app.
    """
)

matlab_code = """%% Clean the EJI 2024 New Mexico dataset
% David Jaramillo

% ---- Step 1: Load dataset ----
infile = 'EJI_2024_New_Mexico.csv';
outfile = 'EJI_2024_New_Mexico_CLEAN.csv';

fprintf('Loading %s...\\n', infile);
T = readtable(infile);

% ---- Step 2: Standardize missing entries ----
T = standardizeMissing(T, {"", "NA", "N/A", "NaN", "null", -999, -9999});

% ---- Step 3: Remove duplicate rows ----
T = unique(T);

% ---- Step 4: Convert numeric-looking text columns to numbers ----
for i = 1:width(T)
    col = T.(i);
    if iscell(col) || isstring(col)
        numCol = str2double(string(col));
        % Replace column if >50% numeric values
        if sum(~isnan(numCol)) > 0.5 * height(T)
            T.(i) = numCol;
        end
    end
end

% ---- Step 5: Fill missing numeric data with column means ----
for i = 1:width(T)
    if isnumeric(T.(i))
        T.(i) = fillmissing(T.(i), 'constant', mean(T.(i), 'omitnan'));
    end
end

% ---- Step 6: Display summary ----
disp('✅ Cleaned dataset preview:');
disp(T(1:10, :));
summary(T);

% ---- Step 7: Save cleaned data ----
writetable(T, outfile);
fprintf('Cleaned data saved as %s\\n', outfile);
"""

with st.expander("Show MATLAB code"):
    st.code(matlab_code, language="matlab")






