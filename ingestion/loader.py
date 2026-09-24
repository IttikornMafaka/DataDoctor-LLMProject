import os 
import pandas as pd 
from pathlib import Path

def load_csv(file_path:str) -> pd.DataFrame : #->list[Document] ส่งค่า return เป็น list document
    encoding_try = ["utf-8", "utf-8-sig", "tis-620", "cp874"]
    last_error = None #ตัวแปรไว้เก็บ error ล่าสุด
    for enc in encoding_try : #  loop ไว้ลองว่า ถ้าใช้ encoding_try แล้วว่าสามารถใช้ได้มั้ยถ้าไม่ได้ให้ส่งค่า error แล้วไปใช้ตัวถัดไป
        try :  # ให้ลองทำงานในนี้ถ้าเกิด error ที่เราระบุให้ไปทำงานใน except
            return pd.read_csv(file_path,encoding=enc)
        except UnicodeDecodeError as e : # UnicodeDecodeError : Error ที่เกิดขึ้นเมื่อ Python พยายามอ่านข้อมูลด้วย Encoding ที่ไม่ตรงกับ Encoding ของไฟล์
            last_error = e  # เก็บ error ใหม่ไว้ใน last_error
            continue
    raise last_error    # ถ้าลอง Encoding ทุกตัวแล้วไม่มีตัวไหนอ่านสำเร็จ ให้แสดง Error ล่าสุดออกมา          

''' 
Code เปรียบเทียบ
try  ลองใช้กุญแจ
except กุญแจใช้ไม่ได้
last_error = e เก็บสาเหตุที่กุญแจใช้ไม่ได้
continue เปลี่ยนไปลองกุญแจดอกถัดไป
return เปิดประตูได้ สำเร็จและจบ
raise last_error กุญแจทุกดอกใช้ไม่ได้ จึงแจ้งปัญหาสุดท้าย
'''

def load_excel(file_path:str) -> pd.DataFrame :
    return pd.read_excel(file_path)

def load_document(file_path:str) -> pd.DataFrame :
    
    path = Path(file_path)
    if not path.exists() :
        raise FileNotFoundError(f"File not found : {file_path}")
    
    ext = path.suffix.lower() #แบ่งไฟล์เป็น 2 ส่วน เลือกข้อมูลจากนามสกุล ตามเลข index
    if ext == '.csv' :
        return load_csv(file_path) 
    elif ext in ['.xlsx','.xls'] :
        return load_excel(file_path)
    else :
        raise ValueError(f"Unsupported file type or extension: {ext}")