import pandas as pd
import utils.plot as plot
import utils.prepro as prepro

DF = prepro.preprocessing('../data/다시최종_경남2.xlsx' )

# ploting package를 묶어서 한번에 보여주게 하는 function
def make_svg(raw , title):
    # Network_graph 객체를 생성
    obj =plot.Network_graph(raw , show = False)

    # 4가지 유형의 plot을 saving
    obj.plot(f'{title} 거래처 + 구매처' , 1)
    obj.plot(f'{title} 판매처' , 2)
    obj.plot(f'{title} 구매처' , 3)
    obj.plot(f'{title} top5 구매처' , 4)
    obj.plot(f'{title} top5 판매처', 5)

# 경남에서 business_are 별로 plot saving
bus_area = ['1.IT제조' , '3.SW' ,'2.IT서비스' ]
name = [x.split('.')[1] for x in bus_area]

for i , bus_i in enumerate(bus_area):
    raw_it = DF[(DF['업체명_사업분야'] == '1.IT제조') & (DF['사업분야'] == bus_i)]
    make_svg(raw_it, f'경남_IT_{name[i]}')

    raw_sw = DF[(DF['업체명_사업분야'] == '3.SW') & (DF['사업분야'] == '1.IT제조')]
    make_svg(raw_sw, f'경남_SW_{name[i]}')

    raw_acc = DF[DF['사업분야'] == bus_i]
    make_svg(raw_acc, f'경남_거래처_{name[i]}')

    raw_sv = DF[(DF['업체명_사업분야'] == '2.IT서비스') & (DF['사업분야'] == bus_i)]
    make_svg(raw_sv, f'경남_서비스_{name[i]}')

    raw_cm = DF[DF['업체명_사업분야'] == '1.IT제조']
    make_svg(raw_cm, f'경남_업체_{name[i]}')
    print(f'DF {bus_i} complete')

# 전국 data frame 불러오기
DF_A = prepro.preprocessing('../data/다시최종_전국.xlsx' )

scale = ['대기업' , '벤처기업', '중소기업']
# 전국의 모든 기업에 대해 plotting
for i , bus_i in enumerate(bus_area):
    # 사업 분야 별 plotting
    raw_a = DF_A[DF_A['업체명사업분야'] == bus_i]
    make_svg(raw_a, f'전국_전국_{name[i]}')

    # 사업체 규모별 plotting
    raw_a_s = DF_A[DF_A['업체명사업체규모'] == scale[i]]
    make_svg(raw_a_s, f'전국_전국_{scale[i]}')

    print(f'DF_A_1 {bus_i} complete')

# 전국중 경남 기업에 대해서 data frame 불러오기
DF_A_G = DF_A[DF_A['시도'] == '경남']
make_svg(DF_A_G, '전국_경남')

# 전국 중 경남기업에 대해 plotting
for i , bus_i in enumerate(bus_area):
    # 사업 분야 별 plotting
    raw_g_area = DF_A_G[DF_A_G['업체명사업분야'] == bus_i]
    make_svg(raw_g_area, f'전국_경남_{name[i]}')

    # 사업 규모별 plotting
    raw_g_s = DF_A_G[DF_A_G['업체명사업체규모'] == scale[i]]
    make_svg(raw_g_s, f'전국_경남_{scale[i]}')

    print(f'DF_A_2 {bus_i} complete')