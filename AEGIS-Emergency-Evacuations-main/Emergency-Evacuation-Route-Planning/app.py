from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from graph import load_building_map
from dijkstra import dijkstra, build_path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AEGIS | Emergency Route Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# FUTURISTIC THEME
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 15% 0%,
                rgba(124, 58, 237, 0.16),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(6, 182, 212, 0.10),
                transparent 28%
            ),
            #050711;
        color: #E8ECF8;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.3rem;
        padding-bottom: 2rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #080A14,
                #090B18
            );
        border-right: 1px solid #1D2338;
    }

    section[data-testid="stSidebar"] * {
        color: #E7EAF4;
    }

    .stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 10px;
        border: 1px solid rgba(139, 92, 246, 0.65);
        background:
            linear-gradient(
                100deg,
                #6D28D9,
                #7C3AED 55%,
                #0891B2
            );
        color: white;
        font-weight: 800;
        letter-spacing: 0.035em;
        box-shadow:
            0 0 24px rgba(124, 58, 237, 0.20);
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow:
            0 0 34px rgba(34, 211, 238, 0.24);
    }

    div[data-baseweb="select"] > div {
        background: #0D1020;
        border: 1px solid #252C46;
        border-radius: 9px;
    }

    div[data-baseweb="select"] span {
        color: #E7EAF4;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(15, 19, 35, 0.96),
                rgba(9, 12, 24, 0.96)
            );
        border: 1px solid #222943;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        box-shadow:
            0 10px 35px rgba(0, 0, 0, 0.20);
    }

    div[data-testid="stMetricLabel"] {
        color: #747D9C;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
    }

    div[data-testid="stMetricValue"] {
        color: #F4F6FF;
        font-weight: 750;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
        border: 1px solid #282E47;
    }

    h1,
    h2,
    h3 {
        color: #F4F6FF;
        letter-spacing: -0.025em;
    }

    hr {
        border-color: #1D2338;
    }

    .stCaption {
        color: #707994;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD BUILDING DATA
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

graph, locations, exits = load_building_map(
    BASE_DIR / "data" / "building_map.json"
)


# =========================================================
# SESSION STATE
# =========================================================

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "recommended" not in st.session_state:
    st.session_state.recommended = None

if "available_routes" not in st.session_state:
    st.session_state.available_routes = []

if "distances" not in st.session_state:
    st.session_state.distances = None

if "previous" not in st.session_state:
    st.session_state.previous = None

if "simulation_done" not in st.session_state:
    st.session_state.simulation_done = False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:1.55rem;
            font-weight:800;
            letter-spacing:0.08em;
            color:#F4F6FF;
        ">
            ◈ AEGIS
        </div>

        <div style="
            margin-top:4px;
            font-size:0.66rem;
            letter-spacing:0.20em;
            color:#697391;
        ">
            EMERGENCY ROUTE INTELLIGENCE
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### SCENARIO")

    location_codes = list(locations.keys())

    default_index = (
        location_codes.index("G3")
        if "G3" in location_codes
        else 0
    )

    start = st.selectbox(
        "Starting Location",
        location_codes,
        index=default_index,
        format_func=lambda code: locations[code],
        key="starting_location"
    )

    emergency_type = st.selectbox(
        "Emergency Type",
        [
            "Fire",
            "Earthquake",
            "Gas Leak",
            "General Emergency"
        ],
        key="emergency_type"
    )

    st.markdown("### NETWORK CONDITIONS")

    blocked_options = []

    for source in graph:

        for destination, distance in graph[source]:

            if source < destination:

                blocked_options.append(
                    (
                        source,
                        destination,
                        f"{locations[source]} → "
                        f"{locations[destination]}"
                    )
                )

    blocked_labels = [
        item[2]
        for item in blocked_options
    ]

    selected_blocked = st.multiselect(
        "Unavailable Connections",
        blocked_labels,
        help=(
            "Select building connections that "
            "are currently blocked."
        ),
        key="blocked_connections"
    )

    blocked_edges = set()

    for source, destination, label in blocked_options:

        if label in selected_blocked:

            blocked_edges.add(
                frozenset(
                    [source, destination]
                )
            )

    # During the live demonstration, automatically
    # simulate Staircase A -> Exit A becoming blocked.
    if st.session_state.simulation_done:

        blocked_edges = {
            frozenset(["G5", "G6"])
        }

    st.divider()

    analyze = st.button(
        "◈  RUN EVACUATION ANALYSIS",
        key="analyze_button"
    )

    st.markdown(
        "<div style='height:8px'></div>",
        unsafe_allow_html=True
    )

    simulate = st.button(
        "▶  RUN LIVE EMERGENCY DEMO",
        key="simulation_button"
    )

    st.divider()

    st.caption("SYSTEM CORE")

    st.write("● ROUTING ENGINE  —  ONLINE")
    st.write("● GRAPH ENGINE    —  ONLINE")
    st.write("● DIJKSTRA CORE   —  READY")
    st.write("● NETWORK MODE    —  DYNAMIC")


# =========================================================
# MANUAL ANALYSIS
# =========================================================

if analyze:

    # Manual analysis cancels simulation mode.
    st.session_state.simulation_done = False

    distances, previous = dijkstra(
        graph,
        start,
        blocked_edges
    )

    available_routes = []

    for exit_location in exits:

        path = build_path(
            previous,
            start,
            exit_location
        )

        if path:

            available_routes.append(
                {
                    "exit": exit_location,
                    "path": path,
                    "distance": distances[exit_location]
                }
            )

    recommended = None

    if available_routes:

        recommended = min(
            available_routes,
            key=lambda route: route["distance"]
        )

    st.session_state.analysis_done = True
    st.session_state.recommended = recommended
    st.session_state.available_routes = available_routes
    st.session_state.distances = distances
    st.session_state.previous = previous


# =========================================================
# LIVE EMERGENCY SIMULATION
# =========================================================

if simulate:

    import time

    # Fixed demonstration starting point:
    # Room 101 = G3
    demo_start = "G3"

    # Staircase A -> Exit A
    demo_blocked = {
        frozenset(["G5", "G6"])
    }

    st.session_state.simulation_done = True
    st.session_state.analysis_done = False
    st.session_state.recommended = None
    st.session_state.available_routes = []

    simulation_box = st.empty()

    # -----------------------------------------------------
    # STEP 1
    # -----------------------------------------------------

    simulation_box.info(
        "🟢 LIVE SIMULATION • "
        "NORMAL EVACUATION NETWORK"
    )

    time.sleep(1.5)

    # -----------------------------------------------------
    # STEP 2
    # -----------------------------------------------------

    simulation_box.warning(
        "⚠️ HAZARD DETECTED • "
        "STAIRCASE A → EXIT A IS NOW BLOCKED"
    )

    time.sleep(1.5)

    # -----------------------------------------------------
    # STEP 3
    # -----------------------------------------------------

    simulation_box.info(
        "⚡ AEGIS IS RECALCULATING THE "
        "EVACUATION NETWORK..."
    )

    time.sleep(1.5)

    # -----------------------------------------------------
    # RUN DIJKSTRA
    # -----------------------------------------------------

    distances, previous = dijkstra(
        graph,
        demo_start,
        demo_blocked
    )

    available_routes = []

    for exit_location in exits:

        path = build_path(
            previous,
            demo_start,
            exit_location
        )

        if path:

            available_routes.append(
                {
                    "exit": exit_location,
                    "path": path,
                    "distance": distances[exit_location]
                }
            )

    recommended = None

    if available_routes:

        recommended = min(
            available_routes,
            key=lambda route: route["distance"]
        )

    # -----------------------------------------------------
    # STORE RESULT
    # -----------------------------------------------------

    st.session_state.analysis_done = True
    st.session_state.recommended = recommended
    st.session_state.available_routes = available_routes
    st.session_state.distances = distances
    st.session_state.previous = previous

    # -----------------------------------------------------
    # FINAL MESSAGE
    # -----------------------------------------------------

    simulation_box.success(
        "✓ ROUTE RECALCULATED • "
        "ALTERNATIVE EVACUATION PATH FOUND"
    )


# =========================================================
# RETRIEVE RESULTS
# =========================================================

recommended = st.session_state.recommended

available_routes = (
    st.session_state.available_routes
)

distances = st.session_state.distances

previous = st.session_state.previous


# =========================================================
# DISPLAY START LOCATION
# =========================================================

display_start = (
    "G3"
    if st.session_state.simulation_done
    else start
)


# =========================================================
# TOP BAR
# =========================================================

top1, top2 = st.columns([5.5, 1.2])

with top1:

    st.markdown(
        """
        <div style="
            font-size:2.65rem;
            font-weight:850;
            letter-spacing:-0.055em;
            line-height:1.05;
            color:#F5F7FF;
        ">
            AEGIS
            <span style="
                color:#8B5CF6;
            ">
                //
            </span>
            Emergency Intelligence
        </div>

        <div style="
            margin-top:8px;
            color:#727B99;
            font-size:0.72rem;
            letter-spacing:0.18em;
        ">
            REAL-TIME EVACUATION ROUTE OPTIMIZATION
        </div>
        """,
        unsafe_allow_html=True
    )

with top2:

    st.metric(
        "SYSTEM",
        "● LIVE"
    )


st.divider()


# =========================================================
# COMPACT STATUS BAR
# =========================================================

s1, s2, s3, s4 = st.columns(4)

with s1:

    st.metric(
        "EMERGENCY",
        emergency_type.upper()
    )

with s2:

    st.metric(
        "START",
        locations[display_start].upper()
    )

with s3:

    st.metric(
        "BLOCKED",
        len(blocked_edges)
    )

with s4:

    if recommended:

        st.metric(
            "EXIT",
            locations[
                recommended["exit"]
            ].upper()
        )

    else:

        st.metric(
            "EXIT",
            "WAITING"
        )


# =========================================================
# NETWORK MAP
# =========================================================

st.markdown("### LIVE BUILDING NETWORK")


# =========================================================
# GRAPH COORDINATES
# =========================================================

coords = {

    "G1": (100, 280),

    "G2": (280, 280),

    "G3": (455, 130),

    "G4": (455, 390),

    "G5": (650, 390),

    "G6": (850, 280),

    "F4": (850, 510),

    "F1": (650, 620),

    "F2": (1050, 510),

    "F3": (1240, 620),

    "F5": (1240, 280)
}


# =========================================================
# CREATE SVG EDGES
# =========================================================

svg_edges = ""

for source in graph:

    for destination, distance in graph[source]:

        if source >= destination:
            continue

        x1, y1 = coords[source]
        x2, y2 = coords[destination]

        edge = frozenset(
            [source, destination]
        )

        # -------------------------------------------------
        # BLOCKED EDGE
        # -------------------------------------------------

        if edge in blocked_edges:

            svg_edges += f"""
            <line
                x1="{x1}"
                y1="{y1}"
                x2="{x2}"
                y2="{y2}"
                class="blocked"
            />

            <circle
                cx="{(x1 + x2) / 2}"
                cy="{(y1 + y2) / 2}"
                r="7"
                class="hazard"
            />
            """

            continue

        # -------------------------------------------------
        # CHECK RECOMMENDED ROUTE
        # -------------------------------------------------

        is_route = False

        if recommended:

            route = recommended["path"]

            for i in range(len(route) - 1):

                route_edge = frozenset(
                    [
                        route[i],
                        route[i + 1]
                    ]
                )

                if edge == route_edge:

                    is_route = True
                    break

        # -------------------------------------------------
        # ACTIVE ROUTE
        # -------------------------------------------------

        if is_route:

            svg_edges += f"""
            <line
                x1="{x1}"
                y1="{y1}"
                x2="{x2}"
                y2="{y2}"
                class="route-glow"
            />

            <line
                x1="{x1}"
                y1="{y1}"
                x2="{x2}"
                y2="{y2}"
                class="route"
            />
            """

        else:

            svg_edges += f"""
            <line
                x1="{x1}"
                y1="{y1}"
                x2="{x2}"
                y2="{y2}"
                class="connection"
            />
            """


# =========================================================
# CREATE SVG NODES
# =========================================================

svg_nodes = ""

for code, name in locations.items():

    x, y = coords[code]

    # Starting point
    if code == display_start:

        node_class = "start"

    # Recommended exit
    elif (
        recommended
        and code == recommended["exit"]
    ):

        node_class = "target"

    # Other exit
    elif code in exits:

        node_class = "exit"

    # Normal
    else:

        node_class = "normal"

    svg_nodes += f"""
    <g>

        <circle
            cx="{x}"
            cy="{y}"
            r="25"
            class="{node_class}"
        />

        <circle
            cx="{x}"
            cy="{y}"
            r="5"
            class="core"
        />

        <text
            x="{x}"
            y="{y + 47}"
            class="code"
        >
            {code}
        </text>

        <text
            x="{x}"
            y="{y + 63}"
            class="name"
        >
            {name.upper()}
        </text>

    </g>
    """


# =========================================================
# SVG MAP
# =========================================================

svg = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

html,
body {{
    margin:0;
    padding:0;
    background:#050711;
}}

.map {{
    width:100%;
    height:650px;
    border-radius:16px;
    overflow:hidden;
    border:1px solid #242B45;

    background:
        radial-gradient(
            circle at 50% 45%,
            rgba(124,58,237,0.10),
            transparent 43%
        ),
        #070A16;

    box-shadow:
        inset 0 0 90px rgba(0,0,0,0.45),
        0 15px 45px rgba(0,0,0,0.25);
}}

svg {{
    width:100%;
    height:100%;
}}


/* ===================================
   GRID
   =================================== */

.grid {{
    stroke:#13182A;
    stroke-width:1;
    opacity:0.9;
}}


/* ===================================
   NORMAL CONNECTION
   =================================== */

.connection {{
    stroke:#343D5B;
    stroke-width:3;
    opacity:0.9;
}}


/* ===================================
   ROUTE GLOW
   =================================== */

.route-glow {{
    stroke:#22D3A3;
    stroke-width:16;
    opacity:0.16;

    filter:
        blur(6px);
}}


/* ===================================
   ACTIVE ROUTE
   =================================== */

.route {{
    stroke:#22D3A3;
    stroke-width:6;
    stroke-linecap:round;

    stroke-dasharray:18 12;

    filter:
        drop-shadow(
            0 0 7px
            rgba(34,211,163,0.95)
        );

    animation:
        routeFlow 1.1s linear infinite;
}}

@keyframes routeFlow {{

    to {{
        stroke-dashoffset:-30;
    }}

}}


/* ===================================
   BLOCKED
   =================================== */

.blocked {{
    stroke:#F43F5E;
    stroke-width:7;

    stroke-dasharray:11 9;

    filter:
        drop-shadow(
            0 0 7px
            rgba(244,63,94,0.85)
        );
}}

.hazard {{
    fill:#F43F5E;

    filter:
        drop-shadow(
            0 0 9px
            rgba(244,63,94,1)
        );

    animation:
        hazardPulse 1s ease-in-out infinite;
}}

@keyframes hazardPulse {{

    0%,100% {{
        opacity:0.5;
    }}

    50% {{
        opacity:1;
    }}

}}


/* ===================================
   NORMAL NODE
   =================================== */

.normal {{
    fill:#0D1327;
    stroke:#65708F;
    stroke-width:2;
}}


/* ===================================
   START NODE
   =================================== */

.start {{
    fill:#0C1D36;
    stroke:#38BDF8;
    stroke-width:4;

    filter:
        drop-shadow(
            0 0 12px
            rgba(56,189,248,0.85)
        );
}}


/* ===================================
   EXIT
   =================================== */

.exit {{
    fill:#211B0B;
    stroke:#FBBF24;
    stroke-width:3;
}}


/* ===================================
   TARGET
   =================================== */

.target {{
    fill:#08251E;
    stroke:#22D3A3;
    stroke-width:5;

    filter:
        drop-shadow(
            0 0 15px
            rgba(34,211,163,0.9)
        );
}}


/* ===================================
   NODE CORE
   =================================== */

.core {{
    fill:#E8ECF8;
}}


/* ===================================
   LABELS
   =================================== */

.code {{
    fill:#AEB7D1;

    font-family:
        Arial,
        sans-serif;

    font-size:13px;

    font-weight:800;

    letter-spacing:2px;

    text-anchor:middle;
}}

.name {{
    fill:#646E8E;

    font-family:
        Arial,
        sans-serif;

    font-size:10px;

    font-weight:600;

    letter-spacing:1px;

    text-anchor:middle;
}}

</style>

</head>

<body>

<div class="map">

<svg
    viewBox="0 0 1340 680"
    preserveAspectRatio="xMidYMid meet"
>

<defs>

<pattern
    id="grid"
    width="40"
    height="40"
    patternUnits="userSpaceOnUse"
>

<path
    d="M 40 0 L 0 0 0 40"
    fill="none"
    class="grid"
/>

</pattern>

</defs>

<rect
    width="100%"
    height="100%"
    fill="url(#grid)"
/>

{svg_edges}

{svg_nodes}

</svg>

</div>

</body>

</html>
"""


components.html(
    svg,
    height=670,
    scrolling=False
)


# =========================================================
# MAP LEGEND
# =========================================================

lg1, lg2, lg3, lg4 = st.columns(4)

with lg1:
    st.info("◉  START")

with lg2:
    st.success("━  ACTIVE ROUTE")

with lg3:
    st.error("╍  BLOCKED")

with lg4:
    st.warning("◉  EXIT")


# =========================================================
# DECISION AREA
# =========================================================

st.divider()

st.markdown("### EVACUATION DECISION")


# =========================================================
# BEFORE ANALYSIS
# =========================================================

if not st.session_state.analysis_done:

    st.info(
        "Configure the emergency scenario and run "
        "the evacuation analysis."
    )


# =========================================================
# NO ROUTE
# =========================================================

elif not available_routes:

    st.error(
        "NO EVACUATION ROUTE AVAILABLE"
    )

    st.write(
        "The routing engine could not find a valid "
        "connection from the selected location "
        "to any available exit."
    )


# =========================================================
# ROUTE FOUND
# =========================================================

else:

    st.success(
        "EVACUATION ROUTE IDENTIFIED"
    )

    result1, result2, result3 = st.columns(3)

    with result1:

        st.metric(
            "RECOMMENDED EXIT",
            locations[
                recommended["exit"]
            ].upper()
        )

    with result2:

        st.metric(
            "ROUTE DISTANCE",
            f"{recommended['distance']} m"
        )

    with result3:

        estimated_time = (
            recommended["distance"] / 1.4
        )

        st.metric(
            "EST. WALK TIME",
            f"{estimated_time:.0f} SEC"
        )

    # =====================================================
    # ROUTE
    # =====================================================

    st.markdown(
        "#### OPTIMAL AVAILABLE ROUTE"
    )

    route_names = [
        locations[node]
        for node in recommended["path"]
    ]

    route_text = "  →  ".join(
        route_names
    )

    st.success(
        f"◈  {route_text}"
    )

    # =====================================================
    # BLOCKAGES
    # =====================================================

    if blocked_edges:

        st.markdown(
            "#### DETECTED BLOCKAGES"
        )

        for source, destination, label in blocked_options:

            edge = frozenset(
                [source, destination]
            )

            if edge in blocked_edges:

                st.error(
                    f"BLOCKED  //  "
                    f"{locations[source]}  →  "
                    f"{locations[destination]}"
                )

    # =====================================================
    # EXIT STATUS
    # =====================================================

    st.markdown(
        "#### EXIT STATUS"
    )

    exit_columns = st.columns(
        len(exits)
    )

    for index, exit_location in enumerate(exits):

        with exit_columns[index]:

            path = build_path(
                previous,
                display_start,
                exit_location
            )

            if path:

                distance = distances[
                    exit_location
                ]

                if (
                    exit_location
                    == recommended["exit"]
                ):

                    st.success(
                        f"### ◈ "
                        f"{locations[exit_location]}"
                    )

                    st.write(
                        f"**{distance} m**"
                    )

                    st.caption(
                        "RECOMMENDED EXIT"
                    )

                else:

                    st.info(
                        f"### "
                        f"{locations[exit_location]}"
                    )

                    st.write(
                        f"**{distance} m**"
                    )

                    st.caption(
                        "ALTERNATIVE EXIT"
                    )

            else:

                st.error(
                    f"### ✕ "
                    f"{locations[exit_location]}"
                )

                st.caption(
                    "NO ROUTE AVAILABLE"
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AEGIS // Emergency Route Intelligence   •   "
    "Weighted Graph   •   Dijkstra   •   "
    "Dynamic Rerouting"
)