"""Check categories in Excel file."""
import pandas as pd

df = pd.read_excel('Inventario Ferre-Exito.xlsx', skiprows=2)
print('Categorías únicas:')
print(df['Categoria'].unique()[:30])
print(f'\nTotal categorías: {df["Categoria"].nunique()}')
print(f'\nTotal productos: {len(df)}')

# Show some examples
print('\nEjemplos por categoría:')
for cat in df['Categoria'].unique()[:10]:
    examples = df[df['Categoria'] == cat][['Codigo', 'Descripcion del Articulo']].head(3)
    print(f'\n{cat}:')
    print(examples.to_string(index=False))
