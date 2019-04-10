# -*- coding: utf-8 -*-
# 将xml格式数据处理后加载到数据库中
import xml.etree.cElementTree as ET
from EGWeb.models import EventNode, TriggerNode
from py2neo import Graph


def adddata(filepath, graph, theme):
    root = ET.ElementTree(file=filepath)
    # print(777)
    xml_graph = root.find('graph')
    nodes = xml_graph.find('nodes')
    edges = xml_graph.find('edges')

    event_nodes = {}  # {id: EventNode}
    trigger_nodes = {}  # {id: TriggerNode}
    event_trigger = {}  # {eventId: [triggers]}

    for node in nodes.findall(
            'node'):  # finds only elements with a tag which are direct children of the current element.
        # print(node)
        if node.attrib['labels'] == ":ENTITY:TRIGGER":
            # trigger node
            trigger_id = node.attrib['id'].replace('{', '').replace('}', '')
            name= ''
            verb= ''
            noun = ''

            for data in node.findall('data'):
                if data.attrib['key'] == 'name':
                    name = data.text.replace('{', '').replace('}', '')
                    trigger_info = name.split('-')
                    if len(trigger_info) == 2:
                        verb = trigger_info[0]
                        noun = trigger_info[1]
                    else:
                        verb = trigger_info[0]
                        noun = ''
                    break
            trigger = creat_triggerNode(name, graph)
            trigger.name = name
            trigger.verb = verb
            trigger.noun = noun
            trigger_nodes[trigger_id] = trigger
        elif node.attrib['labels'] == ":EVENTNODE":
            # event node
            event_id = node.attrib['id'].replace('{', '').replace('}', '')
            event = EventNode()
            for data in node.findall('data'):
                if data.attrib['key'] == 'trigger':
                    # 添加eventNode与triggerNode的关系
                    e_triggers = data.text.replace('[', '').replace(']', '').replace(' ', '').split(',')
                    event_trigger[event_id] = []
                    for e_t in e_triggers:
                        event_trigger[event_id].append(e_t.replace('{', '').replace('}', ''))
                elif data.attrib['key'] == 'title':
                    event.title = data.text.replace(u'\xa0', '').lstrip()
                elif data.attrib['key'] == 'time':
                    event.time = data.text
                elif data.attrib['key'] == 'person':
                    event.persons = data.text.replace('[', '').replace(']', '').replace(',', '')
                elif data.attrib['key'] == 'location':
                    event.locations = data.text.replace('[', '').replace(']', '').replace(',', '')
                elif data.attrib['key'] == 'organization':
                    event.organizations = data.text.replace('[', '').replace(']', '').replace(',', '')
                elif data.attrib['key'] == 'keywords':
                    event.keywords = data.text.replace('[', '').replace(']', '').replace(',', '')
            event.theme = theme  # 添加事件主题
            event_nodes[event_id] = event
        else:
            print("some error in dataconvert")
            return

            # 构建event <- trigger关系
    for e_id, tris in event_trigger.items():
        for t_id in tris:
            event_nodes[e_id].triggers.add(trigger_nodes[t_id])
            trigger_nodes[t_id].belong_tos.add(event_nodes[e_id])

    # 构建trigger -> trigger关系
    for edge in edges.findall('edge'):
        source_node = trigger_nodes[edge.attrib['source'].replace('{', '').replace('}', '')]
        target_node = trigger_nodes[edge.attrib['target'].replace('{', '').replace('}', '')]
        weight = 0
        for data in edge.findall('data'):
            if data.attrib['key'] == 'weight':
                weight = data.text
        source_node.next_triggers.add(target_node, properties={'weight': weight})

    # 构建event -> event关系
    for e in event_nodes.values():
        # 找到当前事件e的触发词集合T1
        # 得到该触发词集合的next集合T2
        # 得到T2的事件集合E2        当出现一个触发词多个事件时, 此操作会引入其他事件的节点, 因此需要进行一部过滤操作  bug date: 2019-04-10
        # 构建e -> E2 - {e}的事件关系
        next_trigger_set = set()  # T2集合
        next_event_set = set()  # E2集合
        for t in e.triggers:
            for next_t in t.next_triggers:
                next_trigger_set.add(next_t)  # 获取T2集合
        # print(len(next_trigger_set))
        for next_t in next_trigger_set:
            for re_e in next_t.belong_tos:
                if re_e.theme == theme: # 当出现一个触发词多个事件时, 得到E2集合的过程会引入其他事件的节点, 因此需要进行一部过滤操作  bug date: 2019-04-10
                    next_event_set.add(re_e)  # 获取E2集合
        # print(len(next_event_set))

        if e in next_event_set:
            next_event_set.remove(e)

        for next_e in next_event_set:
            e.next_events.add(next_e)

    # 更新数据库
    for e_n in event_nodes.values():
        graph.push(e_n)
    for t_n in trigger_nodes.values():
        graph.push(t_n)

    return 0
'''
def creat_eventNode(name, graph):
'''

def creat_triggerNode(name, graph):
    results = list(TriggerNode.match(graph, name))
    if(len(results) == 0): 
        return TriggerNode()
    else:
        return results[0]

if __name__ == '__main__':
    graph = Graph(password='123456')
    adddata("../data/李文星_Sample.xml", graph, "李文星")
