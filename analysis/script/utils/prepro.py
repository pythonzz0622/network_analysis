import pandas as pd
import re

def preprocessing(data_path):
    df = pd.read_excel(data_path)
    # 이상치 제거
    df = df[df['거래금액'] > 0]

    df['업체명'] = df['업체명'].astype('str')
    df['거래처명'] = df['거래처명'].astype('str')
    # 주 제거
    df['업체명'] = df['업체명'].apply(lambda x: re.sub('\(주\)', '', x))
    df['거래처명'] = df['거래처명'].apply(lambda x: re.sub('\(주\)', '', x))
    return df
