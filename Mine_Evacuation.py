# Python3 program to implement
# the above approach
from sys import maxsize
from typing import List
import numpy as np
#ploting
import matplotlib.pyplot as plt

INF = maxsize // 2 - 1


#addres_excell="C:\\Users\\Sean\\Desktop\\New code\\NEW_SENSOR2_DATA (32 Sensors) (2).xlsx"  # Put the spreadsheet's filepath here
addres_excell="C:\\Users\\Sean\\PycharmProjects\\Gas sensor\\duplicate.xlsx"
img = mpimg.imread('C:\\Users\\Sean\\Desktop\\New code\\CO concentration Model_3.png')      # Put the reference image filepath here

class Graph:

    def __init__(self, graph):
        self.graph = graph
        self. ROW = len(graph)
        self.allPaths_u=[]
        self.allPaths_v = []
        self.allFlows=[]
        self.number_of_times=0


    # Using BFS as a searching algorithm
    def searching_algo_BFS(self, s, t, parent):

        visited = [False] * (self.ROW)
        queue = []

        queue.append(s)
        visited[s] = True

        while queue:
            #print(queue)
            u = queue.pop(0)
            gr=self.graph

            for ind, val in enumerate(self.graph[u]):
                if visited[ind] == False and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u

        #print(parent)
        return True if visited[t] else False

    # Applying fordfulkerson algorithm
    def ford_fulkerson(self, source, sink):
        parent = [-1] * (self.ROW)


        max_flow = 0

        while self.searching_algo_BFS(source, sink, parent):
            #print(parent)



            path_flow = float("Inf")
            s = sink
            while(s != source):
                #print(parent)

                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]

            # Adding the path flows
            path_flow=path_flow
            max_flow += path_flow


            # Updating the residual values of edges
            v = sink

            allPathsu=[]
            allPathsv = []
            while(v != source):
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
            self.number_of_times+=1
            print(self.number_of_times)

            if self.number_of_times>10:
                break


        return max_flow


import matplotlib.image as mpimg


# Driver Code
s = 6-1
t = 32-1
time=1800 #seconds
nodes_with_high_capacity=28
DontuseDecapacitor=False#if you want to only use FFA with conctant capacity of 5
#Concentration of CO data
import pandas as pd
df=pd.read_excel(addres_excell,sheet_name = 'Sheet1',engine='openpyxl')
sensorData=pd.read_excel(addres_excell,sheet_name = 'Sheet2',engine='openpyxl')
velocity=1 #m/s
AllParameters=['Airflow m³/s','Velocity m/s','Temp Wet Bulb ºC','Visibility m','O2  %','CO  ppm']
indOfParamToUse=[0,1,2,3,4,5]#the parameters to be used, 5 means 'CO  ppm';
weightParamToUse=[1,1,-1,1,1,-1]#1 means weight 1. you can change it to 2,.5, etc.  negative sign means that there capacity has inverse proportion to sensor value. for example higher CO has inverse effect on campacity.
# If you want include only part of sensors, for example visibility and CO, you should change form of indOfParamToUse=[3,5], weightParamToUse=[1,-1]

individualparams=5;indOfParamToUse=[indOfParamToUse[individualparams]];weightParamToUse=[weightParamToUse[individualparams]] # uncomment this line if single parameters is wanted., for example individualparams=5 means use only CO, individualparams=3 means use only Visibility
parameterToAnalyze=[AllParameters[indOfParamToUse[k]] for k in range(len(indOfParamToUse))]

sensorsTime=sensorData.values.__array__()[3:,0]
difference_array = np.absolute(sensorsTime - time)
# find the index of minimum element from the array
indexOfTime = difference_array.argmin()

sensorsDataNamesAll=sensorData.values.__array__()[1,1:]
ParametersNamesAll=sensorData.values.__array__()[0,1:]
sensorsDataAll=sensorData.values.__array__()[indexOfTime+3,1:]
sensorsDataForParameter_CO=[sensorsDataAll[k] for k in range (len(sensorsDataAll)) if ParametersNamesAll[k]=='CO  ppm']
sensorsDataForParameter_Vis=[sensorsDataAll[k] for k in range (len(sensorsDataAll)) if ParametersNamesAll[k]=='Visibility m']


