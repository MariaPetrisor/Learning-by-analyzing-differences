#!/usr/bin/python2.7

'''
    File name: analyzing_differences_learning.py 
    Author: Maria Petrisor
    Date created: 27/05/2018
    Python Version: 2.7
'''


class Node:
    def __init__(self, node_name):
        self.node_name = node_name

    def get_node_name(self):
        return self.node_name

    def compare_nodes(self, new_node):
        return self.node_name == new_node.get_node_name()


class Link:
    def __init__(self, link_type, node1, node2):
        self.link_type = link_type
        self.node1 = node1
        self.node2 = node2

    def get_node1(self):
        return self.node1

    def get_node2(self):
        return self.node2

    def get_node_tuple(self):
        return (self.node1, self.node2)

    def get_link_type(self):
        return self.link_type

    def compare_links(self, new_link):
        return new_link.get_link_type() == self.link_type and new_link.get_node1().compare_nodes(self.node1) and \
               new_link.get_node2().compare_nodes(self.node2)

    def to_string(self):
        return "{}({}, {})".format(self.link_type, self.node1.get_node_name(), self.node2.get_node_name())


class Model:
    def __init__(self, node_list, link_list):
        self.node_list = node_list
        self.link_list = link_list

    def get_node_list(self):
        return self.node_list

    def get_link_list(self):
        return self.link_list

    def add_link(self, new_link):
        self.link_list.append(new_link)

    def require_link(self, link):
        for idx, item in enumerate(self.link_list):
            if item.compare_links(link):
                new_link_string = "must-" + link.get_link_type()
                new_link = Link(new_link_string, link.get_node1(), link.get_node2())

                self.link_list[idx] = new_link

    def forbid_link(self, link):
        new_link_string = "must-not-" + link.get_link_type()
        new_link = Link(new_link_string, link.get_node1(), link.get_node2())

        self.link_list.append(new_link)

    def specialize(self, near_miss_model):
        for link in self.link_list:
            flag = False
            for nm_link in near_miss_model.get_link_list():
                if link.compare_links(nm_link):
                    flag = True
            if not flag:
                self.require_link(link)

        for nm_link in near_miss_model.get_link_list():
            flag = False
            for link in self.link_list:
                if link.compare_links(nm_link):
                    flag = True
            if not flag:
                self.forbid_link(nm_link)

    def climb_tree(self, link1, link2, model):
        for link in self.link_list:
            if link.get_link_type() == "of-type" and link.get_node1().compare_nodes(link1.get_node2()):
                
                evolving_model_link_type = link.get_node2()
                for new_model_link in model.get_link_list():
                    if new_model_link.get_link_type() == "of-type" and \
                            new_model_link.get_node1().compare_nodes(link2.get_node2()):
                        new_model_link_type = new_model_link.get_node2()

                        if evolving_model_link_type.get_node_name() == new_model_link_type.get_node_name():
                            self.link_list.remove(link)
                            new_link = Link("must-be-a", link1.get_node1(), evolving_model_link_type)
                            
                            index = self.link_list.index(link1)
                            self.link_list[index] = new_link
                            return True
        return False

    def enlarge_set(self, link1, link2):
        new_class = link1.get_node2().get_node_name() + "-or-" + link2.get_node2().get_node_name()
        new_link = Link("must-be-a", link1.get_node1(), Node(new_class))

    def generalize(self, model):
        for link in self.link_list:
            if link.get_link_type() == "is-a":
                for new_model_link in model.get_link_list():
                    if new_model_link.get_link_type() == "is-a":
                        verdict = self.climb_tree(link, new_model_link, model)

                        if not verdict:
                            self.enlarge_set(link, new_model_link)

    
if __name__ == "__main__":

    # Evolving model
    node1 = Node("A")
    node2 = Node("B")
    node3 = Node("C")

    link1 = Link("support", node1, node2)
    link2 = Link("support", node2, node3)
    link3 = Link("left-to", node1, node3)

    evolving_model = Model([node1, node2, node3], [link1, link2, link3])

    # Near miss model with missing support edges
    nm_link = Link("left-to", node1, node3)
    near_miss_model = Model([node1, node2, node3], [nm_link])

    # The evolving model specializes learning that the support edges are necessary (must-support)
    print "Specialization 1:"
    evolving_model.specialize(near_miss_model)
    for entry in evolving_model.get_link_list():
        print entry.to_string()

    # Near miss model with nodes that touch
    nm2_link1 = Link("must-support", node1, node2)
    nm2_link2 = Link("must-support", node2, node3)
    nm2_link3 = Link("left-to", node1, node3)
    nm2_link4 = Link("touch", node1, node3)
    nm2_link5 = Link("touch", node3, node1)
    near_miss_model2 = Model([node1, node2, node3], [nm2_link1, nm2_link2, nm2_link3, nm2_link4, nm2_link5])

    # The evolving modes specializes learning that the nodes must not touch (must-not-touch)
    print "\nSpecialization 2:"
    evolving_model.specialize(near_miss_model2)
    for entry in evolving_model.get_link_list():
        print entry.to_string()

    # The evolving model will learn by generalization that the arch is not necessarily a Brick, but can be a Wedge too
    # Both are of type Block
    brick = Node("Brick")
    block = Node("Block")

    evolving_model.add_link(Link("is-a", node2, brick))
    evolving_model.add_link(Link("of-type", brick, block))

    wedge = Node("Wedge")
    new_arch_link1 = Link("must-support", node1, node2)
    new_arch_link2 = Link("must-support", node2, node3)
    new_arch_link3 = Link("left-to", node1, node3)
    new_arch_link4 = Link("must-not-touch", node1, node3)
    new_arch_link5 = Link("must-not-touch", node3, node1)
    new_arch_link6 = Link("is-a", node2, wedge)
    new_arch_link7 = Link("of-type", wedge, block)

    new_model = Model([node1, node2, node3, wedge, block], [new_arch_link1, new_arch_link2, new_arch_link3,
                                                            new_arch_link4, new_arch_link5, new_arch_link6,
                                                            new_arch_link7])

    evolving_model.generalize(new_model)
    print "\nGeneralization 1:"
    for entry in evolving_model.get_link_list():
        print entry.to_string()
