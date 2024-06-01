# Python3 program to implement
do_not_show_plot_just_save=0
start_node_name=78# Initial point, source, the 6 is the initial point in this case, mines 1 to execute the movement for one node to another.
goal_node_name=24# Final point,sink , the 6 is the initial point in this case, mines 1 to execute the movement for one node to another.
time = 800  # Set up the time in Seconds
pathData="C:\\Projects\\Arduino-Python_sensor_datalink-KorCleanup\\2024-05-25_16-15_data.xlsx"

image_path='C:\\Projects\\Arduino-Python_sensor_datalink-KorCleanup\\Sensor_layout.png'

import os
os.chdir("C:\\Projects\\Arduino-Python_sensor_datalink-KorCleanup")
import sys
sys.path.insert(0,"C:\\Projects\\Arduino-Python_sensor_datalink-KorCleanup")
import os.path
import tkinter.messagebox
#import time
from sys import maxsize
from typing import List
import numpy as np
# ploting
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import openpyxl as xl
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import matplotlib.cm as cm
import matplotlib.animation as animation
import shutil
import subprocess
import heapq
import networkx as nx
import Modules.functions as func

#1. Maximization of the number of data
config = func.open_file("config")
global y ,x, v, MIN, MAX, selectedParm, ppi, nodeNames, grph, weights, sensorSX, sensorSY, sensor_value, parameterToAnalyze, main_node, cost


y=x=v=ppi=nodeNames=sensorSX=sensorSY=main_node=parameterToAnalyze=[]
grph= weights={}

img = mpimg.imread( image_path   )  # (This file must be part of the folder where the code is running)


def findSensorCoordinates(coord):
    for pos in enumerate(config['Button_Coordinates']):
        if coord in pos[1]:
            return pos[1]


def readPythonSpreadSheet(pathData,parameterIndex=3,time=60):
    global y, x, v, MIN, MAX, selectedParm, ppi, nodeNames, grph, weights, sensorSX, sensorSY, sensor_value, parameterToAnalyze, main_node, cost

    df = pd.read_excel(pathData,
                       sheet_name='Data', engine='openpyxl')# Importation of the data base by collecting in VentSim

    sensorsTime = df.values[1:, 0]
    difference_array = np.absolute(sensorsTime - time)
    # 6.1 Find the index of minimum element from the array
    indexOfTime = difference_array.argmin()
    AllParameters = ['Airflow (m3_s)', 'Air Velocity (m_s)', 'Temperature (C)', 'Gas (ppm)']  # 'Airflow m³/s','Velocity m/s','Temp Wet Bulb ºC','Visibility m','O2  %' (in this step multiple varibles could be selected, the risks in the emergency)
    k_parm=parameterIndex
    parameterToAnalyze=AllParameters[k_parm]
    #for indexOfTime in range(1,(df.values).shape[0]-1):
    selectedParm=AllParameters[k_parm]
    a=df.columns.values
    ppi=[]

    for k in range(len(df.columns)):
        if selectedParm==df.columns.T[k].split('.')[0]:
            ppi.append(k)
    MIN=1E9
    MAX=-1E9
    for k in ppi :
        for kk in range(2,np.size(df.values,0)):
            if k-1>0 and np.isnan(df.values[kk,k]):
                df.values[kk, k]=df.values[kk-1,k]
            if k-1>0 and k_parm==2 and ((df.values[kk,k])>90 or df.values[kk,k]<5):
                df.values[kk, k]=df.values[kk-1,k]
            if int(df.values[kk,k])!=100 and MIN>float(df.values[kk,k]):
                MIN=df.values[kk,k]
            if int(df.values[kk,k])!=100 and MAX<float(df.values[kk,k]):
                MAX=df.values[kk,k]
    if k_parm==3:
        MAX=3000
    Xi=df.values[0,:]
    names=df.columns[1:].T

    Vi=df.values[indexOfTime+1,0:]
    x=[]
    y=[]
    v=[]
    nodeNames=[]
    nodeContents=[]
    i=0
    for k in ppi:
            #xi=Xi[k].split("-")[0]
            #yi = Xi[k].split("-")[1]
            found=False
            for kk in range(len(config['Button_Coordinates'])):
                if found==False and Xi[k]==config['Button_Coordinates'][kk][2]:
                    xi=config['Button_Coordinates'][kk][0]
                    yi = config['Button_Coordinates'][kk][1]
                    nodeNames_i=config['Button_Coordinates'][kk][4]
                    nodeContents_i = config['Button_Coordinates'][kk][3]
                    found=True
            #if found == False:
                #xi = Xi[k].split("-")[0]
                #yi = Xi[k].split("-")[1]
            vi=Vi[k]
            x.append(int(xi))
            y.append(int(yi))
            nodeNames.append(nodeNames_i)
            nodeContents.append(nodeContents_i)
            if vi==100:
                vi=0
            v.append(vi)

