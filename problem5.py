"""
问题 5: 数据管道聚合器(AI 开发)
Problem 5: Data Pipeline Aggregator (Developped by AI)
"""
from typing import List, Dict, Any, Optional, Callable


def clean_and_aggregate(
    records: List[Dict[str, Any]],
    group_by: str,
    metric: str,
    aggregation: str = "mean",
    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
) -> Dict[str, float]:
    """按指定键对记录进行过滤、清洗和聚合。"""

    # 检查输入类型和空列表。
    if not isinstance(records, list):
        raise TypeError("records must be a list")

    if not records:
        raise ValueError("records cannot be empty")

    valid_aggregations = {"sum", "mean", "min", "max", "count"}
    agg_op = aggregation.lower()

    if agg_op not in valid_aggregations:
        raise ValueError(
            f"Invalid aggregation '{aggregation}'. "
            f"Must be one of {valid_aggregations}"
        )

    grouped_values: Dict[str, List[float]] = {}

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise TypeError(
                f"Record at index {i} must be a dictionary"
            )

        if group_by not in record:
            raise ValueError(
                f"Record at index {i} is missing group_by key: "
                f"'{group_by}'"
            )

        if metric not in record:
            raise ValueError(
                f"Record at index {i} is missing metric key: "
                f"'{metric}'"
            )

        if filter_fn is not None and not filter_fn(record):
            continue

        raw_val = record[metric]

        # 忽略指标值为 None 的记录。
        if raw_val is None:
            continue

        # bool 虽然是 int 的子类，但这里不作为有效数值。
        if not isinstance(raw_val, (int, float)) or isinstance(raw_val, bool):
            raise TypeError(
                f"Metric value '{raw_val}' in record {i} is not numeric"
            )

        group_key = str(record[group_by])
        if group_key not in grouped_values:
            grouped_values[group_key] = []

        grouped_values[group_key].append(float(raw_val))

    results: Dict[str, float] = {}

    for group_key, values in grouped_values.items():
        if agg_op == "sum":
            val = sum(values)
        elif agg_op == "mean":
            val = sum(values) / len(values)
        elif agg_op == "min":
            val = min(values)
        elif agg_op == "max":
            val = max(values)
        else:  # count
            val = float(len(values))

        results[group_key] = round(val, 2)
        
        
    return results
    """
    Filter, clean, and aggregate a list of dictionary records by a grouping key.
    根据分组键过滤、清洗并聚合字典记录列表。

    Args:
    参数：
        records (List[Dict[str, Any]]): List of records (each record is a dict).
        records (List[Dict[str, Any]])：记录列表（每条记录都是一个字典）。
        group_by (str): The dictionary key to group records by.
        group_by (str)：用于分组的字典键。
        metric (str): The numeric dictionary key to aggregate.
        metric (str)：要聚合的数值字典键。
        aggregation (str): Aggregation function: "sum", "mean", "min", "max", or "count".
        aggregation (str)：聚合函数："sum"、"mean"、"min"、"max" 或 "count"。
        filter_fn (Optional[Callable]): Optional predicate function to filter records before aggregation.
        filter_fn (Optional[Callable])：在聚合前筛选记录的可选谓词函数。

    Returns:
    返回：
        Dict[str, float]: Aggregated dictionary mapping group names to calculated float metrics.
        Dict[str, float]：按分组名映射到计算结果浮点值的聚合字典。

    Raises:
    引发：
        ValueError: 如果 records 为空、聚合类型无效，或记录中缺少键。
        TypeError: 如果 records 不是列表，或者指标值不是数字。
    """


  
