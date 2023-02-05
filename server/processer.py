from typing import Any, Dict

PSEUDO_WEIGHT = 999999.0


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
        measure_date = measure_grp["date"].fromtimestamp()
        measure_date_str = measure_date.strftime("%Y/%m/%d")
        weight = measure_grp["measures"][0]["value"]
        if measure_date_str not in weights:
            weights[measure_date_str] = PSEUDO_WEIGHT
        weights[measure_date_str] = min(weights[measure_date_str], weight)

    return weights