def dataWeigh(val):
    hardness=0
    if val>=0 and val<9:
        hardness=0
    elif val>=9 and val<25:
        hardness = 0.1
    elif val>=25 and val<500:
        hardness = 0.3
    elif val>=500 and val<1000:
        hardness = 0.5
    elif val>=1000 and val<2000:
        hardness = 0.75
    elif val>=2000 and val<3000:
        hardness = 0.95
    elif val>=3000 :
        hardness = 1
    return hardness

INF = maxsize // 2 - 1
def plot_excel_dta_only():
    fig = plt.figure()
    plt.imshow(img)  # , extent=(.1, 32, .1, 16) -45445.00,-45142.00,-3006075.00,-3005450.00
    plt.scatter( y,x, s=175, marker="o", c=v, vmin=MIN, vmax=MAX)
    cbar = plt.colorbar(format=ticker.FuncFormatter(myfmt))
    cbar.set_label(selectedParm, rotation=90, fontsize=15, fontweight="bold")
    cbar.ax.tick_params(labelsize=15)
    plt.rcParams.update({'font.size': 14})

def searchNode(sensor_i):

    search_connection_node=1
    global  ppi, nodeNames

    sensor_i_index=[]
    for kkk in range(len(config['Node_Connections'])):
        if search_connection_node and config['Node_Connections'][kkk][0] == sensor_i:
            search_connection_node = 0
            sensor_i_index = kkk
            break
    search_data_node=1
    sensor_data_index=[]
    for kkk in range(len(nodeNames)):
        if search_data_node and nodeNames[kkk] == sensor_i:
            search_data_node = 0
            sensor_data_index = kkk
            break
    search_data_coordinate=1
    button_data_index=[]
    for kkk in range(len(config['Button_Coordinates'])):
        if search_data_coordinate and config['Button_Coordinates'][kkk][4] == sensor_i:
            search_data_node = 0
            button_data_index = kkk
            break
    return sensor_i_index,sensor_data_index,button_data_index
