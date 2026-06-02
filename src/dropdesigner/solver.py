from flowcalc import lcwFlow, boardsFlow, featureFlow, dropFlow
from scipy.optimize import brentq

def usDropSolveWSE(targetQ, dsWSE, drop):
    lower = drop.get("usFloorElev", 0.0)
    upper = lower + 40

    def residual(usWSE):
        calcQ = dropFlow(usWSE, dsWSE, drop)
        return calcQ - targetQ

    return brentq(residual, lower, upper)