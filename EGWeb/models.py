from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from py2neo import Graph


class EventNode(GraphObject):  # 实现一个对象和Node的关联
    __primarykey__ = 'title'

    theme = Property()  # 事件主题, 例如李文星、魏则西等等

    title = Property()
    time = Property()
    locations = Property()  # 以空格/逗号做分割的字符串形式
    persons = Property()
    organizations = Property()
    keywords = Property()

    next_events = RelatedTo('EventNode', 'NEXT_EVENT')
    triggers = RelatedFrom('TriggerNode', 'BELONG_TO')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.title == other.title
        else:
            return False

    def __hash__(self):
        return hash(self.title)


class TriggerNode(GraphObject):
    __primarykey__ = 'name'

    name = Property()
    verb = Property()
    noun = Property()

    belong_tos = RelatedTo('EventNode', 'BELONG_TO')
    next_triggers = RelatedTo('TriggerNode', 'NEXT_TRIGGER')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)


if __name__ == '__main__':
    graph = Graph(password='sjh19970201')

    new_event_1 = EventNode()
    new_event_2 = EventNode()
    new_trigger_1 = TriggerNode()
    new_trigger_2 = TriggerNode()

    new_event_1.theme = "李文星"
    new_event_1.title = "李文星尸体在天津静海区被发现。"
    new_event_2.theme = "李文星"
    new_event_2.title = "foo"

    new_trigger_1.name = "发现-尸体"
    new_trigger_2.name = "f"

    new_event_1.next_events.add(new_event_2)
    new_event_1.next_events.add(new_event_1)
    new_event_1.triggers.add(new_trigger_1)
    new_event_2.triggers.add(new_trigger_2)
    new_trigger_1.next_triggers.add(new_trigger_2)

    # Update the graph with changes from a GraphObject and its associated RelatedObject instances. If a corresponding remote node does not exist, one will be created. If one does exist, it will be updated. The set of outgoing relationships will be adjusted to match those described by the RelatedObject instances.

    graph.push(new_event_1)
    # graph.push(new_event_2)
    # graph.push(new_trigger_1)
    # graph.push(new_trigger_2)