def capacityBuilding():
        weight_i=-1
        global y, x, v, MIN, MAX, selectedParm, ppi, nodeNames, grph, weights, sensorSX, sensorSY, sensor_value, parameterToAnalyze, main_node, cost

        MAXsensorsData = max(np.max(v),1000)
        if weight_i < 0:
            v_for_algorithm = (MAXsensorsData - np.array(v))/MAXsensorsData
            v_for_algorithm[v_for_algorithm<0]=0
        for k in range(len(v_for_algorithm)):
            v_for_algorithm[k]=(1-dataWeigh(v[k]))*10
        cap = np.zeros((len(config['Node_Connections']), len(config['Node_Connections'])))
        cost = np.ones((len(config['Node_Connections']), len(config['Node_Connections'])))
        expos_sensors=np.zeros((len(config['Node_Connections']), len(config['Node_Connections'])))
        sensor_value=[]
        main_node=[]
        sensorSY=[]
        sensorSX=[]
        for k in range(np.size(cap,axis=0)):
            main_node_i = config['Node_Connections'][k][0]
            main_node_i_index, main_sensor_data_i_index,main_button_data_index = searchNode(main_node_i)
            if main_sensor_data_i_index or main_sensor_data_i_index==0:
                main_node.append(main_node_i)
                sensor_value.append(v[main_sensor_data_i_index])
                sensorSY.append(float(config['Button_Coordinates'][main_button_data_index][0]))
                sensorSX.append(float(config['Button_Coordinates'][main_button_data_index][1]))
            else:
                main_node.append(main_node_i)
                sensor_value.append(-1)
                sensorSY.append(-1e4)
                sensorSX.append(-1e4)

            for kn in range(1,len(config['Node_Connections'][k])):
                connection_node_i = config['Node_Connections'][k][kn]
                for kk in range(len(config['Button_Coordinates'])):
                    sensor_i=config['Button_Coordinates'][kk][4]
                    sensor_connection_i_index=[]
                    if sensor_i==connection_node_i:
                        sensor_connection_i_index,sensor_data_connection_index,button_data_index=searchNode(sensor_i)
                        break
                if (sensor_data_connection_index or sensor_data_connection_index==0) and 'G' in  config['Button_Coordinates'][sensor_connection_i_index][3]:
                    cap[main_node_i_index,sensor_connection_i_index]=v_for_algorithm[sensor_data_connection_index]
                    expos_sensors[main_node_i_index,sensor_connection_i_index] = v[sensor_data_connection_index]
        sensorSY[64]=135
        sensorSY[65] = 135
        sensorSX[64]=918
        sensorSX[65] = 946
        return  cap,expos_sensors,sensorSX,sensorSY

def graph_Weighted_A_Star():
    weight_i = 1
    global y, x, v, MIN, MAX, selectedParm, ppi, nodeNames, grph, weights, sensorSX, sensorSY, sensor_value, parameterToAnalyze, main_node, cost

    MAXsensorsData = max(np.max(v), 1000)
    if weight_i < 0:
        v_for_algorithm = (MAXsensorsData - np.array(v)) / MAXsensorsData
        v_for_algorithm[v_for_algorithm < 0] = 0
    else:
        v_for_algorithm=np.array(v)
    for k in range(len(v_for_algorithm)):
        v_for_algorithm[k] = (1 + dataWeigh(v[k])) * 10
    grph = {}
    # weights defined for each node
    weights = {}
    for k in range(len(config['Node_Connections'])):
        main_node_i = config['Node_Connections'][k][0]
        main_node_i_index, main_sensor_data_i_index, main_button_data_index = searchNode(main_node_i)
        if (main_sensor_data_i_index or main_sensor_data_i_index == 0):
            sensorSY_i=(float(config['Button_Coordinates'][main_button_data_index][1]))
            sensorSX_i=(float(config['Button_Coordinates'][main_button_data_index][0]))
            grph_i = {(sensorSX_i, sensorSY_i): {}}
            weights.update({(sensorSX_i, sensorSY_i): v_for_algorithm[main_sensor_data_i_index]})
        else:
            sensorSY_i=(-1e4)
            sensorSX_i=(-1e4)

        for kn in range(1, len(config['Node_Connections'][k])):
            connection_node_i = config['Node_Connections'][k][kn]
            for kk in range(len(config['Button_Coordinates'])):
                sensor_i = config['Button_Coordinates'][kk][4]
                sensor_connection_i_index = []
                if sensor_i == connection_node_i:
                    sensor_connection_i_index, sensor_data_connection_index, button_data_index = searchNode(sensor_i)
                    break
            if (sensor_data_connection_index or sensor_data_connection_index == 0):
                sensorSY_in = (float(config['Button_Coordinates'][button_data_index][1]))
                sensorSX_in = (float(config['Button_Coordinates'][button_data_index][0]))
            else:
                sensorSY_in = (-1e4)
                sensorSX_in = (-1e4)
            if (main_sensor_data_i_index or main_sensor_data_i_index==0) and (sensor_data_connection_index or sensor_data_connection_index==0) and 'G' in  config['Button_Coordinates'][sensor_connection_i_index][3]:
                grph_i[sensorSX_i, sensorSY_i].update({(sensorSX_in,sensorSY_in):v_for_algorithm[sensor_data_connection_index]})
        grph.update(grph_i)
    return grph,weights




