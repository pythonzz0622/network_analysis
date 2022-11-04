import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import re
import plotly.graph_objects as go
from matplotlib import font_manager, rc
rc('font', family='AppleGothic')

def get_data():

    raw = pd.read_excel('../data/다시최종_경남2.xlsx')
    # 이상치 제거
    raw = raw[raw['거래금액'] > 0]
    raw['사업분야'].value_counts()

    # 주 제거
    raw['업체명'] = raw['업체명'].apply(lambda x: re.sub('\(주\)', '', x))
    raw['거래처명'] = raw['거래처명'].apply(lambda x: re.sub('\(주\)', '', x))

    # 업체명의 사업분야가 IT제조이면서 사업분야가 IT제조인거 가져오기
    raw = raw[(raw['업체명_사업분야'] == '1.IT제조') & (raw['사업분야'] == '1.IT제조')]

    # 업체명이나 거래처명이 0번 초과해서 언급된 것들 select 하기
    selected = [k for k, v in zip(Counter(raw['업체명'].tolist() + raw['거래처명'].tolist()).keys(),
                                  Counter(raw['업체명'].tolist() + raw['거래처명'].tolist()).values()) if v > 0]

    # 선택된 곳중에서 거래가 판매처인 곳의 금액을 가중치로 넘기기
    temp = raw[raw['거래구분'] == '판매처']
    cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
    w = temp['거래금액'].tolist()

    # 선택된 곳중에서 거래가 구매처인 곳의 금액을 가중치로 넘기기
    temp = raw[raw['거래구분'] == '구매처']
    cnt = cnt + [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
    w = w + temp['거래금액'].tolist()

    temp = raw[raw['거래구분'] == '구매처']
    top5 = temp.groupby(['업체명']).sum()['거래금액'].sort_values(ascending=False).index[:5]

    for f in top5:
        temp2 = temp[temp['업체명'] == f]
        acc_list = temp2['거래처명'].tolist()
        acc_list.append(f)

        temp2 = temp[temp['업체명'].isin(acc_list)]
        cnt = [(b, a) for a, b in zip(temp2['업체명'], temp2['거래처명'])]
        w = temp2['거래금액'].tolist()
        w = [(sorted(w).index(i) + 1) * 1.5 for i in w]

        plt.figure(figsize=(10, 10))
        G = nx.DiGraph()

        G.add_edges_from(cnt, relation='cnt')

        pos = nx.spring_layout(G)  # 각 노드, 엣지를 draw하기 위한 position 정보
        pos[f] = np.array([0, 0])
        # nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=['yellow' if i == f else 'gray' for i in pos.keys()])
        # nx.draw_networkx_edges(G, pos, edgelist=cnt, arrowstyle='-|>', arrowsize=50, width=w, edge_color='lightgray')
        # if f == '유니온':
        #     break
        cnt, w, pos, G

    return cnt , w, pos , G

def get_node_trace(G):
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=[50 ,70 , 50 , 50 , 50 , 50 , 50],
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    node_adjacencies = []
    node_text = []
    node_size = []
    for node, adjacencies in enumerate(G.adjacency()):
        if adjacencies[0] == '정민기전':
            node_adjacencies.append(5)
            node_size.append(70)
        else:
            node_size.append(50)
            node_adjacencies.append(1)
        node_text.append(adjacencies[0])

    node_trace['marker']['color'] = node_adjacencies
    node_trace['text'] = node_text
    node_trace['marker']['size'] = node_size

    return node_trace


def get_edge_trace(G):
    #### make edge
    edge_x = []
    edge_y = []
    annotation_list = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

        annotation_list.append(
            dict(
                ax=G.nodes[edge[0]]["pos"][0],
                ay=G.nodes[edge[0]]["pos"][1],
                axref="x",
                ayref="y",
                x=G.nodes[edge[1]]["pos"][0] * 0.85
                  + G.nodes[edge[0]]["pos"][0] * 0.15,
                y=G.nodes[edge[1]]["pos"][1] * 0.85
                  + G.nodes[edge[0]]["pos"][1] * 0.15,
                xref="x",
                yref="y",
                showarrow=True,
                arrowhead=1,
                arrowsize=2
            )
        )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    return edge_trace