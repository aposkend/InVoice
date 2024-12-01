# forms.py
import pandas as pd
import openpyxl
from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise forms.ValidationError('Invalid file format. Only CSV, XLSX, and XLS files are allowed.')

        # Load the file into a pandas DataFrame
        if file.name.lower().endswith('.csv'):
            try:
                df = pd.read_csv(file)
            except Exception as e:
                raise forms.ValidationError(f'Error reading CSV file: {e}')
        else:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                raise forms.ValidationError(f'Error reading Excel file: {e}')

        # Check if required columns exist
        required_columns = [
            'user_id', 'datetime', 'inv_num', 'item_name', 'unit_price', 'quantity', 'amount', 'item_brand_name',
            'store_brand_name', 'county', 'city_area'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise forms.ValidationError(f'Missing columns in the file: {", ".join(missing_columns)}')

        # Reset the file pointer to the beginning after reading
        file.seek(0)

        return file