def weighted_a_star(graph, start, goal, heuristic, weight=1.0, weights=None):
    if weights is None:
        weights = {node: 1.0 for node in graph}

        # assign default weight to nodes not in weights
        for node in graph:
            if node not in weights:
                weights[node] = 1.0

    open_list = []  # min-heap, priority queue that stores nodes for evaluation
    heapq.heappush(open_list, (0, start))  # add starting node to the 'open_list' with a priority of zero
    came_from = {}  # dictionary to track best path to each node
    g_score = {
        start: 0}  # dictionary that holds the cost of the dheapest path from the start node to each node. Cost for start node is initialized to zero
    f_score = {start: heuristic(start,
                                goal)}  # dictionary that holds the estimated total cost (current cost + heuristic) from the start node to the goal through each node. The start node's f_score is initialized to the heuristic value from the start to the goal.

    while open_list:  # loop runs as long as there is no node to be evaluated
        current = heapq.heappop(open_list)[
            1]  # pops the node with the lowest 'f_score' from 'open_list' and sets it as 'current'

        if current == goal:
            return reconstruct_path(came_from,
                                    current)  # If the current node is the goal node, the function reconstructs and returns the path from the start to the goal using the came_from dictionary

        for neighbor, cost in graph[current].items():  # iterate over each node
            tentative_g_score = g_score[current] + cost * weights.get(neighbor,
                                                                      1.0)  # calculate cost to reach neighbor node through current node

            if neighbor not in g_score or tentative_g_score < g_score[
                neighbor]:  # update path information if neighbor has not been evaluated or neighbor is cheaper than any path previously recorded
                came_from[neighbor] = current  # records that the best path to the neighbor is through the current node
                g_score[neighbor] = tentative_g_score  # update cost to reach neighbor
                f_score[neighbor] = tentative_g_score + weight * heuristic(neighbor,
                                                                           goal)  # update the estimated total cost from start the start node to the goal node through the neighbor
                heapq.heappush(open_list,
                               (f_score[neighbor], neighbor))  # add neighbor to open list for further evaluation

    return None  # Path not found


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def heuristic(a, b):
    # Manhattan distance for grid-based pathfinding
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
def distance(a, b):
    # Manhattan distance for grid-based pathfinding
    return (abs(a[0] - b[0])**2 + abs(a[1] - b[1])**2)**.5


def plot_graph_path(graph, path):
    G = nx.DiGraph()
    for node in graph:
        for neighbor, cost in graph[node].items():
            G.add_edge(node, neighbor, weight=cost)

    pos = {node: (node[1], - node[0]) for node in G.nodes()}
    plt.figure(figsize=(100, 100))

    # draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='blue')

    # draw edges
    nx.draw_networkx_edges(G, pos, width=1)

    # draw labels
    nx.draw_networkx_labels(G, pos, font_size=5, font_family='sans-serif')

    # show path
    if path:
        edge_path = [(path[n], path[n + 1]) for n in range(len(path) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edge_path, width=1, edge_color='r')

    # plot title
    #plt.gca().invert_yaxis();    plt.gca().invert_xaxis()
    plt.title("Graph with Weighted A* Path")
    plt.show()


def node_coordinates(start_node):
    start_x=[]
    start_y=[]
    sensor_connection_i_index, sensor_data_connection_index, button_data_index = searchNode(str(start_node))
    if (sensor_data_connection_index or sensor_data_connection_index == 0):
        start_y = (float(config['Button_Coordinates'][button_data_index][1]))
        start_x = (float(config['Button_Coordinates'][button_data_index][0]))
    return start_x,start_y


class Graph:

    def __init__(self, graph):
        self.graph = graph
        self.ROW = len(graph)
        self.allPaths_u = []
        self.allPaths_v = []
        self.allFlows = []
        self.number_of_times = 0

# 2. Using BFS as a searching algorithm
    def searching_algo_BFS(self, s, t, parent):

        visited = [False] * (self.ROW)
        queue = []

        queue.append(s)
        visited[s] = True

        while queue:
            # print(queue)
            u = queue.pop(0)
            gr = self.graph

            for ind, val in enumerate(self.graph[u]):
                if visited[ind] == False and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u

        # print(parent)
        return True if visited[t] else False

# 3. Applying Ford-Fulkerson algorithm
    def ford_fulkerson(self, source, sink):
        parent = [-1] * (self.ROW)
# 3.1 Initial Flow
        max_flow = 0 #Initial flow is zero, the summation of max_flow must to be zero at the begining.

        while self.searching_algo_BFS(source, sink, parent):
            # print(parent)

            path_flow = float("Inf")
            s = sink
            while (s != source):
                # print(parent)

                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]

