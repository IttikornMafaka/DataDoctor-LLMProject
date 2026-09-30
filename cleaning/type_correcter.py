import pandas as pd 
from typing import Optional 
from .utils import is_text_like , resolve_column 

Support_type = ["numeric","integer","boolean","datetime","string"]

def detect_type_issue(df:pd.DataFrame,columns:Optional[list[str]]=None,)-> pd.DataFrame :
    rows = []
    if columns :
        target_columns = columns 
    else :
        target_columns = list(df.columns)
        
    for name in target_columns :
        columns = resolve_column(df,name)
        
        if columns is None :
            continue 
        series = df[columns]
        
        # text-> Numeric 
        if is_text_like(series) :
            value = series.dropna().astype(str).str.strip()
            if value.empty : 
                continue
            numeric_value = pd.to_numeric(value,errors="coerce")
            numeric_ratio = numeric_value.notna().mean()
            if numeric_ratio >= 0.9 :
                if(numeric_value.dropna()%1 == 0 ).all() :
                    suggested_type = "integer"
                else : 
                    suggested_type = "numeric"
                rows.append({"column":columns,"current_type":str(series.dtypes),"suggested_dtype":suggested_type,"confidence":round(numeric_ratio*100,1)})
                continue 
            
        # text->Boolean 
        if is_text_like(series) :
            value = (series.dropna().astype(str).str.strip().str.lower())
            if value.empty :
                continue 
            boolean_values = {"true","false","yes","no"}
            boolean_ratio = value.isin(boolean_values).mean()
            if boolean_ratio >= 0.9 :
                rows.append({"column":columns,"current_type":str(series.dtype),"suggested_type":"boolean","confidence":round(boolean_ratio*100,1)})
                continue 
        # text->Datetime 
        if is_text_like(series) :
            value = (series.dropna().astype(str).str.strip())
            if value.empty :
                continue 
            datetime_values = pd.to_datetime(value,errors="coerce")
            datetime_ratio = datetime_values.notna().mean()
            if datetime_ratio>= 0.9 :
                rows.append({"column":columns,"current_type":str(series.dtype),"suggested_type":"datetime","confidence":round(datetime_ratio*100,1)})
    return pd.DataFrame(rows,columns=["column","current_type","suggested_type","confidence"])


def correct_types(df:pd.DataFrame,correction:dict[str,str]) -> pd.DataFrame :
    cleaned = df.copy()
    type_log = []
    
    for column , target_type in correction.items() :
        column = resolve_column(cleaned,column)
        if column is None :
            continue 
        
        old_type = str(cleaned[column].dtype)
        
        if target_type == "numeric" :
            cleaned[column] = pd.to_numeric(cleaned[column],errors="coerce") # coerce = ถ้าแปลงข้อมูลไม่ได้ ให้เปลี่ยนค่านั้นเป็น NaN
        elif target_type == "boolean" :
            mapping = {"true":True,"false":False,"True":True,"False":False}
            cleaned[column] = (cleaned[column].astype(str).str.strip().str.lower().map(mapping).astype("boolean"))
        elif target_type == "integer" :
            numeric = pd.to_numeric(cleaned[column],errors="coerce")
            cleaned[column] = numeric.astype("Int64")
        elif target_type == "datetime" :
            cleaned[column] = pd.to_datetime(cleaned[column],errors="coerce")
        elif target_type == "string" :
            cleaned[column] = cleaned[column].astype("string")
            
        new_type = str(cleaned[column].dtype)
        type_log.append({"column": column,"old_type": old_type,"new_type": new_type,})
    return cleaned , type_log