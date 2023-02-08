import datetime
from typing import Any, Dict

PSEUDO_WEIGHT = 999999999.0


def fetch_weights_from_json(measure_grps: Any) -> Dict[str, float]:
    """Fetch a list of weights from the retrieved Json file.

    Returns
    -------
    Dict[int, float]
         key : Datetime of weighing(format="yyyy/MM/dd")
         value : Weight of the datetime
    """
    weights = {}
    for measure_grp in measure_grps:
        measure_date = datetime.datetime.fromtimestamp(measure_grp["date"])
        measure_date_str = measure_date.strftime("%Y/%m/%d")
        weight = measure_grp["measures"][0]["value"] / 1000
        if measure_date_str not in weights:
            weights[measure_date_str] = PSEUDO_WEIGHT
        weights[measure_date_str] = min(weights[measure_date_str], weight)

    return weights