# 4. Adding the path flows
            path_flow = path_flow
            max_flow += path_flow

 # 4.1 Updating the residual values of edges
            v = sink

            allPathsu = []
            allPathsv = []
            while (v != source):
                u = parent[v]
                self.graph[u][v] -= path_flow
                allPathsu.append(u)
                allPathsv.append(v)
                self.graph[v][u] += path_flow
                v = parent[v]

            print(allPathsu)
            print(allPathsv)
            self.allPaths_u.append(allPathsu)
            self.allPaths_v.append(allPathsv)
            self.allFlows.append(path_flow)
            print(path_flow)
            self.number_of_times += 1
            print(self.number_of_times)

            if self.number_of_times > 10:
                break

        return max_flow

def draw_arrow(plt, arr_start, arr_end, costi='left', Head_width=0.2, Head_length=0.2, colcode='red', threshold=5):
        dx = arr_end[0] - arr_start[0]
        dy = arr_end[1] - arr_start[1]
        head_length = ((dx ** 2 + dy ** 2) ** 0.5)  # Calculating length of arrowhead
        # colcode='red'
    # 11. Arrow set up.
        if head_length > threshold:
            plt.arrow(arr_start[0], arr_start[1], dx, dy, head_width=Head_width, head_length=Head_length,
                      length_includes_head=True, color=colcode, linewidth=4, linestyle='dotted')
        else:
            plt.plot([arr_start[0], arr_end[0]], [arr_start[1], arr_end[1]], linestyle='dotted', color='green')

        textAnnotate = [str(costi) + 's'][0]
        plt.annotate(textAnnotate, xy=((arr_end[0] + arr_start[0]) / 2, (arr_end[1] + arr_start[1]) / 2), size=10)

        # plt.arrow(allPaths_u[0], allPaths_u[0])

def myfmt(x, pos):
    return '{0:.1f}'.format(x)