#////////////////
dict_data=dict()
for k in range(len(indOfParamToUse)):
    ki=indOfParamToUse[k]
    parameterToAnalyze_i = AllParameters[k]
    sensorsDataForParameter_i = [sensorsDataAll[k] for k in range(len(sensorsDataAll)) if
                               ParametersNamesAll[k] == parameterToAnalyze_i]
    if (k in indOfParamToUse):

        weight_i=weightParamToUse[indOfParamToUse.index(ki)]
        MAXsensorsDataNamesForParameteri = np.max(sensorsDataForParameter_i)
        if weight_i<0:
            sensorsDataForParameter_i =( MAXsensorsDataNamesForParameteri - sensorsDataForParameter_i)
        MAXsensorsDataNamesForParameteri = np.max(sensorsDataForParameter_i)
        sensorsDataForParameter_i=sensorsDataForParameter_i/MAXsensorsDataNamesForParameteri*np.abs(weight_i)

    dict_data[parameterToAnalyze_i]=sensorsDataForParameter_i
if len(indOfParamToUse)>1:
    sensorsDataForParameter=sensorsDataForParameter_i*0
    for k in dict_data:
        sensorsDataForParameter=dict_data[k]+sensorsDataForParameter
        sensorsDataForParameter_Original = sensorsDataForParameter * 1
else:
    weight_i = weightParamToUse[indOfParamToUse.index(indOfParamToUse[0])]
    sensorsDataForParameter = [sensorsDataAll[k] for k in range(len(sensorsDataAll)) if
                                   ParametersNamesAll[k] == parameterToAnalyze[0]]
    sensorsDataForParameter_Original=sensorsDataForParameter*1
   # if  ('CO  ppm' in parameterToAnalyze):
    #    for k in range(len(sensorsDataForParameter)):
    #            sensorsDataForParameter[k]=np.fix(max(0, (1 - sensorsDataForParameter[k] / 400.0) * 5))
    MAXsensorsDataNamesForParameteri = np.max(sensorsDataForParameter)
    if weight_i < 0:
        sensorsDataForParameter = (MAXsensorsDataNamesForParameteri - sensorsDataForParameter)

sensorsDataNamesForParameter=[sensorsDataNamesAll[k] for k in range (len(sensorsDataAll)) if ParametersNamesAll[k]==parameterToAnalyze[0]]
#/////////////////////


multiParameterToAnalyze=[AllParameters[indOfParamToUse[k]] for k in range(len(indOfParamToUse))]

sensors=df.values.__array__()[1:,0]
cap=np.zeros((len(sensors),len(sensors)))
cost=np.zeros((len(sensors),len(sensors)))

sensorConnection=df.values.__array__()[1:,6:10]
sensorSXY=df.values.__array__()[1:,2:6]
apply_brute_equual_chance_for_all_nodes=0


if np.max(sensorsDataForParameter)==np.min(sensorsDataForParameter):
    apply_brute_equual_chance_for_all_nodes=1 # for example t=0, every where has equal co concentration of 0 then we put 1 capacity for all

sensorsDataNamesForParameteri=[]
for i in range(len(sensors)):
    for kkk in range(len(sensorsDataForParameter)):
        if sensorsDataNamesForParameter[kkk] == sensors[i]:
            sensorsDataNamesForParameteri.append(sensorsDataForParameter_Original[kkk])
            break
MAXsensorsDataNamesForParameteri=np.max(sensorsDataNamesForParameteri)
sensorsDataForParameterforCapacity = sensorsDataForParameter*1
MAXsensor=np.max(sensorsDataForParameter)

increasCapacity=False
capcoef=1

