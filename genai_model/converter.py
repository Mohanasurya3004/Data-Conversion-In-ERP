import os
import pandas as pd
import xmltodict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_input_file(filepath):
    ext = filepath.split('.')[-1].lower()
    if ext == 'csv':
        df = pd.read_csv(filepath)
    elif ext == 'json':
        df = pd.read_json(filepath)
    elif ext in ['xls', 'xlsx']:
        df = pd.read_excel(filepath)
    elif ext == 'xml':
        with open(filepath, 'r') as f:
            xml_data = f.read()
        data_dict = xmltodict.parse(xml_data)
        df = pd.json_normalize(data_dict)
    else:
        raise ValueError("Unsupported file type.")
    return df

def clean_data(df):
    df.drop_duplicates(inplace=True)
    df.fillna("N/A", inplace=True)  # Or use df.fillna(method='ffill') for forward-fill
    return df

def convert_data(input_path, output_path):
    try:
        df = load_input_file(input_path)
        df = clean_data(df)
        input_content = df.to_csv(index=False)

        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        prompt = f"""
        You are an expert in Odoo ERP data migration.

        Given this legacy data in CSV:
        {input_content}

        Convert it into Odoo-compatible format for the `res.partner` model.
        Use the following fields only:
        - name
        - phone
        - email
        - street
        - city
        - zip
        - country_id
        - is_company

        Return the converted data in CSV format.
        """

        response = model.generate_content(prompt)
        output = response.text.strip()

        with open(output_path, 'w') as f:
            f.write(output)

    except Exception as e:
        raise RuntimeError(f"Conversion error: {str(e)}")
