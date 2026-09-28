import re # Regular Expression  ใช้ค้นหา/แทนที่ pattern
from typing import Dict, Optional
from difflib import SequenceMatcher  # ใช้วัดว่าข้อความสองตัวเหมือนกันมั้ย
import pandas as pd 
from .utils import is_text_like , resolve_column

def normalize_category(value:str) -> str :
    value = str(value).strip().lower()
    
    # เปลี่ยนช่องว่างหลายตัวให้เหลือ 1 ช่อง
    value = re.sub(r"\s+"," ",value)
    
    # delete  . -
    value = value.replace('.','')
    value = value.replace("-",'') 
    return value 

def detect_category_variant(df:pd.DataFrame,columns: Optional[list[str]]=None,) -> pd.DataFrame :
    rows = []
    
    if columns :
        target_columns = columns 
    else :
        target_columns = list(df.columns)
        
    for name in target_columns :
        column = resolve_column(df,name)
        if column is None :
            continue 
        series = df[column]
        
        if not is_text_like(series) :
            continue 
        values = series.dropna().astype(str)
        
        if values.empty :
            continue
        
        # เก็บค่าจริง 
        unique_values = values.unique()
        
        groups: Dict[str,list[str]] = {} # ใช้เก็บ Normalize  orginal val 
        for value in unique_values :
            normalized = normalize_category(value)
            if normalized :
                groups.setdefault(normalized,[]).append(value)
                
        # เช็คว่ามีหลายรูปแบบมั้ย (Category ที่ normalize แล้วเหมือนกัน แต่เขียนต่างกัน)
        for normalized,variants in groups.items() :
            if len(variants) < 2 : # มี value มากกว่า 2 มั้ย
                continue 
            canonical = max(variants,key=lambda x:(values==x).sum()) # เลือกค่าที่พบใน DataFrame บ่อยที่สุดเป็นค่ามาตรฐาน
            for variant in variants :
                if variant == canonical :
                    continue 
                rows.append({"column":column,"variant":variant,"canonical":canonical,"count":int((values==variant).sum()),"match_type":"format"}) #สร้าง Report ออกมา
    return pd.DataFrame(rows,columns=["column","variant","canonical","count","match_type"]) # สร้าง Dataframe ส่งกลับมา