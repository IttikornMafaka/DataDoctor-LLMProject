"""
value_validator.py

Value Sanity Validation: checks whether the actual values in each column violate the rules defined in rule.py,
e.g. negative age, a decimal quality score where an integer is expected, a percentage above 100.

Unlike validator.py (detect_invalid_values), this module checks against explicitly defined rules
(rule.py) instead of guessing from text patterns. It is best suited to checking value ranges and data types of numeric columns.

Violation types checked:
    not_number   cannot be converted to a number although the rule requires a number/integer
    not_integer  is a number but has a decimal part although the rule requires an integer (e.g. quality = 4.5)
    negative     negative value in a column where the rule sets non_negative=True
    below_min    value is below the configured min_value (e.g. age -5)
    above_max    value is above the configured max_value (e.g. age 250)
    not_allowed  value is not in the configured allowed_values

No function modifies the original DataFrame; they only check and report.
The user reviews the report first, then chooses how to fix issues via value_normalizer.py
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

import re

import numpy as np
import pandas as pd

from .rule import ValueRule, match_rules

REPORT_COLUMNS = [
    "column",
    "rule",
    "violation",
    "description",
    "invalid_count",
    "percent",
    "min_allowed",
    "max_allowed",
    "examples",
]

VIOLATION_INFO: Dict[str, str] = {
    "not_number": "Cannot be converted to a number (the rule expects a number)",
    "not_integer": "Has a decimal part (the rule expects an integer)",
    "negative": "Negative value (this column should not be negative)",
    "below_min": "Value is below the configured minimum",
    "above_max": "Value is above the configured maximum",
    "not_allowed": "Value is not in the list of allowed values",
}


def _to_bool_array(mask: pd.Series) -> np.ndarray:
    return mask.fillna(False).to_numpy(dtype=bool)


def _numeric_values(series: pd.Series) -> pd.Series:
    """Convert a series to numbers (float); values that cannot be converted become NaN, existing NaN is left alone."""
    if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
        return series.astype("float64")
    return pd.to_numeric(series.astype("object").where(series.notna(), np.nan), errors="coerce")


def _is_integer_like(numbers: pd.Series) -> pd.Series:
    """True only for rows that are truly whole numbers (tolerates tiny floating point error)."""
    rounded = numbers.round()
    return (numbers - rounded).abs() < 1e-9


def _rule_masks(series: pd.Series, rule: ValueRule) -> Dict[str, np.ndarray]:
    masks: Dict[str, np.ndarray] = {}
    present = series.notna()

    if rule.allowed_values is not None:
        allowed = {str(v).strip() for v in rule.allowed_values}
        as_text = series.astype(str).str.strip()
        masks["not_allowed"] = _to_bool_array(present & ~as_text.isin(list(allowed)))
        return masks  # allowed_values is a categorical rule; no numeric range/type checks follow

    if rule.dtype in ("integer", "number"):
        numbers = _numeric_values(series)
        could_not_convert = _to_bool_array(present & numbers.isna())
        if could_not_convert.any():
            masks["not_number"] = could_not_convert

        # Only check values that converted to numbers, so NaN from not_number does not mix with below_min etc.
        convertible = _to_bool_array(present) & ~could_not_convert

        if rule.dtype == "integer" and convertible.any():
            integer_ok = np.zeros(len(series), dtype=bool)
            integer_ok[convertible] = _is_integer_like(numbers[convertible]).to_numpy(dtype=bool)
            not_integer = convertible & ~integer_ok
            if not_integer.any():
                masks["not_integer"] = not_integer

        if rule.non_negative and rule.min_value is None and convertible.any():
            masks["negative"] = convertible & _to_bool_array(numbers < 0)

        if rule.min_value is not None and convertible.any():
            masks["below_min"] = convertible & _to_bool_array(numbers < float(rule.min_value))

        if rule.max_value is not None and convertible.any():
            masks["above_max"] = convertible & _to_bool_array(numbers > float(rule.max_value))

    return masks


# ---------------------------------------------------------------------------
# Unit stripping: "5 pcs" -> 5, "1,200 kg" -> 1200, "$120" -> 120, "75%" -> 75
# ---------------------------------------------------------------------------

# optional currency prefix, number (with , thousands), optional short unit text
UNIT_PATTERN = re.compile(
    r"^\s*[$€£฿¥]?\s*([+\-]?\d[\d,]*(?:\.\d+)?)\s*([A-Za-z%°/².\s]{0,15})\s*$"
)


def _extract_number_and_unit(series: pd.Series):
    """Return (numbers, has_unit_mask, fits_mask) for a text series."""
    text = series.astype("string").str.strip()
    parts = text.str.extract(UNIT_PATTERN)
    fits = parts[0].notna()
    numbers = pd.to_numeric(parts[0].str.replace(",", "", regex=False), errors="coerce")

    unit_text = parts[1].fillna("").str.strip()
    has_currency = text.str.match(r"^\s*[$€£฿¥]", na=False)
    has_unit = fits & ((unit_text != "") | has_currency)
    return numbers, has_unit, fits


def strip_units(
    df: pd.DataFrame,
    rule_columns: Optional[Iterable[Any]] = None,
    rule_ratio: float = 0.3,
    generic_ratio: float = 0.8,
) -> Tuple[pd.DataFrame, int, str]:
    """
    Strip unit text from numeric-looking text columns (does not modify df).

    A text column is converted when at least one value carries a unit/symbol and the share of
    values that look like "number + optional unit" is >= rule_ratio for columns the value rules
    say are numeric (quantity, price, ...), or >= generic_ratio for every other column
    (kept high so IDs and names are left alone). Date columns are never touched.

    Returns: (new_df, corrections, log_text)
    """
    result = df.copy()
    rule_columns = set(rule_columns or [])
    corrections = 0
    logs: List[str] = []

    for column in result.columns:
        series = result[column]

        if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            continue

        present = series.notna()
        if not present.any():
            continue

        numbers, has_unit, fits = _extract_number_and_unit(series)
        if not has_unit.any():
            continue

        needed = rule_ratio if column in rule_columns else generic_ratio
        if fits[present].mean() < needed:
            continue

        changed = int((present & has_unit).sum())
        unreadable = int((present & numbers.isna()).sum())

        clean = numbers
        valid = clean.dropna()
        if len(valid) and ((valid - valid.round()).abs() < 1e-9).all():
            clean = clean.round().astype("Int64")

        result[column] = clean
        corrections += changed
        logs.append(
            f"{column} [unit]: removed units from {changed:,} value(s)"
            + (f", {unreadable:,} unreadable value(s) set to NaN" if unreadable else "")
        )

    return result, corrections, "\n".join(logs)


def find_violation_masks(
    df: pd.DataFrame,
    extra_rules: Optional[Iterable[ValueRule]] = None,
    overrides: Optional[Dict[Any, ValueRule]] = None,
) -> Dict[Tuple[Any, str], np.ndarray]:
    """
    Find masks (boolean arrays by row position) of rule-violating values for every (column, violation) pair.

    Columns that match no rule (not in DEFAULT_RULES/extra_rules/overrides) are simply skipped.
    A column that raises an error while being checked (e.g. an unusual dtype) is skipped on its own without failing everything.
    """
    matched_rules = match_rules(df.columns, extra_rules=extra_rules, overrides=overrides)
    result: Dict[Tuple[Any, str], np.ndarray] = {}

    for column, rule in matched_rules.items():
        try:
            for violation, mask in _rule_masks(df[column], rule).items():
                result[(column, violation)] = mask
        except Exception as error:
            import warnings

            warnings.warn(f"Value check skipped for column {column!r}: {error}")
            continue

    return result


def detect_value_violations(
    df: pd.DataFrame,
    extra_rules: Optional[Iterable[ValueRule]] = None,
    overrides: Optional[Dict[Any, ValueRule]] = None,
) -> pd.DataFrame:
    """
    Check all values in every column that matches a rule and return a report for the user to review before fixing.

    Args:
        df: DataFrame to check
        extra_rules: additional user-defined rules (see rule.ValueRule)
        overrides: rules for specific real column names {column_name: ValueRule}

    Returns:
        DataFrame with columns: column, rule, violation, description, invalid_count, percent,
        min_allowed, max_allowed, examples
        (sorted from most to least frequent problem)
    """
    matched_rules = match_rules(df.columns, extra_rules=extra_rules, overrides=overrides)
    masks = find_violation_masks(df, extra_rules=extra_rules, overrides=overrides)

    rows: List[dict] = []
    total = len(df)

    for (column, violation), mask in masks.items():
        count = int(mask.sum())
        if count == 0:
            continue

        rule = matched_rules.get(column)
        examples = (
            df[column][mask].astype(str).drop_duplicates().head(3).map(lambda v: v[:30]).tolist()
        )

        rows.append(
            {
                "column": str(column),
                "rule": rule.name if rule else "",
                "violation": violation,
                "description": VIOLATION_INFO.get(violation, violation),
                "invalid_count": count,
                "percent": round(count / total * 100, 2) if total else 0.0,
                "min_allowed": rule.min_value if rule else None,
                "max_allowed": rule.max_value if rule else None,
                "examples": ", ".join(examples),
            }
        )

    report = pd.DataFrame(rows, columns=REPORT_COLUMNS)

    if not report.empty:
        report = report.sort_values("invalid_count", ascending=False).reset_index(drop=True)

    return report


def build_rule_summary(
    df: pd.DataFrame,
    extra_rules: Optional[Iterable[ValueRule]] = None,
    overrides: Optional[Dict[Any, ValueRule]] = None,
) -> pd.DataFrame:
    """
    Summarize which column is matched with which rule, with a description of the rule's assumptions.
    Useful for checking that the rules the system guessed fit the real data (e.g. is rating really 1-5?)
    before trusting the results of detect_value_violations()
    """
    matched_rules = match_rules(df.columns, extra_rules=extra_rules, overrides=overrides)
    rows = [
        {
            "column": str(column),
            "rule": rule.name,
            "dtype": rule.dtype or "-",
            "min_allowed": rule.min_value,
            "max_allowed": rule.max_value,
            "non_negative": rule.non_negative,
            "description": rule.description,
        }
        for column, rule in matched_rules.items()
    ]
    return pd.DataFrame(
        rows,
        columns=["column", "rule", "dtype", "min_allowed", "max_allowed", "non_negative", "description"],
    )