from config import run_mode
from services import Service, API


class Wikidata_Endpoint_Service(Service):
    name = "Wikidata_Endpoint_Service"

    if run_mode == 0:
        root = "http://127.0.0.1:5007"
    else:
        root = "http://endpoint.wikidata.svc:5007"

    def __init__(self):
        self.get_type_for = API(self, self.root, "get_type_for", "text", "POST")
        self.get_type_for_lst = API(self, self.root, "get_type_for_lst", "texts", "POST")

        self.get_ancestors_for_lst = API(self, self.root, "get_ancestors_for_lst", "entities", "POST")

        self.get_hierarchy_for_lst = API(self, self.root, "get_hierarchy_for_lst", "entities", "POST")

        self.get_subclasses_for = API(self, self.root, "get_subclasses_for", "wikiclass", "POST")

        self.get_parents_for = API(self, self.root, "get_parents_for", "wikiclass", "POST")
        self.get_parents_for_lst = API(self, self.root, "get_parents_for_lst", "texts", "POST")

        self.get_connection_for_lst = API(self, self.root, "get_connection_for_lst", ["pairs"], "POST")

        # Literals
        self.get_literals_for_lst = API(self, self.root, "get_literals_for_lst", ["texts"], "POST")
        self.get_literals_topranked_for_lst = API(self, self.root, "get_literals_topranked_for_lst", ["texts"], "POST")
        self.get_literals_full_for_lst = API(self, self.root, "get_literals_full_for_lst", ["texts"], "POST")

        self.get_literals_for = API(self, self.root, "get_literals_for", ["text"], "POST")
        self.get_literals_topranked_for = API(self, self.root, "get_literals_topranked_for", ["text"], "POST")
        self.get_literals_full_for = API(self, self.root, "get_literals_full_for", ["text"], "POST")

        # Objects
        self.get_objects_for_lst = API(self, self.root, "get_objects_for_lst", ["texts"], "POST")
        self.get_objects_topranked_for_lst = API(self, self.root, "get_objects_topranked_for_lst", ["texts"], "POST")
        self.get_objects_full_for_lst = API(self, self.root, "get_objects_full_for_lst", ["texts"], "POST")

        self.get_objects_for = API(self, self.root, "get_objects_for", ["text"], "POST")
        self.get_objects_topranked_for = API(self, self.root, "get_objects_topranked_for", ["text"], "POST")
        self.get_objects_full_for = API(self, self.root, "get_objects_full_for", ["text"], "POST")

        # reverse Objects
        self.get_reverse_objects_for_lst = API(self, self.root, "get_reverse_objects_for_lst", ["entities"], "POST")
        self.get_reverse_objects_topranked_for_lst = API(self, self.root, "get_reverse_objects_topranked_for_lst", ["entities"], "POST")

        self.get_reverse_objects_classed_for_lst = API(self, self.root, "get_reverse_objects_classed_for_lst", ["entities", "class"], "POST")

        self.get_children_for_lst = API(self, self.root, "get_children_for_lst", ["entities"], "POST")

        # other
        self.get_popularity_for_lst = API(self, self.root, "get_popularity_for_lst", ["entities"], "POST")
        self.get_direct_types_for_lst = API(self, self.root, "get_direct_types_for_lst", "entities", "POST")

        # Strings
        # self.get_strings_for_lst = API(self, self.root, "get_strings_for_lst", ["texts", "lang"], "POST")
        # self.get_strings_for = API(self, self.root, "get_strings_for", ["text", "lang"], "POST")

        # Labels
        self.get_labels_for_lst = API(self, self.root, "get_labels_for_lst", ["entities", "lang"], "POST")

        # Properties
        self.get_properties_for_lst = API(self, self.root, "get_properties_for_lst", ["texts", "lang"], "POST")
        self.get_properties_topranked_for_lst = API(self, self.root, "get_properties_topranked_for_lst", ["texts", "lang"], "POST")
        self.get_properties_full_for_lst = API(self, self.root, "get_properties_full_for_lst", ["texts", "lang"], "POST")

        self.get_properties_for = API(self, self.root, "get_properties_for", ["text", "lang"], "POST")
        self.get_properties_topranked_for = API(self, self.root, "get_properties_topranked_for", ["text", "lang"], "POST")
        self.get_properties_full_for = API(self, self.root, "get_properties_full_for", ["text", "lang"], "POST")

        self.filter_entities_by_classes = API(self, self.root, "filter_entities_by_classes", ["entities", "classes"], "POST")
