import streamlit as st

from loader import load_flumegates
import flowcalc as fc

# Load Rubicon Flumegate Data
df = load_flumegates()
gateData = df.to_dict("records")

# Page Setup
st.set_page_config(
    page_title="Drop Builder",
    layout="wide"
)

def opFlowColumn(col_num, usWSE, dsWSE):
    bayType = st.selectbox("Bay Type",bayTypes,format_func=lambda x: f'{x["name"]}', key=f"feature_{i}")
    prefix = f"bay_{col_num}"

    flowMode = 1 if opFlowTab.open else 0

    if bayType["type"] == "lcw":
        bayType["weirLength"] = st.number_input("Weir Length (ft)", min_value=0, key=f"{prefix}_weirLength")
        bayType["weirCrestElev"] = st.number_input("Crest Elev (ft)", key=f"{prefix}_weirCrestElev")
    elif bayType["type"] == "boards":
        bayType["bayWidth"] = st.number_input("Bay Width (ft)", min_value=0.0, key=f"{prefix}_bayWidth")
        bayType["sillElev"] = st.number_input("Sill Elev (ft)",key=f"{prefix}_sillElev")
        bayType["boardsPushed"] = st.number_input("Boards Pushed", min_value=0, step=1,key=f"{prefix}_boardsPushed")*flowMode
        bayType["boardHeight"] = st.number_input("Height of Each Board (in)", min_value=0.0, value=6.0,key=f"{prefix}_boardHeight")
    elif bayType["type"] == "sluice":
        bayType["gateWidth"] = st.number_input("Gate Width (ft)", min_value=0.0, key=f"{prefix}_gateWidth")
        # bayType["bottomElev"] = st.number_input("Gate Bottom Elev (ft)",key=f"{prefix}_bottomElev")
        # ^for U/S floor elevations different between bays
        bayType["bottomElev"] = usFloorElev
        # bayType["bladeHeight"] = st.number_input("Blade Height (ft)", min_value=0,key=f"{prefix}_bladeHeigh")
        # ^for if sluice gates act as weirs (water flows over)
        bayType["bladeHeight"] = 99
        bayType["openHeight"] = st.number_input("Gate Opened Height (ft)", min_value=0.0, step=0.1, key=f"{prefix}_openHeight")*flowMode + 99*(1-flowMode)
    elif bayType["type"] == "flumegate":
        bayType["gate"] = st.selectbox("Gate Model", gateData, format_func=lambda gate: gate["model"],key=f"{prefix}_gate")
        # usFloor = st.number_input("Bay Upstream Floor Elev (ft)",key=f"{prefix}_ st")
        # ^for U/S floor elevations different between bays
        usFloor = usFloorElev
        sandWeirHeight = st.number_input("Sand Weir Height (in)", key=f"{prefix}_sandWeirHeight")
        bayType["seatElev"] = usFloor + sandWeirHeight/12
        bayType["openAngleDeg"] = st.number_input("Gate Open Angle (degree)", value=5.0, min_value=5.0,key=f"{prefix}_openAngleDeg")*flowMode + 5*(1-flowMode)

    features[f"bay_{col_num}"] = bayType

    featureFlow = fc.featureFlow(usWSE, dsWSE, bayType)
    return featureFlow
    

# Sidebar
sb = st.sidebar
sb.header("Structure")
usWSE = sb.number_input("Upstream Water Elev (ft)")
dsWSE = sb.number_input("Downstream Water Elev (ft)")
usFloorElev = sb.number_input("Upstream Floor Elev (ft)")
numBays = sb.number_input("Number of Bays", value=4, min_value=1, max_value=12, step=1)

sb.divider()

sb.header("Flow")
opFlow = sb.number_input("Max Operational Flow (cfs)", min_value=0, step=1)
stormFlow = sb.number_input("Max Storm Flow (cfs)", min_value=0, step=1)

sb.divider()

# Main
bayTab = st.tabs(["Drop Bays"])
bays = st.columns(int(numBays), border=True, gap="xxsmall", width="stretch")

opFlowTab, stormFlowTab = st.tabs(["Operational Flow", "Storm Flow"], on_change="rerun")

bayTypes = [
    {
        "type" : "lcw",
        "name" : "Long Crested Weir"
    },
    {
        "type" : "boards",
        "name" : "Board Bay"
    },
    {
        "type" : "flumegate",
        "name" : "Flume Gate"
    },
    {
        "type" : "sluice",
        "name" : "Slide Gate"
    },
]

features = {}

bayFlows = []

for i, bay in enumerate(bays):
    with bay:
        st.info(f"**Bay #{i+1}**")
        bayFlowCalc = opFlowColumn(i, usWSE, dsWSE)
        bayFlows.append(bayFlowCalc)

with opFlowTab:
    st.subheader("Flow at Existing Water Levels")
    flows = st.columns(int(numBays), border=True, gap="xxsmall", width="stretch")

    for i, flow in enumerate(flows):
        with flow:
            st.metric(f"BAY #{i+1} FLOW", f"**{bayFlows[i]:.1f}** cfs")
    
    dropFlow = sum(bayFlows)
    
    with st.container(border=True):
        st.metric("FLOW THROUGH DROP", f"**{dropFlow:.0f}** cfs")

with stormFlowTab:
    st.subheader("Flow at Existing Water Levels")
    flows = st.columns(int(numBays), border=True, gap="xxsmall", width="stretch")

    for i, flow in enumerate(flows):
        with flow:
            st.metric(f"BAY #{i+1} FLOW", f"**{bayFlows[i]:.1f}** cfs")
    
    dropFlow = sum(bayFlows)
    
    with st.container(border=True):
        st.metric("FLOW THROUGH DROP", f"**{dropFlow:.0f}** cfs")
