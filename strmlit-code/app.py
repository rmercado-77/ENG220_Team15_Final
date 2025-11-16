import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="EJI 2024 New Mexico – Clean Data Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 EJI 2024 New Mexico – Clean Dataset Dashboard")
st.write(
    """
    This app displays the cleaned **EJI 2024 New Mexico** dataset and provides an 
    interactive dashboard for visual exploration. The dataset was cleaned in MATLAB
    and saved as `EJI_2024_New_Mexico_CLEAN.csv`.
    """
)

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data(uploaded_file=None, default_path="EJI_2024_New_Mexico_CLEAN.csv"):
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
ABBREV_DEFS = {
    "STATEFP": "State FIPS Code — standardized code identifying each U.S. state.",
    "COUNTYFP": "County FIPS Code — standardized 3-digit identifier for each county.",
    "TRACTCE": "Census Tract Code — identifies a specific census tract within a county.",
    "GEOID": "Geographic Identifier — unique ID combining state, county, and tract.",
    "NAME": "Name of the geographic area (e.g., census tract name).",
    "ALAND": "Land area in square meters.",
    "AWATER": "Water area in square meters.",
    "INTPTLAT": "Latitude of an internal reference point (centroid) for the area.",
    "INTPTLONG": "Longitude of an internal reference point (centroid) for the area.",
    # Add more here if your dataset has additional abbreviations:
    # "VAR_NAME": "Explanation ..."
}

# -----------------------------
# Dataset overview
# -----------------------------
st.subheader("📁 Dataset Overview")

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
st.subheader("📘 Abbreviation Reference Guide")
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
st.subheader("📈 Interactive Visualization")

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
st.subheader("🧮 MATLAB Cleaning Code Used")

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
