import pandas as pd
import utils.plot as plot
import utils.prepro as prepro


def make_svg(raw, title):
  # Network_graph 객체를 생성
  obj = plot.Network_graph(raw, show=False)

  # 4가지 유형의 plot을 saving
  obj.plot(f'{title} 거래처 + 구매처', 1)
  obj.plot(f'{title} 판매처', 2)
  obj.plot(f'{title} 구매처', 3)
  obj.plot(f'{title} top5 구매처', 4)
  obj.plot(f'{title} top5 판매처', 5)
# # 전국 data frame 불러오기
DF_A = prepro.preprocessing('../data/다시최종_전국.xlsx' )

# 전국 plotting
make_svg(DF_A, '전국_전국')

df = prepro.preprocessing('../data/최종_사업체정리완료_전국.xlsx')

df_area = df[['빅데이터사업' , '인공지능(AI)사업' , '블록체인사업' , 'IoT사업' ,
              '클라우드사업' , '실감콘텐츠사업' , '자율주행차', '무인이동체']]

df_ICT = df[df_area.isnull().sum(axis = 1) != 8]
df_big = df_ICT[df_ICT['산업분류'] != '기타']
df_ai = df_big[(df_big['산업분류'] == '에너지') | (df_big['산업분류'] == '신산업')]

make_svg(df_big, '빅데이터')
make_svg(df_ai, 'AI')
