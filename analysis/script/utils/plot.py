import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import igviz as ig
import re
import plotly.graph_objects as go
import os
import time
from matplotlib import font_manager, rc
def parse_data(df, type = 4):
    '''
    Description:
        거래 형식에 따라 데이터를 반환하는 함수

    :param df: dataframe
    :param type (int):

            type == 1 : 판래처와 구매처
            type == 2 : 판래처
            type == 3 : 구매처
            type == 4 : 매출규모 top5

    :return: type에 따라 그래프를 그리기 위한 요소들이 반환됨

             type 1-3 : 기업체 별로의 connection 관계 반환
             type 4 : 기업체 별 node 리스트 , 연결 정보 리스트 , 거래 규모 리스트 , top5 기업이름
    '''
    # 업체명이나 거래처명이 0번 초과해서 언급된 것들 select 하기
    selected = [k for k, v in zip(Counter(df['업체명'].tolist() + df['거래처명'].tolist()).keys(),
                                  Counter(df['업체명'].tolist() + df['거래처명'].tolist()).values()) if v > 0]

    if type == 1:
        ## 1. 거래처 구매처 모두 합한 것
        temp = df[df['거래구분'] == '판매처']
        cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        temp = df[df['거래구분'] == '구매처']
        cnt += [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        return cnt

    if type == 2:
        # 선택된 곳중에서 거래가 판매처인 곳의 금액을 가중치로 넘기기
        temp = df[df['거래구분'] == '판매처']
        cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        return cnt

    if type == 3:
        # 선택된 곳중에서 거래가 구매처인 곳의 금액을 가중치로 넘기기
        temp = df[df['거래구분'] == '구매처']
        cnt = cnt = [(a, b) for a, b in zip(temp['업체명'], temp['거래처명']) if (a in selected) & (b in selected)]
        return cnt

    if (type == 4) or (type == 5):
        # 구매처가 top5인 부분만 남기기
        if type == 4:
            temp = df[df['거래구분'] == '구매처']
        if type == 5:
            temp = df[df['거래구분'] == '판매처']

        top5 = temp.groupby(['업체명']).sum()['거래금액'].sort_values(ascending=False).index[:5]

        cnt_list = []
        w_list = []
        node_list = []

        # top5 기업들의 node , cnt , w , 이름들을 반환하기 위한 iteration
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

class Network_graph():
    def __init__(self , df , show = True):
        '''
        Description:
            Network그래프를 그리기 위한 class
            화살표가 있는 top5 network graph function 과
            화살표가 없는 일반 network graph function 으로 나뉨

        :param df: dataframe
        :param show (boolean): 그래프를 저장만할지, inline plotting도 할지에 대한 param
        '''
        self.df = df
        self.show = show

    # network시각화 중 node plot을 그리기 위한 함수
    def _get_node_trace(self , G , company):

        node_x = []
        node_y = []
        # networkx 를 활용해 그려진 Grpah 의 노드 Position 을 얻기 위한 iteration
        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)

        # plotly를 활요한 graph 그리기
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

        # Graph를 활용해 node 의 color와 text size 받아오기
        for node, adjacencies in enumerate(G.adjacency()):
            if adjacencies[0] == company:
                node_adjacencies.append(5)
                node_size.append(70)
            else:
                node_size.append(50)
                node_adjacencies.append(4)
            node_text.append(adjacencies[0])

        # color , text , size 설정
        node_trace['marker']['color'] = node_adjacencies
        node_trace['text'] = node_text
        node_trace['marker']['size'] = node_size

        return node_trace

    # network시각화 중 edge plot을 그리기 위한 함수
    def _get_edge_trace(self , G  , weight):
        #### make edge
        edge_x = []
        edge_y = []
        annotation_list = []

        # networkx 를 활용해 그려진 Grpah 의 엣지 Position 을 얻기 위한 iteration
        for i, edge in enumerate(G.edges()):
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

            # weight 값의 크기에 따라서 edge를 다르게 표현하기 위해 edge별로 각각 그려서 annotation_list를 만듦
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

    # type 1-3 의 경우에 사용되는 기본 함수 (arrow 없는 버전)
    def _make_normal_plot(self , cnt ):

        # networkx로 기본적인 graph를 그림
        G = nx.DiGraph()
        G.add_edges_from(cnt, relation='cnt')
        pos = nx.spring_layout(G)  # 각 노드, 엣지의 position 정보
        data = nx.draw_networkx_edges(G, pos, edgelist=cnt)
        plt.close()

        edge_x = []
        edge_y = []

        # networkx로 그린 edge를 plotly형식에 맞게 변환하는 iteration
        for data_i in data:
            x0, y0 = data_i._posA_posB[0]
            x1, y1 = data_i._posA_posB[1]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        # plotly를 활용해 scatter plot을 그림
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_text = []

        # networkx로 그린 node를 plotly형식에 맞게 변환하는 iteration
        for key, value in pos.items():
            x, y = value[0], value[1]
            node_x.append(x)
            node_y.append(y)
            node_text.append(key)

        # plotly를 활용해 scatter plort을 그림
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                colorscale='purp',
                reversescale=True,
                line_width=2)
            , textposition="top center"
        )

        # set trace attribution
        node_trace['marker']['color'] = 70
        node_trace['text'] = node_text

        return edge_trace , node_trace

    # type에 따라 그리는 function
    # type 1-3 : 일반 plot
    # type 4 : top5 plot
    def plot(self , title , type):

        if (type == 4) or (type == 5):
            node_list, cnt_list, w_list, top5 = parse_data(self.df , type )

            # top5 별로 그래프를 각각 그림 즉 5개 return
            for i in range(len(top5)):
                cnt , w  = cnt_list[i] , w_list[i]
                G = nx.DiGraph()

                # Add nodes:
                nodes = node_list[i]
                G.add_nodes_from(nodes)

                # Add edges or links between the nodes:
                edges = cnt
                G.add_edges_from(edges)
                ig.plot(G, size_method="static")

                # get edge and node
                edge_traces , annotation_list = self._get_edge_trace(G , w)
                node_trace = self._get_node_trace(G , top5[i])

                if type == 4:
                    text = f'{title} {top5[i]} 구매처 rank {i}'
                if type == 5:
                    text = f'{title} {top5[i]} 판매처 rank {i}'

                # edge trace 와 Node를 활용해
                fig = go.Figure(
                            data= [*edge_traces , node_trace],
                             layout=go.Layout(
                                title= text,
                                titlefont_size=16,
                                                showlegend=False,
                                margin=dict(b=20,l=5,r=5,t=40),
                                xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=True, zeroline=False, showticklabels=False)),
                                )
                fig.update_layout(
                    annotations = annotation_list
                )
                fig.write_image(f'../output/{title}_{top5[i]}_rank_{i}.jpg')

                if self.show == False:
                    plt.close()
                else:
                    fig.show()

        if type != 4:
            # get 연결 리스트
            cnt = parse_data(self.df , type )
            edge_trace , node_trace = self._make_normal_plot(cnt)

            # edge , node로 그래프 그리기
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                title= f'{title} network',
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            )

            fig.update_layout(width=1000,
                              height=1000, )
            fig.write_image(f'../output/{title}.jpg')

            if self.show == False:
                plt.close()
            else:
                fig.show()