for k in range(len(sensors)):
    for kk in range(np.size(sensorConnection,1)):

        if sensorConnection[k,kk]!='--' and sensorConnection[k,kk]!='nan':
            pp=(sensors==sensorConnection[k,kk])
            pp_connecting_node=[k for k in range(len(pp)) if pp[k]][0]
            if 'Visibility m' in parameterToAnalyze:
                valuesi=[x for x in sensorConnection[k,:] if isinstance(x, (int,float))]
                for val in valuesi:
                 if val>10:
                     increasCapacity=True


            dist=np.sqrt(((sensorSXY[k,0]+sensorSXY[k,2])/2-(sensorSXY[pp_connecting_node,0]+sensorSXY[pp_connecting_node,2])/2)**2+((sensorSXY[k,1]+sensorSXY[k,3])/2-(sensorSXY[pp_connecting_node,1]+sensorSXY[pp_connecting_node,3])/2)**2)
            for kkk in range(len(sensorsDataForParameter)):
                if sensorsDataNamesForParameter[kkk]==sensors[k]:
                        if increasCapacity:
                            capcoef=3
                        else:
                            capcoef=1
                        if  sensorsDataForParameter[kkk]!=0:
                            #cap[k, pp_connecting_node] = sensorsDataForParameterforCapacity[kkk]*capcoef
                            cap[k, pp_connecting_node] = max(0,(sensorsDataForParameter[kkk]))
                            if DontuseDecapacitor:
                                cap[k, pp_connecting_node] = 5
                            cost[k, pp_connecting_node] =  dist/velocity
                            if ('CO  ppm' in parameterToAnalyze) and sensorsDataForParameter_CO[kkk]>400 and k != s and k<=nodes_with_high_capacity:
                                cap[k, pp_connecting_node]=0
                            if ('Visibility m' in parameterToAnalyze) and sensorsDataForParameter_Vis[kkk]<5 and k != s and k<=nodes_with_high_capacity:
                                cap[k, pp_connecting_node]=0

                            #cap[k, pp_connecting_node] = 1
                            if k == s or k>nodes_with_high_capacity:
                                cap[k, pp_connecting_node] =  10*MAXsensor
                        else:
                            cap[k, pp_connecting_node]=max(0,sensorsDataForParameter[kkk])
                            if DontuseDecapacitor:
                                cap[k, pp_connecting_node] = 5
                            cost[k, pp_connecting_node] =  dist/velocity
                            if ('CO  ppm' in parameterToAnalyze) and sensorsDataForParameter[kkk]>400 and k != s and k<=nodes_with_high_capacity:
                                cap[k, pp_connecting_node]=0
                            #cap[k, pp_connecting_node] = 1
                            if k == s or k>nodes_with_high_capacity:
                                cap[k, pp_connecting_node] =  10*MAXsensor
                        if  apply_brute_equual_chance_for_all_nodes:
                            cap[k, pp_connecting_node] = 10 # apply 10 as everywhere has the same capacity
                            if k == s or k>nodes_with_high_capacity:
                                cap[k, pp_connecting_node] = 10





#cap[6][9]=100;cap[7][9]=100

if ('CO  ppm' in parameterToAnalyze):
    for k in range(np.size(cap,0)):
        for kk in range(np.size(cap, 1)):
            if cap[k][kk] != 0 and cap[k][kk] != -999.99:
                pass
                #cap[k][kk]=cap[k][kk]/cost[k][kk]
    MAXCAP = np.max(cap)
    for k in range(np.size(cap,0)):
        for kk in range(np.size(cap, 1)):
            if cap[k][kk] == -999.99:
                cap[k][kk]=MAXCAP

#cap[24, 0:] =  cap[24, 0:]*0
#cap[23,:]=0
'''
cost = [[0, 83.65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 71.25, 65.65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 65.61, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 66.82, 43.51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 41.73, 92.56, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 65.61, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 94.64, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 67.47, 45.42, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 44.46, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 65.21, 153.4, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 152.6, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 68.6, 80.6, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 63.43, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 67.45, 65.39, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 42.25, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 66.04, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 192.5],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


for k in range(np.size(cap,0)):
    for kk in range(np.size(cap, 1)):
        if  cost[k][kk]!=0:
            cost[k][kk]=1

cost[6][9]=100;cost[7][9]=100

for k in range(np.size(cap,0)):
    for kk in range(np.size(cap, 1)):
        if  cost[k][kk]!=0:
            cap[k][kk]=cap[k][kk]/cost[k][kk]
            if cap[k][kk] > 10:
                cap[k][kk] = 10
'''
"""
for k in range(np.size(cap, 0)):
    for kk in range(np.size(cap, 1)):
        if cap[k][kk] !=0:
            cap[k][kk] = 1
            cost[k][kk] = 1
            if k==s:
                cap[k][kk] = .1
                cost[k][kk] = 1

#cap=[[0,1,1,0],[0, 0, 1,1],[0,0,0,0],[0,0,1,0]]; cost=[[0,1,1,0],[0, 0, 1,1],[0,0,0,0],[0,0,1,0]];s=0;t=2

capi = cap
costi = cost
N = len(cap)

for k in range(N):
    if capi[srci][k]!=0:
        found[k]=True
        pathList.append(k)
        srci=k
        continue
srci = s
sink = t
foundi = [False for _ in range(N)]
pathList = []
pathList.append((srci))
k1=0
while srci!=sink:

    for k in range(k1,N):
        if capi[srci][k] != 0:
            found[k] = True
            pathList.append(k)
            srci = k
            continue
print(pathList)



"""
graphcopy=np.copy(cap)

