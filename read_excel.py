import pandas as pd

xl = pd.ExcelFile('Libro de Inventario Art 177julioagosto.xlsx')
print('Sheets:', xl.sheet_names)
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f'Sheet: {sheet}')
    print(df.head())
    print('Columns:', df.columns.tolist())
    print('---')