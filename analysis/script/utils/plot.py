import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import igviz as ig
import re
import plotly.graph_objects as go
from matplotlib import font_manager, rc

def preprocessing(data_path , b_a , b_a_2 , loc):
    raw = pd.read_excel(data_path)
    # 이상치 제거
    if loc == '경남':
        raw = raw[raw['시도'] == '경남']

    raw = raw[raw['거래금액'] > 0]
    raw['사업분야'].value_counts()

    # 주 제거
    raw['업체명'] = raw['업체명'].apply(lambda x: re.sub('\(주\)', '', x))
    raw['거래처명'] = raw['거래처명'].apply(lambda x: re.sub('\(주\)', '', x))

    # 업체명의 사업분야가 IT제조이면서 사업분야가 IT제조인거 가져오기
    raw = raw[(raw['업체명_사업분야'] == b_a) & (raw['사업분야'] == b_a_2)]

    ## 기업 규모에 따른 나누기
    ## raw = raw[raw['업체명사업체규모'] == '벤처기업']
    return raw

def get_data(raw, type = 4):
    # 업체명이나 거래처명이 0번 초과해서 언급된 것들 select 하기
    selected = [k for k, v in zip(Counter(raw['업체명'].tolist() + raw['거래처명'].tolist()).keys(),
                                  Counter(raw['업체명'].tolist() + raw['거래처명'].tolist()).values()) if v > 0]

    if type == 1:
        ## 1. 거래처 구매처 모두 합한 것
        temp = raw[raw['거래구분'] == '판매처']
        cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        temp = raw[raw['거래구분'] == '구매처']
        cnt += [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        return cnt

    if type == 2:
        # 선택된 곳중에서 거래가 판매처인 곳의 금액을 가중치로 넘기기
        temp = raw[raw['거래구분'] == '판매처']
        cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        return cnt

    if type == 3:
        # 선택된 곳중에서 거래가 구매처인 곳의 금액을 가중치로 넘기기
        temp = raw[raw['거래구분'] == '구매처']
        cnt = cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        return cnt

    if type == 4:
        # 구매처가 top5인 부분만 남기기
        temp = raw[raw['거래구분'] == '구매처']
        top5 = temp.groupby(['업체명']).sum()['거래금액'].sort_values(ascending=False).index[:5]

        cnt_list = []
        w_list = []
        node_list = []
        for f in top5:
            temp2 = temp[temp['업체명'] == f]
            acc_list = temp2['거래처명'].tolist()
            acc_list.append(f)

            temp2 = temp[temp['업체명'].isin(acc_list)]
            cnt = [(b, a) for a, b in zip(temp2['업체명'], temp2['거래처명'])]
            w = temp2['거래금액'].tolist()
            w = [(sorted(w).index(i) + 1) * 1.5 for i in w]

            cnt_list.append(cnt)
            w_list.append(w)

            data_list = []
            for cn in cnt:
                data_list.append(cn[0])
                data_list.append(cn[1])
            data_list = list(set(data_list))
            node_list.append(data_list)

        return node_list, cnt_list, w_list, top5

class graph_top5():
    def __init__(self , raw , type):
        if type ==4:
            self.node_list , self.cnt_list , self.w_list , self.top5 = get_data(raw , type)
        else:
            self.cnt = get_data(raw , type)

    def _get_node_trace(self , G , company):

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
                colorscale='YlGnBu',
                        reversescale=True,
                line_width=2)
            , textposition="top center"
        )
        node_adjacencies = []
        node_text = []
        node_size = []
        for node, adjacencies in enumerate(G.adjacency()):
            if adjacencies[0] == company:
                node_adjacencies.append(5)
                node_size.append(70)
            else:
                node_size.append(50)
                node_adjacencies.append(4)
            node_text.append(adjacencies[0])

        node_trace['marker']['color'] = node_adjacencies
        node_trace['text'] = node_text
        node_trace['marker']['size'] = node_size

        return node_trace

    def _get_edge_trace(self , G  , weight):
        #### make edge
        edge_x = []
        edge_y = []
        annotation_list = []
        for i, edge in enumerate(G.edges()):
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
                    arrowhead=3,
                    arrowsize=weight[i] * 0.3
                )
            )

        x_link = np.array(edge_x).reshape(-1, 3).tolist()
        y_link = np.array(edge_y).reshape(-1, 3).tolist()

        # make multiple traces
        edge_traces = []
        for i in range(0, len(x_link)):
            edge_traces.append(
                go.Scatter(x=x_link[i],
                           y=y_link[i],
                           line=dict(
                               color='#4c72b0',
                               width=weight[i] * 0.5))
            )
        return edge_traces , annotation_list

    def top_5_plot(self):
        for i in range(len(self.top5)):
            cnt , w  = self.cnt_list[i] , self.w_list[i]
            G = nx.DiGraph()

            # Add nodes:
            nodes = self.node_list[i]
            G.add_nodes_from(nodes)

            # Add edges or links between the nodes:
            edges = cnt
            G.add_edges_from(edges)
            ig.plot(G, size_method="static")
            edge_traces , annotation_list = self._get_edge_trace(G , w)
            node_trace = self._get_node_trace(G , self.top5[i])

            fig = go.Figure(
                        data= [*edge_traces , node_trace],
                         layout=go.Layout(
                            title=f'{self.top5[i]} vs all',
                            titlefont_size=16,
                                            showlegend=False,
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=True, zeroline=False, showticklabels=False)),
                            )

            fig.update_layout(
                annotations = annotation_list
            )

            fig.show()

    def normal_plot(self , cnt):
        plt.figure(figsize=(20, 20))
        G = nx.DiGraph()

        G.add_edges_from(cnt, relation='cnt')

        pos = nx.spring_layout(G)  # 각 노드, 엣지를 draw하기 위한 position 정보
        relation = nx.get_edge_attributes(G, 'relation')

        # nx.draw(G,pos, with_labels=True, edge_color='white')
        nx.draw_networkx_edges(G, pos, edgelist=cnt, connectionstyle='arc3, rad = -0.2', arrowstyle='->', width=0.2)
        nx.draw_networkx_labels(G, pos, font_family='AppleGothic', font_size=10)
        plt.show()