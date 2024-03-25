from pandas import DataFrame

def dataframe_validation(df: DataFrame) -> DataFrame:
    column_renames = {}
    if 'ean' in df.columns:
        column_renames['ean'] = 'EAN'
    if 'Price' in df.columns:
        column_renames['Price'] = 'price'
    if 'PRICE' in df.columns:
        column_renames['PRICE'] = 'price'

    if column_renames:
        df.rename(columns=column_renames, inplace=True)
    
    # dropping the null values
    if df['EAN'].isnull().any():
        df.dropna(subset=['EAN'], inplace=True)
    if df['price'].isnull().any():
        df.dropna(subset=['price'], inplace=True)
    
    return df