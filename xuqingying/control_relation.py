import sys
sys.path.append('../src')
from data_door import DataDoor
import find_path
import numpy as np
from wink_path import WeakPath as wp
IP = "202.114.74.170"
Port = 9900
class ControlAB:
    """
    查控制关联
    entity1:持股实体
    entity2:被控股公司
    """
    def __init__(self,entity1,entity2,username,password,exist=False,control=False):
        self.entity1=entity1
        self.entity2=entity2
        self.exist=exist#有无控制关联
        self.cotntrol=control#是否A受B控制
        self.username=username
        self.password=password

    def check(self):
        """
        检验连接是否存在
        """
        path=find_path.queryholders(self.entity1,self.entity2)
        if path:
            self.exist=True
            return path
        else:
            return None

    def data_process(self):
        """
        判断是否存在最大控制关系
        若存在，返回控制权指数
        """
        #if self.exist==True:
        paths = find_path.queryholders(self.entity1, self.entity2)
        if paths:
            self.exist=True
            graph=[]
            for path in paths:
                ControlA = DataDoor(IP, Port, self.username, self.password, path[0],path[1])
                power=ControlA.data_process()
                if power:
                    graph.append([path[0],path[1],power])
            WeakCacul=wp(graph)
            conAB=WeakCacul.calculation(self.entity1,self.entity2)
            allNodes=WeakCacul.Graph[0]
            control=[]
            for node in allNodes:
                con=WeakCacul.calculation(node,self.entity2)
                control.append(con)
            if max(control)==conAB:
                self.cotntrol=True
                return conAB
        else:
            pass

class ControlA:
    """
    输出：二维数组
    """
    def __init__(self,entity,username,password):
        self.entity=entity
        self.username=username
        self.password=password

    def getFather(self,layer):
        """
        向外提取父节点
        layer:层数
        输出：股权图
        """
        if layer<0:
            print('Error:层数应大于0')
        else:
            #entity=self.entity
            nodes=[]#所有点
            nodes.append(self.entity)
            l=[]
            graph=[]#所有边
            while layer>0:
                for node in nodes:
                    print(node)
                    print(len(nodes))
                    ControlA = DataDoor(IP, Port, self.username, self.password, entity2=node)
                    data = ControlA.data_processA()
                    print(data)
                    if data:
                        for da in data:
                            l.append(da[0])
                            #print(da[0])
                    print(node)
                layer = layer-1
                nodes=nodes+l
                print(layer)
            for node1 in nodes:
                for node2 in nodes:
                    con12= DataDoor(IP, Port, self.username, self.password,node1, node2)
                    power=con12.data_process()
                    if power:
                        #print(power)
                        graph.append([node1,node2,power])
            print(graph)
            return graph

    def data_process(self,layer):
        """
        通过最弱边算法得到控制权
        """
        graph=self.getFather(layer)
        print('数据加载完毕,开始计算。')
        WeakCacul=wp(graph)
        control=WeakCacul.calcuAll()
        return control

class ControlFull:
    """
    查控制网络页面
    """
    def __init__(self,entity,username,password):
        self.entity=entity
        self.username=username
        self.password=password

    def getSon(self,layer):
        """
        向内提取子节点
        layer:层数
        输出：所有子节点
        """
        if layer<0:
            print('Error:层数应大于0')
        else:
            entity=self.entity
            nodes=[entity]#所有点
            l=[]
            #graph=[]#所有边
            while layer>0:
                for node in nodes:
                    ControlA = DataDoor(IP, Port, self.username, self.password, entity1=node)
                    data = ControlA.data_processA()
                    if data:
                        for da in data:
                            l.append(da[0])
                layer=layer-1
                nodes=nodes+l
            print('子节点提取完毕')
            return nodes

    def getFather(self,layer):
        """
        向外提取父节点
        layer:层数
        输出：股权图
        """
        if layer<0:
            print('Error:层数应大于0')
        else:
            entity=self.entity
            nodes=[entity]#所有点
            l=[]
            graph=[]#所有边
            while layer>0:
                for node in nodes:
                    ControlA = DataDoor(IP, Port, self.username, self.password, entity2=node)
                    data = ControlA.data_processA()
                    if data:
                        for da in data:
                            #print(da[0])
                            l.append(da[0])
                layer=layer-1
                nodes=nodes+l
                #print(layer)
            for node1 in nodes:
                for node2 in nodes:
                    con12= DataDoor(IP, Port, self.username, self.password,node1, node2)
                    power=con12.data_process()
                    if power:
                        graph.append([node1,node2,power])
                        #print(power)
            print('父节点提取完毕。')
            return graph


    def data_process(self,layer):
        """
        输出：属于被查询实体控制系的点，及他们之间的控制权指数
        """
        Sonnodes=self.getSon(layer)
        Department=[]
        for node in Sonnodes:
            graph=self.getFather(layer)
            WeakCacul=wp(graph)
            control=[]
            for no in WeakCacul.Graph[0]:
                con=WeakCacul.calculation(self.entity,no)
                control.append(con)
            conAB=WeakCacul.calculation(self.entity,node)
            if conAB==max(control):
                Department.append([self.entity,node,conAB])
            #班扎夫指数计算
            #id1.append(self.entity)
            #leng = len(id1)
            #A = np.empty(leng, leng)
            #for i in range(leng - 1):
            #    for j in range(leng - 1):
            #        if id1[i]==self.entity:
            #            index=i
            #        ControlA = DataDoor(IP, Port, username, password, id1[i], id1[j])
            #        ControlA.get_data()
            #        data[i][j] = ControlA.data_process()
            #con = bz.Banzhaf0(A, [[1] * leng] * leng, [1 / (2 ** leng)] * (2 ** leng))
            #con.float_change()
            #control_A = con.Banzhaf()
            #if control_A[index][leng-1]==max(control_A[:,leng-1]):
            #    cons.append({'name':isi,'control':control_A[index][leng-1]})
        return Department

if __name__=='__main__':
    uesrname = 'root'
    password = '123456'
    #controlAB=ControlAB('常玉英','交通银行股份有限公司')
    #AB=controlAB.data_process()
    #print(AB)
    #exist=controlAB.exist
    #print(exist)
    #control=controlAB.cotntrol
    #print(control)
    controlA=ControlA('上海山阳电讯器材厂',uesrname,password)
    data=controlA.data_process(1)#向外提取一层
    print(data)

    #controlB=ControlFull('常玉英',uesrname,password)
    #B=controlB.data_process(1)#向内提取一层
    #print(B)

