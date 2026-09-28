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
                rows.append({"column":column,"current_type":str(series.dtypes),"suggested_dtype":suggested_type,"confidence":round(numeric_ratio*100,1)})
                continue 
            
        # text->Boolean 
        if is_text_like(series) :
            value = (series.dropna().astype(str).str.strip().str.lower())
            if value.empty :
                continue 
            boolean_values = {"true","false","yes","no"}
            boolean_ratio = value.isin(boolean_values).mean()
            if boolean_ratio >= 0.9 :
                rows.append("column":column,"current_type":str(series.dtype),"suggested_type":"boolean","confidence":round(boolean_ratio*100,1))
                continue 
        # text->    
            