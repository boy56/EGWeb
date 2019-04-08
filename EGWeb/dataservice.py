from py2neo import Graph
from EGWeb.models import TriggerNode, EventNode
from py2neo.data import Node

graph = Graph(
    "bolt://127.0.0.1:7687", username="neo4j", password="sjh19970201"
)


# return json:{nodes:[], edges:[]}
def search_event_by_theme(theme):
    # 返回的node只有EVENT类型的节点, 关系也只有事件之间的关系
    result_data = {}
    nodes_list = []
    edges_list = []  # [{sourseID:.., targetID:..., weight:...}, {sourseID:..., targetID:..., weight:...}, ...]

    event_nodes = list(EventNode.match(graph).where("_.theme=" + "\'" + theme + "\'"))
    if len(event_nodes) == 0:   # 未查找到相关信息
        result_data['status'] = 0  # 1代表成功, 0代表失败
        result_data['nodes'] = nodes_list
        result_data['edges'] = edges_list
        return result_data
    for event_n in event_nodes:
        # get EVENT node info
        node_dict = {}
        # node_dict['ID'] = event_n.__node__.__uuid__
        node_dict['ID'] = event_n.__node__.identity
        node_dict['TYPE'] = "EVENT"
        node_dict['title'] = event_n.title
        node_dict['time'] = event_n.time
        node_dict['locations'] = event_n.locations
        node_dict['persons'] = event_n.persons
        node_dict['organizations'] = event_n.organizations
        node_dict['keywords'] = event_n.keywords
        node_dict['triggers'] = ''
        for tri in event_n.triggers:
            node_dict['triggers'] = node_dict['triggers'] + tri.name + ' '
        node_dict['triggers'] = node_dict['triggers'][:-1]
        nodes_list.append(node_dict)

        # get NEXT_EVENT relations edge
        for next_event in event_n.next_events:
            
            edge_dict = {}
            # edge_dict['sourceID'] = event_n.__node__.__uuid__
            edge_dict['sourceID'] = event_n.__node__.identity
            # edge_dict['targetID'] = next_event.__node__.__uuid__
            edge_dict['targetID'] = next_event.__node__.identity
            edge_dict['weight'] = 1
            edges_list.append(edge_dict)

    # 构造返回数据
    result_data['status'] = 1  # 1代表成功, 0代表失败
    result_data['nodes'] = nodes_list
    result_data['edges'] = edges_list
    return result_data


def search_trigger_by_name(triname):
    # 从数据库中查询符合要求的触发词
    # 如果触发词为v-n形式则全匹配查询, 未查到则采用v查询
    # 如果触发词为v形式, 则直接进行v查询, 不进行全匹配查询
    result_data = {}
    nodes_list = []
    edges_list = []  # [{sourseID:.., targetID:..., weight:...}, {sourseID:..., targetID:..., weight:...}, ...]
    tri_nodes = []
    tri_info = triname.split('-')
    
    if len(tri_info) == 2:  # v-n形式
        tri_nodes = list(TriggerNode.match(graph).where("_.name=" + "\'" + triname + "\'"))
    if len(tri_nodes) == 0:  # 未找到
        tri_nodes = list(TriggerNode.match(graph).where("_.verb=" + "\'" + tri_info[0] + "\'"))
        if len(tri_nodes) == 0:
            result_data['status'] = 0  # 1代表成功, 0代表失败
            result_data['nodes'] = nodes_list
            result_data['edges'] = edges_list
            return result_data

    tri_node_set = set()
    # 根据触发词的下一步关系扩充node节点
    for t in tri_nodes:
        if t not in tri_node_set:
            node_dict = {}
            # node_dict['ID'] = t.__node__.__uuid__
            node_dict['ID'] = t.__node__.identity
            node_dict['TYPE'] = "TRIGGER"
            node_dict['name'] = t.name
            node_dict['verb'] = t.verb
            node_dict['noun'] = t.noun
            node_dict['events'] = []
            for e in t.belong_tos:
                event_info = {}
                event_info['title'] = e.title
                event_info['theme'] = e.theme
                node_dict['events'].append(event_info)
            tri_node_set.add(t)
            nodes_list.append(node_dict)

            # print(t.__node__.__uuid__)

        for next_t in t.next_triggers:
            if next_t not in tri_node_set:
                node_dict = {}
                # node_dict['ID'] = next_t.__node__.__uuid__
                node_dict['ID'] = next_t.__node__.identity
                node_dict['TYPE'] = "TRIGGER"
                node_dict['name'] = next_t.name
                node_dict['verb'] = next_t.verb
                node_dict['noun'] = next_t.noun
                node_dict['events'] = []
                for e in t.belong_tos:
                    event_info = {}
                    event_info['title'] = e.title
                    event_info['theme'] = e.theme
                    node_dict['events'].append(event_info)
                tri_node_set.add(next_t)
                nodes_list.append(node_dict)
            edge_dict = {}
            # edge_dict['sourceID'] = t.__node__.__uuid__
            # edge_dict['targetID'] = next_t.__node__.__uuid__
            edge_dict['sourceID'] = t.__node__.identity
            edge_dict['targetID'] = next_t.__node__.identity
            edge_dict['weight'] = 1
            edges_list.append(edge_dict)

    # 构造返回数据
    result_data['status'] = 1  # 1代表成功, 0代表失败
    result_data['nodes'] = nodes_list
    result_data['edges'] = edges_list
    return result_data

def search_trigger_by_theme(theme):
    # 返回的node只有EVENT类型的节点, 关系也只有事件之间的关系
    result_data = {}
    nodes_list = []
    edges_list = []  # [{sourseID:.., targetID:..., weight:...}, {sourseID:..., targetID:..., weight:...}, ...]

    event_nodes = list(EventNode.match(graph).where("_.theme=" + "\'" + theme + "\'"))
    tri_node_set = set()
    if len(event_nodes) == 0:   #未查找到相关信息
        result_data['status'] = 0  # 1代表成功, 0代表失败
        result_data['nodes'] = nodes_list
        result_data['edges'] = edges_list
        return result_data
    for event_n in event_nodes:
       for t in event_n.triggers:
            if t not in tri_node_set:
                node_dict = {}
                # node_dict['ID'] = t.__node__.__uuid__
                node_dict['ID'] = t.__node__.identity
                node_dict['TYPE'] = "TRIGGER"
                node_dict['name'] = t.name
                node_dict['verb'] = t.verb
                node_dict['noun'] = t.noun
                node_dict['events'] = []
                for e in t.belong_tos:
                    event_info = {}
                    event_info['title'] = e.title
                    event_info['theme'] = e.theme
                    node_dict['events'].append(event_info)
                tri_node_set.add(t)
                nodes_list.append(node_dict)
    for t in tri_node_set:
        for next_t in t.next_triggers:
            if next_t in tri_node_set:  # 保证是当前事件的触发词
                edge_dict = {} 
                edge_dict['sourceID'] = t.__node__.identity
                edge_dict['targetID'] = next_t.__node__.identity
                edge_dict['weight'] = 1
                edges_list.append(edge_dict)
    # 构造返回数据
    result_data['status'] = 1  # 1代表成功, 0代表失败
    result_data['nodes'] = nodes_list
    result_data['edges'] = edges_list
    return result_data

if __name__ == '__main__':
    # graph = Graph(password='sjh19970201')
    # 完成Node到类对象的映射
    # print(search_trigger_by_name("发现"))
    print(search_event_by_theme("李文星"))