g=Graph(cap)
#ret = getMaxFlow(cap, cost, s, t)

#print("{} {}".format(ret[0], ret[1]))
print("Max Flow: %f " % g.ford_fulkerson(s, t))
flow=np.array(graphcopy)-np.array(cap)
for k in range(len(cap)):
    for kk in range(len(cap)):
        if flow[k,kk]<0:
            flow[k,kk]=0
# This code is contributed by sanjeev2552, sequence and arrows
def draw_arrow(plt, arr_start, arr_end,costi,Head_width=0.5,Head_length=0.5):
    dx = arr_end[0] - arr_start[0]
    dy = arr_end[1] - arr_start[1]
    plt.arrow(arr_start[0], arr_start[1], dx, dy, head_width=Head_width, head_length=Head_length, length_includes_head=True, color='green',linewidth=3)
    textAnnotate=[str(costi)+' s'][0]
    plt.annotate(textAnnotate,xy=((arr_end[0] + arr_start[0])/2, (arr_end[1] + arr_start[1])/2),size=10)





A=(sensorSXY[:,2]);B=(sensorSXY[:,3])

sensorDATAXY=pd.read_excel(addres_excell,sheet_name = 'Sheet3',engine='openpyxl')


A=[sensorSXY[k,0] if abs(np.arctan((sensorSXY[k,3]-sensorSXY[k,1])/(sensorSXY[k,2]-sensorSXY[k,0]+1e-16))) <10 else sensorSXY[k,2] for k in range(len(sensorSXY))]
B=[sensorSXY[k,1] if abs(np.arctan((sensorSXY[k,3]-sensorSXY[k,1])/(sensorSXY[k,2]-sensorSXY[k,0]+1e-16))) >50 else sensorSXY[k,3] for k in range(len(sensorSXY))]
A=(sensorSXY[:,0]+sensorSXY[:,2])/2
B=(sensorSXY[:,1]+sensorSXY[:,3])/2

A=sensorDATAXY.values[:,0]
B=sensorDATAXY.values[:,1]
#fig=plt.figure()
# Output Images
ximg=np.linspace(-45190.00,-45400.00,np.shape(img)[0])
yimg=np.linspace(-3006075.00,	-3005450.00,np.shape(img)[1])
fig=plt.figure();plt.imshow(img,extent=(-45445.00,-45142.00,-3006075.00,-3005450.00))
import matplotlib.ticker as ticker
def myfmt(x, pos):
    return '{0:.1f}'.format(x)
plt.scatter(A,B,s=300,marker="o",c=sensorsDataNamesForParameteri)
cbar = plt.colorbar(format=ticker.FuncFormatter(myfmt))
cbar.set_label(parameterToAnalyze, rotation=90, fontsize=12,fontweight="bold")
cbar.ax.tick_params(labelsize=12)

for i in range(len(sensors)):
    plt.text(A[i]-5, B[i]-2, str(int(sensors[i])),color="White", fontsize = 10)

#flow=graphcopy*1

MAX=np.max(np.abs(flow))
flow=flow/MAX
totalTravelTime=0

#flow=cap
for i in range(len(flow)):
    for j in range(len(flow)):
        if abs(flow[i][j])>0:
            draw_arrow(plt, [A[i],B[i]], [A[j],B[j]],int(cost[i][j]),flow[i][j]*20,flow[i][j]*20)
            totalTravelTime+=cost[i][j]

plt.xlabel('X Position (m)', size=14,fontweight="bold")
plt.ylabel('Y Position (m)',  size=14,fontweight="bold")
#+ ' (route total time : ' +str(int(totalTravelTime/60)) + ' minutes )'
plt.title('Time: '+ str(int(time/60))+' minutes from fire'  ,  size=14,fontweight="bold")
#fig.tight_layout()
plt.axis('off')
#plt.rcParams.update({'font.size': 14})
plt.show()