def pathFinderFF(s,t):
    rockfalNodes=[]
    if rockfalNodes:
        cap[rockfalNodes,:]=0 # For example, in this case the node 22, is blocked for a roof fall, the sensor 22 does not collect and process the data

    # 9. Alternative data for the Maximum cost

    # It is not necessary to apply this cost. For that reason is in green. It is used just in case to display a new patterns in the road.

    # 10. Residual Graph

    graphcopy = np.copy(cap)

    g = Graph(cap)
    print("Max Flow: %f " % g.ford_fulkerson(s, t))
    flow = np.array(graphcopy) - np.array(cap)
    for k in range(len(cap)):
        for kk in range(len(cap)):
            if flow[k, kk] < 0:
                flow[k, kk] = 0


    # Reference: This code is contributed by sanjeev2552, sequence and arrows


    print(g.allPaths_u[0])
    print(g.allPaths_v[0])


    # 12. Analysis of the sensor data
    sensorSXY=np.transpose(np.vstack((sensorSX,sensorSY,sensorSX,sensorSY)))

    #sensorSXY=np.copy(sensorSXYcoordinate)
    sensorDATAXY=sensorSXY[:,0:2]
    A = (sensorSXY[:, 2]);
    B = (sensorSXY[:, 3])


    A = [sensorSXY[k, 0] if abs(
        np.arctan((sensorSXY[k, 3] - sensorSXY[k, 1]) / (sensorSXY[k, 2] - sensorSXY[k, 0] + 1e-16))) < 10 else sensorSXY[
        k, 2] for k in range(len(sensorSXY))]
    B = [sensorSXY[k, 1] if abs(
        np.arctan((sensorSXY[k, 3] - sensorSXY[k, 1]) / (sensorSXY[k, 2] - sensorSXY[k, 0] + 1e-16))) > 50 else sensorSXY[
        k, 3] for k in range(len(sensorSXY))]
    A = (sensorSXY[:, 0] + sensorSXY[:, 2]) / 2
    B = (sensorSXY[:, 1] + sensorSXY[:, 3]) / 2

    A = sensorDATAXY[:, 0]
    B = sensorDATAXY[:, 1]
    # fig=plt.figure()

    # 13. Output Images
    #img = mpimg.imread(image_path) #(This file must be part of the folder where the code is running)

     # 13.1 Coordinates of the mine desing

    fig = plt.figure();
    plt.imshow(img)  # , extent=(-45445.00, -45143.00, -3006062.00, -3005450.00)-45445.00,-45142.00,-3006075.00,-3005450.00

    # Note: The coordinates could vary depending on the mine desing.



     # 13.2 Scatter of the permissible exposure parameter limits and recommendations
    plt.scatter( sensorSX,sensorSY, s=375, marker="o", c=sensor_value)
    cbar = plt.colorbar(format=ticker.FuncFormatter(myfmt))
    cbar.set_label(parameterToAnalyze, rotation=90, fontsize=15, fontweight="bold")
    cbar.ax.tick_params(labelsize=15)
    sensors=np.copy(main_node)
    for i in range(len(sensors)):
        plt.text(A[i] - 10, B[i]+5 , str(int(sensors[i])), color="White", fontsize=10.5, fontweight='bold')

    # 14. Max flow calculation

    MAX = np.max(np.abs(flow))
    flow = flow / MAX
    totalTravelTime = 0
    # flow=cap
    """
    for i in range(len(flow)):
        color=colTable[0]
        for j in range(len(flow)):
            if abs(flow[i][j])>0:
                draw_arrow(plt, [A[i],B[i]], [A[j],B[j]],int(cost[i][j]),flow[i][j]*20,flow[i][j]*20,colcode=color)
                totalTravelTime+=cost[i][j]
    """
     # 14.1 Setting up of the route colors

      # 14.1.1 Alternative path
    colTable = ['green', 'red', 'blue', 'green', 'green', 'green', 'green', 'green', 'green', 'green', 'green', 'green']#'red', 'blue', 'green', 'black', 'yellow', 'cyan', 'brown', 'pink', 'purple', 'none'
      # 14.1.2 Main path
    mainpath = ['red'] #'green', 'green', 'green', 'green', 'red', 'none', 'none', 'green', 'red', 'none', 'none', 'green'
      # 14.1.3 Acumulative Emergency escape time
    totalTimeTable = []
    accomulativeTime = []
    totalCOTable = []
    accomulativeCO = []

    # flow=cap

    for i in range(len(g.allPaths_v)):
        color = colTable[i]
        # color_main_path=mainpath[i]
        ind_ = 0
        totalTravelTime = 0
        accomulativeTime_i = []
        accomulativeCO_i = []
        totalCO = 0

        for j in range(len(g.allPaths_v[i])):
            ii = g.allPaths_u[i][-1 - ind_]# -1 - ind_
            jj = g.allPaths_v[i][-1 - ind_]
            # draw_arrow(plt, [A[ii],B[ii]], [A[jj],B[jj]],int(cost[ii][jj]),flow[ii][jj]*20,flow[ii][jj]*20,colcode=color)
            draw_arrow(plt, [A[ii], B[ii]], [A[jj], B[jj]], int(cost[ii][jj]), 14, 14,
                       colcode=color)  # flow[i][j]*20,flow[i][j]*20

            totalTravelTime += cost[ii][jj]
            accomulativeTime_i.append(totalTravelTime)
            totalCO += expos_sensors[ii][jj]
            accomulativeCO_i.append(totalCO)
            ind_ = ind_ + 1
        totalTimeTable.append(totalTravelTime)
        accomulativeTime.append(accomulativeTime_i)
        totalCOTable.append(totalCO)
        accomulativeCO.append(accomulativeCO_i)



      # 14.1.4 Sensor enumeration in the mine

    plt.xlabel('X Position (m)', size=14, fontweight="bold")
    plt.ylabel('Y Position (m)', size=14, fontweight="bold")
    # + ' (route total time : ' +str(int(totalTravelTime/60)) + ' minutes )'
    plt.title('Time: ' + str(int(time / 60)) + ' minutes from fire', size=17, fontweight="bold")
    # fig.tight_layout()
    plt.axis('off')
    # plt.rcParams.update({'font.size': 14})
    plt.show()
