from typing import Any , Optional 
import pandas as pd 

# ตรวจว่า column  เป็น text หรือ Catagory 
def is_text_like(series:pd.Series) -> bool : 
    return (pd.api.types.is_object_dtype(series)  # ตรวจสอบว่าเป็น Obj มั้ย
            or pd.api.types.is_string_dtype(series.dtype)  # ตรวจสอบว่า column เป็น str มั้ย
            or isinstance(series.dtype,pd.CategoricalDtype)) # dtype ของ column นี้เป็น CategoricalDtype หรือเปล่า

# หา column จริง แม้ชื่อ column ใน UI จะถูกแปลงเป็น str
def resolve_column(df:pd.DataFrame,name:Any) -> Optional[Any] :
    if name in df.columns :
        return name 
    lookup = {str(column):column for column in df.columns} 
    return lookup.get(str(name))

# แปลงค่าจาก Gradio checkbox/table ให้เป็น True/False

def truthy(value:Any) -> bool :
    if value is None :
        return False 
    if isinstance(value,str) :
        return value.strip().lower() in {"true","1","yes","y","✓"}
    try : 
        if pd.isna(value) :
            return False 
    except (TypeError,ValueError) :
        pass 
    return bool(value)