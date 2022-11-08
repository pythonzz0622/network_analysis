import pandas as pd
import re

def preprocessing(data_path):
    raw = pd.read_excel(data_path)
    # 이상치 제거
    raw = raw[raw['거래금액'] > 0]

    # 주 제거
    raw['업체명'] = raw['업체명'].apply(lambda x: re.sub('\(주\)', '', x))
    raw['거래처명'] = raw['거래처명'].apply(lambda x: re.sub('\(주\)', '', x))
    return raw