def coordinate2nodeSearch(Sx,Sy):
    for k in range(len(config['Button_Coordinates'])):
        if float(config['Button_Coordinates'][k][0])==float(Sx) and float(config['Button_Coordinates'][k][1])==float(Sy):
            return k,config['Button_Coordinates'][k][4]

def exposed_gas(SX,SY):
    JJ,node_Sxy_name_i=coordinate2nodeSearch(SX, SY)
    sensor_connection_i_index, sensor_data_connection_index, button_data_index = searchNode(str(node_Sxy_name_i))
    return v[sensor_data_connection_index]




def plot_path_A_Star(path):

    # 12. Analysis of the sensor data
    sensorSXY=np.transpose(np.vstack((sensorSX,sensorSY,sensorSX,sensorSY)))

    #sensorSXY=np.copy(sensorSXYcoordinate)
    sensorDATAXY=sensorSXY[:,0:2]
    A = (sensorSXY[:, 2]);
    B = (sensorSXY[:, 3])


    A = [sensorSXY[k, 0] if abs(
        np.arctan((sensorSXY[k, 3] - sensorSXY[k, 1]) / (sensorSXY[k, 2] - sensorSXY[k, 0] + 1e-16))) < 10 else sensorSXY[
        k, 2] for k in range(len(sensorSXY))]
    B = [sensorSXY[k, 1] if abs(
        np.arctan((sensorSXY[k, 3] - sensorSXY[k, 1]) / (sensorSXY[k, 2] - sensorSXY[k, 0] + 1e-16))) > 50 else sensorSXY[
        k, 3] for k in range(len(sensorSXY))]
    A = (sensorSXY[:, 0] + sensorSXY[:, 2]) / 2
    B = (sensorSXY[:, 1] + sensorSXY[:, 3]) / 2

    A = sensorDATAXY[:, 0]
    B = sensorDATAXY[:, 1]
    # fig=plt.figure()

    # 13. Output Images
    #img = mpimg.imread(image_path) #(This file must be part of the folder where the code is running)

     # 13.1 Coordinates of the mine desing
    fig = plt.figure(figsize=(12, 8))
    plt.imshow(img)  # , extent=(-45445.00, -45143.00, -3006062.00, -3005450.00)-45445.00,-45142.00,-3006075.00,-3005450.00
    #manager = plt.get_current_fig_manager()

    # Note: The coordinates could vary depending on the mine desing.



     # 13.2 Scatter of the permissible exposure parameter limits and recommendations
    plt.scatter( sensorSX,sensorSY, s=375, marker="o", c=sensor_value)
    cbar = plt.colorbar(format=ticker.FuncFormatter(myfmt))
    cbar.set_label(parameterToAnalyze, rotation=90, fontsize=15, fontweight="bold")
    cbar.ax.tick_params(labelsize=15)
    sensors=np.copy(main_node)
    for i in range(len(sensors)):
        plt.text(A[i] - 10, B[i]+5 , str(int(sensors[i])), color="White", fontsize=10.5, fontweight='bold')

    # 14. Max flow calculation

    totalTravelTime = 0
    # flow=cap
    """
    for i in range(len(flow)):
        color=colTable[0]
        for j in range(len(flow)):
            if abs(flow[i][j])>0:
                draw_arrow(plt, [A[i],B[i]], [A[j],B[j]],int(cost[i][j]),flow[i][j]*20,flow[i][j]*20,colcode=color)
                totalTravelTime+=cost[i][j]
    """
     # 14.1 Setting up of the route colors

      # 14.1.1 Alternative path
    colTable = ['green', 'red', 'blue', 'yellow', 'green', 'green', 'green', 'green', 'green', 'green', 'green', 'green']#'red', 'blue', 'green', 'black', 'yellow', 'cyan', 'brown', 'pink', 'purple', 'none'
      # 14.1.2 Main path
    mainpath = ['red'] #'green', 'green', 'green', 'green', 'red', 'none', 'none', 'green', 'red', 'none', 'none', 'green'
      # 14.1.3 Acumulative Emergency escape time
    totalTimeTable = []
    accomulativeTime = []
    totalCOTable = []
    accomulativeCO = []

    # flow=cap
    ind_ = 0
    totalTravelTime = 0
    accomulativeTime_i = []
    accomulativeCO_i = []
    totalCO = 0
    for i in range(len(path)-1):
        color = colTable[0]
        # color_main_path=mainpath[i]



            # draw_arrow(plt, [path[i][0],B[ii]], [A[jj],B[jj]],int(cost[ii][jj]),flow[ii][jj]*20,flow[ii][jj]*20,colcode=color)
        draw_arrow(plt, [path[i][1], path[i][0]], [path[i+1][1], path[i+1][0]], 2, 14, 14,
                   colcode=color)  # flow[i][j]*20,flow[i][j]*20
        dt_i=distance([path[i][1], path[i][0]],[path[i+1][1], path[i+1][0]])/velocity
        totalTravelTime += dt_i
        accomulativeTime_i.append(totalTravelTime)
        CO_i=(exposed_gas(path[i][0], path[i][1])+exposed_gas(path[i+1][0], path[i+1][1]))/2
        totalCO += CO_i*dt_i
        accomulativeCO_i.append(totalCO)
        ind_ = ind_ + 1
        totalTimeTable.append(totalTravelTime)
        accomulativeTime.append(accomulativeTime_i)
        totalCOTable.append(totalCO)
        accomulativeCO.append(accomulativeCO_i)



      # 14.1.4 Sensor enumeration in the mine

    plt.xlabel('X Position (m)', size=14, fontweight="bold")
    plt.ylabel('Y Position (m)', size=14, fontweight="bold")
    # + ' (route total time : ' +str(int(totalTravelTime/60)) + ' minutes )'
    #plt.title('Time: ' + str(int(time / 60)) + ' minutes from accident\n '+'Approx. Gas exposure: ' + str(int(totalCO)) + '(ppm-s) in ' + str(int(totalTravelTime/60))+' minutes '+ ' (' + str(int(totalTravelTime*velocity))+' m) ', size=17, fontweight="bold")
    plt.title('Time: ' + str(int(time / 60)) + ' minutes', size=17, fontweight="bold")

    # fig.tight_layout()
    plt.axis('off')
    # plt.rcParams.update({'font.size': 14})
    #plt.rcParams.update({'font.size': 14})
    plt.savefig("simulation_data_and_path_escape")
    if do_not_show_plot_just_save:
        plt.close(fig)
    else:
        plt.show()

readPythonSpreadSheet(pathData,parameterIndex=3,time=60)


s = start_node_name - 1
t = goal_node_name - 1

readPythonSpreadSheet(pathData,parameterIndex=3,time=time)
cap,expos_sensors,sensorSX,sensorSY=capacityBuilding()
#pathFinderFF(s,t)

# 1 means weight 1. you can change it to 2,.5, etc.  negative sign means that there capacity has inverse proportion to sensor value. for example higher CO has inverse effect on campacity.
# If you want include only part of sensors, for example visibility and CO, you should change form of indOfParamToUse=[3,5], weightParamToUse=[1,-1] [1,1,-1,1,1,-1]
velocity = 1  # m/s #Walking speed of the miners
rockfalNodes=22



start = (node_coordinates(start_node_name)[0], node_coordinates(start_node_name)[1])
goal = (node_coordinates(goal_node_name)[0], node_coordinates(goal_node_name)[1])
grph,weights=graph_Weighted_A_Star()
path = weighted_a_star(grph, start, goal, heuristic, weight=2.0, weights=weights)
print("Path found:", path)

# plot graph showing path
#plot_graph_path(grph, path)
plot_path_A_Star(path)

