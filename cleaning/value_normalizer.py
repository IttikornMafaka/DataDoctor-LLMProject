"""
value_normalizer.py

แก้ค่าที่ผิดกฎ (ตรวจพบโดย value_validator.py) ด้วยวิธีที่ผู้ใช้เลือกเองต่อคู่ (คอลัมน์, violation)
ไม่แก้ไข DataFrame ต้นฉบับ เป็นไปตามรูปแบบเดียวกับ fix_invalid_values() ใน validator.py คือ
"ตรวจ -> ให้ผู้ใช้เลือกรายการที่จะแก้และวิธีแก้ -> ค่อยแก้จริง"

Actions ที่รองรับ:
  to_nan     แปลงค่าที่ผิดเป็นค่าว่าง (ปลอดภัยที่สุด แนะนำเป็นค่าเริ่มต้น) แล้วไปเติมค่าใหม่ทีหลังได้
             ด้วย fill_column()
  clip       ดึงค่าที่เกินช่วงให้เข้าช่วง [min_value, max_value] ของกฎ (เช่น อายุ 150 -> 120)
             ใช้ได้เฉพาะ violation: below_min, above_max (ต้องมี min/max ในกฎ)
  round_int  ปัดเศษเป็นจำนวนเต็มที่ใกล้ที่สุด ใช้ได้เฉพาะ violation: not_integer
  abs_value  แปลงค่าติดลบเป็นค่าบวก (สมมติว่าเป็นการติดเครื่องหมายผิด) ใช้ได้เฉพาะ violation: negative
             *ใช้ด้วยความระมัดระวัง* ถ้าค่าติดลบอาจมีความหมายจริง (เช่นยอดคืนเงิน) อย่าใช้ action นี้
  drop_rows  ลบทั้งแถวที่มีค่าผิด
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import re
from .utils import resolve_column
from .rule import ValueRule, match_rules
from .value_validator import _numeric_values, find_violation_masks

VALID_ACTIONS = {"to_nan", "clip", "round_int", "abs_value", "drop_rows","remove_unit"}

def remove_unit_from_value(value: Any) -> Any:
    """
    Remove non-numeric unit text from a value.

    Examples:
        "80 kg" -> 80
        "90 points" -> 90
        "75%" -> 75
        "100 cm" -> 100
    """
    if pd.isna(value):
        return value

    if isinstance(value, (int, float, np.number)):
        return value

    text = str(value).strip()

    match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*[^\d\s].*$", text)

    if match:
        number = match.group(1)

        if "." in number:
            return float(number)

        return int(number)

    return value


# violation ไหนใช้ action ไหนได้บ้าง (นอกเหนือจาก to_nan / drop_rows ที่ใช้ได้กับทุก violation)
_ACTION_COMPATIBLE_VIOLATIONS = {"clip": {"negative", "below_min", "above_max"},"round_int": {"not_integer"},"abs_value": {"negative", "below_min"},"remove_unit": {"not_number"},}

def _remove_units(series: pd.Series) -> pd.Series:
    """
    Extract numeric values from strings containing units.

    Examples:
        "80 kg"    -> 80
        "75.5 kg"  -> 75.5
        "$120"     -> 120
        "1,200 kg" -> 1200
    """

    if pd.api.types.is_numeric_dtype(series):
        return series.copy()

    text = series.astype("string").str.strip()

    cleaned = (
        text
        .str.replace(",", "", regex=False)
        .str.extract(
            r"([+\-]?\d+(?:\.\d+)?)",
            expand=False
        )
    )

    return pd.to_numeric(cleaned,errors="coerce")

def normalize_values(df: pd.DataFrame,choices: List[Tuple[Any, str, str]],extra_rules: Optional[Iterable[ValueRule]] = None,overrides: Optional[Dict[Any, ValueRule]] = None,) -> Tuple[pd.DataFrame, str]:
    """
    แก้ค่าที่ผิดกฎตามรายการที่ผู้ใช้เลือก (ไม่แก้ df ต้นฉบับ)

    Args:
        df: DataFrame ต้นฉบับ
        choices: list ของ (ชื่อคอลัมน์, violation, action)
                 เช่น [("age", "negative", "to_nan"), ("quality", "not_integer", "round_int")]
                 ดู violation ที่รองรับใน value_validator.VIOLATION_INFO
                 และ action ที่รองรับใน VALID_ACTIONS ด้านบน
        extra_rules / overrides: ต้องส่งชุดเดียวกับตอนเรียก detect_value_violations()
                                  เพื่อให้ mask ที่คำนวณใหม่ตรงกับรายงานที่ผู้ใช้เห็น

    Returns:
        (cleaned_df, log_text)
    """
    matched_rules = match_rules(df.columns, extra_rules=extra_rules, overrides=overrides)
    masks = find_violation_masks(df, extra_rules=extra_rules, overrides=overrides)

    cleaned = df.copy()
    logs: List[str] = []
    drop_mask = np.zeros(len(df), dtype=bool)

    for name, violation, action in choices:
        column = resolve_column(df, name)

        if action not in VALID_ACTIONS:
            logs.append(f"{name} [{violation}]: ไม่รู้จัก action '{action}' (ข้าม)")
            continue

        if column is None:
            logs.append(f"{name} [{violation}]: ไม่พบคอลัมน์นี้ (ข้าม)")
            continue

        mask = masks.get((column, violation))
        if mask is None or not mask.any():
            logs.append(f"{column} [{violation}]: ไม่พบปัญหานี้แล้ว (ข้าม)")
            continue

        rule = matched_rules.get(column)
        compatible = _ACTION_COMPATIBLE_VIOLATIONS.get(action)
        if compatible is not None and violation not in compatible:
            logs.append(
                f"{column} [{violation}]: action '{action}' ใช้กับปัญหานี้ไม่ได้ (ข้าม, "
                f"ใช้ได้กับ: {', '.join(sorted(compatible))})"
            )
            continue

        count = int(mask.sum())
        
        if action == "remove_unit":
            numeric = _remove_units(cleaned[column])
            cleaned[column] = numeric
            logs.append(f"{column} [{violation}]: "f"ลบหน่วย/ข้อความที่ติดกับตัวเลข "f"{count:,} ค่า")
            continue

        if action == "drop_rows":
            drop_mask |= mask
            logs.append(f"{column} [{violation}]: ทำเครื่องหมายลบ {count:,} แถว")
            continue

        if action == "to_nan":
            cleaned[column] = cleaned[column].mask(mask)
            logs.append(f"{column} [{violation}]: แปลง {count:,} ค่าเป็นค่าว่าง")
            continue

        # clip / round_int / abs_value ต้องคำนวณจากค่าตัวเลขของคอลัมน์เดิม (ก่อนแก้ค่าอื่นทับ)
        # ใช้ .where() แทนการ round-trip ผ่าน object/pd.to_numeric เพื่อคงค่า/dtype ของแถวที่ไม่ถูกแก้ไว้เหมือนเดิม
        numbers = _numeric_values(df[column])
        mask_series = pd.Series(mask, index=cleaned.index)

        if action == "clip":
            if rule is None or (rule.min_value is None and rule.max_value is None):
                logs.append(f"{column} [{violation}]: ไม่มี min/max ในกฎ ใช้ clip ไม่ได้ (ข้าม)")
                continue
            clipped = numbers.clip(lower=rule.min_value, upper=rule.max_value)
            cleaned[column] = cleaned[column].where(~mask_series, other=clipped)
            logs.append(
                f"{column} [{violation}]: ดึงค่า {count:,} ค่าเข้าช่วง "
                f"[{rule.min_value}, {rule.max_value}]"
            )

        elif action == "round_int":
            rounded = numbers.round()
            cleaned[column] = cleaned[column].where(~mask_series, other=rounded)
            logs.append(f"{column} [{violation}]: ปัดเศษ {count:,} ค่าเป็นจำนวนเต็ม")

        elif action == "abs_value":
            absolute = numbers.abs()
            cleaned[column] = cleaned[column].where(~mask_series, other=absolute)
            logs.append(f"{column} [{violation}]: แปลง {count:,} ค่าติดลบเป็นค่าบวก")

    if drop_mask.any():
        before = len(cleaned)
        cleaned = cleaned[~drop_mask]
        logs.append(f"ลบทั้งหมด {before - len(cleaned):,} แถว (นับแถวที่ผิดหลายข้อเป็นแถวเดียว)")

    return cleaned, "\n".join(logs)


# Date normalization: 2020-10-02 -> 2020/10/2  (zero_pad=True -> 2020/10/02)

DATE_NAME_HINTS = ("date", "time", "dob", "birth", "created", "updated")
DATE_PATTERN = r"^\s*\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}"


def _parse_dates(series: pd.Series, dayfirst: bool = False) -> pd.Series:
    try:
        return pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=dayfirst)
    except (TypeError, ValueError):
        return pd.to_datetime(series, errors="coerce", dayfirst=dayfirst)


def _format_date(ts, zero_pad: bool):
    if pd.isna(ts):
        return ts
    if zero_pad:
        return f"{ts.year}/{ts.month:02d}/{ts.day:02d}"
    return f"{ts.year}/{ts.month}/{ts.day}"


def normalize_dates(df: pd.DataFrame,zero_pad: bool = False,dayfirst: bool = False,min_ratio: float = 0.8,) -> Tuple[pd.DataFrame, str]:
    """
    Format date columns as YYYY/M/D (or YYYY/MM/DD when zero_pad=True). Does not modify df.

    A column is treated as a date column when it is already a datetime dtype, or its name contains
    a date hint (date, time, dob, ...) and >= 50% of values parse, or >= min_ratio of its values
    look like dates and parse. Values that cannot be parsed are left unchanged.

    Returns: (new_df, log_text)
    """
    result = df.copy()
    logs: List[str] = []

    for col in result.columns:
        s = result[col]

        if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_bool_dtype(s):
            continue

        present = s.notna()
        if not present.any():
            continue

        is_dt = pd.api.types.is_datetime64_any_dtype(s)
        hinted = any(h in str(col).lower() for h in DATE_NAME_HINTS)

        # Avoid treating plain numbers like "2020" or "80" as dates
        if not is_dt and not hinted:
            looks = s[present].astype(str).str.match(DATE_PATTERN).mean()
            if looks < min_ratio:
                continue

        parsed = s if is_dt else _parse_dates(s, dayfirst=dayfirst)
        ratio = parsed[present].notna().mean()
        if ratio < (0.5 if hinted else min_ratio):
            continue

        formatted = parsed.map(lambda ts: _format_date(ts, zero_pad)).astype("object")
        result[col] = formatted.where(parsed.notna(), s.astype("object"))

        ok = int(parsed.notna().sum())
        bad = int((present & parsed.isna()).sum())
        logs.append(
            f"{col}: reformatted {ok:,} date(s)"
            + (f", {bad:,} unparseable left unchanged" if bad else "")
        )

    return result, "\n".join(logs) if logs else "No date columns detected."



# Missing price handling

PRICE_PATTERN = re.compile(r"(?<![a-z])(price|cost|amount|salary|income|revenue|fee)s?(?![a-z])")


def is_price_column(name: Any) -> bool:
    """True for price-like column names: price, unit_price, total_cost, Amount, ..."""
    return PRICE_PATTERN.search(str(name).lower()) is not None


def fill_missing_prices(df: pd.DataFrame,price_columns: Optional[Iterable[Any]] = None,group_by: Optional[Any] = None,max_missing_ratio: float = 0.3,decimals: int = 2,add_flag: bool = False,) -> Tuple[pd.DataFrame, str]:
    """
    Fill blank prices with the MEDIAN (never 0, never the mean). Does not modify df.

    Why median: prices are right-skewed, so a few expensive items drag the mean up and would
    invent a price nobody charges. Filling with 0 is worse: it drags averages down and looks
    like a real (free) price.

    If group_by is given (e.g. "category" or "product"), each blank gets the median of its own
    group; groups with fewer than 3 known prices fall back to the overall median.

    A column is left untouched (with a warning in the log) when more than max_missing_ratio of
    its values are blank: at that point a guessed price is mostly invention, so review it manually.

    add_flag=True adds a "<column>_was_missing" True/False column so models can tell filled
    values from real ones.

    Run this AFTER unit stripping so "$120" / "5 THB" are already numbers.
    Returns: (new_df, log_text)
    """
    
    result = df.copy()
    logs: List[str] = []

    columns = list(price_columns) if price_columns is not None else [c for c in result.columns if is_price_column(c)]
    
    for col in columns:
        if col not in result.columns:
            continue

        raw = result[col]
        blank = raw.isna() | raw.astype("string").str.strip().eq("").fillna(False)
        numbers = pd.to_numeric(raw.mask(blank), errors="coerce")

        missing = blank | numbers.isna()
        missing_count = int(missing.sum())
        if missing_count == 0:
            continue

        known = numbers.dropna()
        if known.empty:
            logs.append(f"{col}: all values missing, nothing to base a price on (skipped)")
            continue

        ratio = missing_count / len(result)
        if ratio > max_missing_ratio:
            logs.append(f"{col}: {missing_count:,} missing ({ratio:.0%}) is more than "f"{max_missing_ratio:.0%}, left unfilled - review manually")
            continue

        overall = known.median()
        filled = numbers.copy()

        if group_by is not None and group_by in result.columns:
            grouped = numbers.groupby(result[group_by])
            group_median = grouped.transform("median")
            group_size = grouped.transform("count")
            usable = group_size >= 3
            filled = filled.fillna(group_median.where(usable))
            filled = filled.fillna(overall)
            how = f"median per '{group_by}' (overall median {overall:g} as fallback)"
        else:
            filled = filled.fillna(overall)
            how = f"median {overall:g}"

        filled = filled.round(decimals)
        if add_flag:
            result[f"{col}_was_missing"] = missing

        result[col] = filled
        logs.append(f"{col}: filled {missing_count:,} missing price(s) with {how}")

    return result, "\n".join(logs) if logs else "No missing prices."