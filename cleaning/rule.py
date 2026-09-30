from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, FrozenSet, Iterable, Optional, Tuple
 
from cleaning.utils import column_tokens, name_has_keyword

current_year = datetime.now().year
@dataclass(frozen=True) 
class ValueRule :
    name:str
    keywords: FrozenSet[str] = field(default_factory=frozenset)
    description:str = ""
    dtype:Optional[str] = None 
    min_value : Optional[float] = None
    max_value : Optional[float] = None
    non_negative: bool =False 
    allowed_values:Optional[Tuple[Any, ... ]] = None 
    
    def matches_column(self,column_name:Any) -> bool :
        if not self.keywords :
            return False 
        return name_has_keyword(column_name,self.keywords)
    
DEFAULT_RULES : Tuple[ValueRule, ...] = (ValueRule(name="age",keywords=frozenset({"age"}),description="Age must be a non-negative integer and must not exceed 120.",dtype="integer",min_value=0,max_value=120,),
                                        ValueRule(name="quality",keywords=frozenset({"quality"}),description="Quality score must be a non-negative integer with no unit.",dtype="integer",min_value=0,),
                                        ValueRule(name="rating",keywords=frozenset({"rating"}),description="Assume a rating scale of 1–5 (Likert scale). If the actual scale differs, define custom overrides accordingly.",dtype="integer",min_value=1,max_value=5,),
                                        ValueRule(name="score",keywords=frozenset({"score"}),description="Assume a score scale of 0–100. If the actual scale differs, define custom overrides accordingly.",dtype="number",min_value=0,max_value=100,),
                                        ValueRule(name="percent",keywords=frozenset({"percent","percentage","pct"}),description="Percentage values must be between 0 and 100, inclusive.",dtype="number",min_value=0,max_value=100,),
                                        ValueRule(name="probability",keywords=frozenset({"probability","prob"}),description="Probability values must be between 0 and 1, inclusive.",min_value=0,max_value=1,),
                                        ValueRule(name="quantity",keywords=frozenset({"quantity", "qty", "count", "stock", "units"}),description="Count values must be non-negative integers.",dtype="integer",non_negative=True,),
                                        ValueRule(name="amount",keywords=frozenset({"price", "cost", "amount", "salary", "income", "revenue", "fee"}),description="Amount values must be non-negative by default. Disable this rule if negative values are valid for refunds or discounts.",dtype="number",non_negative=True,),
                                        ValueRule(name="measurement",keywords=frozenset({"weight", "height", "distance", "length", "width"}),description="Physical measurement values must be non-negative.",dtype="number",non_negative=True,),
                                        ValueRule(name="year",keywords=frozenset({"year"}),description=f"Gregorian year: must be an integer between 1900 and {current_year + 1}.",dtype="integer",min_value=1900,max_value=current_year+1,),
                                        ValueRule(name="latitude",keywords=frozenset({"latitude", "lat"}),description="Latitude must be between -90 and 90, inclusive.",dtype="number",min_value=-90,max_value=90,),
                                        ValueRule(name="longtitude",keywords=frozenset({"longitude", "lon", "lng"}),description="Longitude must be between -180 and 180, inclusive.",dtype="number",min_value=-180,max_value=180,))

def match_rules(df_columns: Iterable[Any],extra_rules: Optional[Iterable[ValueRule]] = None,overrides: Optional[Dict[Any, ValueRule]] = None,) -> Dict[Any, ValueRule] :
    overrides = overrides or {}
    candidate_rules = list(extra_rules or []) + list(DEFAULT_RULES)
    
    '''
        df_columns: รายชื่อคอลัมน์ทั้งหมดของ DataFrame (เช่น df.columns)
        extra_rules: กฎเพิ่มเติมที่ผู้ใช้กำหนดเอง (ตรวจก่อน DEFAULT_RULES)
        overrides: กฎเจาะจงต่อชื่อคอลัมน์จริง {ชื่อคอลัมน์: ValueRule} มีผลเหนือกว่าทุกก
    '''
    
    matched: Dict[Any, ValueRule] = {}
    for column in df_columns:
        if column in overrides:
            matched[column] = overrides[column]
            continue
        for rule in candidate_rules:
            if rule.matches_column(column):
                matched[column] = rule
                break
 
    return matched
    