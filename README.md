# network_analysis

경상국립대 연구실에서 기업 관련 네트워크 분석 프로젝트에서 사용한 코드 입니다.

기존의 networkx pakcage의 포맷의 plotting  형태가 분석 결과를 전달하기 용이하지 않아 

networkx plotting format에서 plotly format으로 customizing 하게 변환시킨 코드입니다,


## 실행방법
```
import utils.plot as plot
import utils.prepro as prepro

# dataframe 이상치 제거 후 불러오기
DF = prepro.preprocessing('../data/다시최종_경남2.xlsx')

# network plot을 그리기 위한 객체 생성
obj =plot.Network_graph(DF , show = True)

# 판매처에 대한 plot 형성
obj.plot(f'경남_IT_판매처' , 2)
# 거래규모 Top5에 대한 plot 형성
obj.plot(f'경남_IT_top5' , 4)

```

## Result
![image](https://user-images.githubusercontent.com/90737305/200571324-15dd06e8-4ba9-4b77-87a4-476aa96bd07c.png)

![image](https://user-images.githubusercontent.com/90737305/200571166-b4fb5159-37d6-4a7e-b36d-d0fd64200a4f.png)

