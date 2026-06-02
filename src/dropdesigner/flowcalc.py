import math

def lcwFlow(usWSE, dsWSE, weirLength, weirCrestElev):

    usHead = usWSE - weirCrestElev
    dsHead = dsWSE - weirCrestElev

    if usHead <= 0:
        return 0
    
    if dsHead < 0:
        submergence = 0
    else:
        submergence = dsHead/usHead

    return 3.27*weirLength*usHead**(3/2) * (1 - submergence**(3/2))**0.385

def boardsFlow(usWSE, dsWSE, bayWidth, sillElev, boardsPushed, boardHeight):
    crestElev = sillElev + boardsPushed*boardHeight/12
    return lcwFlow(usWSE, dsWSE, bayWidth, crestElev)

def sluiceFlow(usWSE, dsWSE, gateWidth, bottomElev, openHeight, bladeHeight, Cd=0.62):
    bladeTopElev = bottomElev + bladeHeight

    if openHeight <= 0 and bladeTopElev >= usWSE: return 0

    areaUnder = gateWidth * min(openHeight, usWSE - bottomElev)

    headloss = usWSE - dsWSE
    usHeadUnder = usWSE - bottomElev
    dsHeadUnder = dsWSE - bottomElev
    if dsHeadUnder <= 0:
        headUnder = usHeadUnder
    else:
        headUnder = headloss
    
    flowUnder = Cd * areaUnder * (64.4 * headUnder)**(1/2)

    flowOver = lcwFlow(usWSE, dsWSE, gateWidth, bladeTopElev)

    return flowUnder + flowOver

def flumeGateFlow(usWSE, dsWSE, gate, seatElev, openAngleDeg):
    radius = gate["radius_in"]
    frameWidth = gate["frame_width_in"]
    fullOpenCrestHeight = gate["oe_in"]
    closedCrestHeight = gate["ce_in"]
    openingWidth = gate["opening_width_in"]
    radOpen = math.radians(openAngleDeg)
    maxOpenDeg = 5
    maxOpenRad = math.radians(5)
    pivotHeight = fullOpenCrestHeight - radius*math.sin(maxOpenRad)
    pivotElev = seatElev + pivotHeight/12
    crestHeight = pivotHeight + radius*math.sin(radOpen)
    crestElev = seatElev + crestHeight/12

    closedAngleRad = math.asin((closedCrestHeight - pivotHeight)/radius)
    closedAngleDeg = math.degrees(closedAngleRad)

    if openAngleDeg < maxOpenDeg:
        raise ValueError(f"Gate cannot open beyond {maxOpenDeg}$\deg$ from horizontal")
    if openAngleDeg > closedAngleDeg:
        raise ValueError(f"Full closed angle for selected gate is {closedAngleDeg:.1f}")

    usHead = usWSE - crestElev
    dsHead = dsWSE - crestElev

    freeboard = (seatElev + closedCrestHeight/12 - usWSE)*12

    if usHead <= 0:
        flow = 0
    else:
        usHead_in = usHead*12
        usHead_m = usHead_in / 39.37007874
        openingWidth_m = openingWidth / 39.37007871

        unsubFlow = (
            2.09
            * openingWidth_m
            * usHead_m ** 1.5
            * 35.314666721
        )

        flow = unsubFlow

        if dsHead > 0:
            subRatio = dsHead / usHead
            subFactor = (1 - subRatio ** 1.5) ** 0.187
            flow = unsubFlow * subFactor

    result = {
        "flow" : flow,
        "freeboard" : freeboard
    }
    
    return result

def culvertFlow(usWSE, dsWSE, culvCSA, culvLength, culvPerim, manningsN,culvCd=0.82):
    headloss = usWSE - dsWSE
    return culvCd*culvCSA*(64.4*(headloss/(1+(29*culvCd**2*manningsN**0*culvLength/((culvCSA/culvPerim)**(4/3))))))**(1/2)

def featureFlow(usWSE, dsWSE, feature):
    if feature['type'] == 'lcw':
        return lcwFlow(usWSE, dsWSE, feature['weirLength'], feature['weirCrestElev'])
    elif feature['type'] == 'boards':
        return boardsFlow(usWSE, dsWSE, feature['bayWidth'], feature['sillElev'], feature['boardsPushed'], feature['boardHeight'])
    elif feature['type'] == 'sluice':
        return sluiceFlow(usWSE, dsWSE, feature['gateWidth'], feature['bottomElev'], feature['openHeight'], feature['bladeHeight'])
    elif feature['type'] == 'flumegate':
        return flumeGateFlow(usWSE, dsWSE, feature['gate'], feature['seatElev'], feature['openAngleDeg'])['flow']

def dropFlow(usWSE, dsWSE, drop):
    flow = 0
    for feature in drop['features']:
        flow += featureFlow(usWSE, dsWSE, feature)
    return flow