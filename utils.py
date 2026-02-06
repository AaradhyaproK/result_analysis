import io
import pandas as pd
import datetime

def convert_df_to_excel(df):
    """
    Converts a pandas DataFrame to an Excel binary stream using xlsxwriter.
    Includes FIX for ValueError: Excel does not support datetimes with timezones.
    """
    output = io.BytesIO()
    
    # --- TIMEZONE FIX START ---
    df_export = df.copy()
    for col in df_export.columns:
        if df_export[col].dtype == object:
            try:
                df_export[col] = df_export[col].apply(
                    lambda x: x.replace(tzinfo=None) if isinstance(x, (datetime.datetime, pd.Timestamp)) else x
                )
            except Exception:
                pass
        if pd.api.types.is_datetime64_any_dtype(df_export[col]):
            df_export[col] = df_export[col].dt.tz_localize(None)
    # --- TIMEZONE FIX END ---

    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Sheet1')
    except Exception as e:
        df_export.to_excel(output, index=False)
            
    return output.getvalue()

def flatten_student_data_for_export(students_data):
    """
    Flattens the nested student objects for a clean Excel export.
    """
    flat_data = []
    for s in students_data:
        row = {
            'Seat No': s.get('Seat No'),
            'PRN': s.get('PRN'),
            'Name': s.get('Name'),
            'Mother Name': s.get('Mother Name'),
            'SGPA': s.get('SGPA'),
            'Result Status': s.get('Result Status'),
            'Total Credits': s.get('Credits'),
            'Passed Subjects': s.get('Passed Subjects'),
            'Total Subjects': s.get('Total Subjects'),
            'Failed Count': s.get('Total Subjects', 0) - s.get('Passed Subjects', 0)
        }
        flat_data.append(row)
    return pd.DataFrame(flat_data)