from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS
from typing import List, Dict
import re

class RDFBuilder:
    def __init__(self, base_ns="http://example.org/poc/"):
        # Section 10.1 : Génération RDF
        self.graph = Graph()
        self.ns = Namespace(base_ns)
        self.graph.bind("poc", self.ns)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)

    def _sanitize(self, text):
        return re.sub(r'[^a-zA-Z0-9_]', '_', text)

    def build_graph(self, entities: List[Dict], relations: List[Dict]):
        # Section 8 : Alignement ontologique (Mode Découverte)
        
        # 1. Traitement des entités
        for ent in entities:
            if ent.get('validated', True):
                ent_uri = URIRef(self.ns[self._sanitize(ent['id'])])
                self.graph.add((ent_uri, RDFS.label, Literal(ent['label'])))
                
                # Section 7.3 : Types conceptuels (rdf:type)
                if 'inferred_type' in ent:
                    type_uri = URIRef(self.ns[self._sanitize(ent['inferred_type'])])
                    self.graph.add((ent_uri, RDF.type, type_uri))
        
        # 2. Traitement des relations
        for rel in relations:
            if rel.get('status') in ['auto_validated', 'human_validated']:
                subj_uri = URIRef(self.ns[self._sanitize(rel['subject']['id'])])
                obj_uri = URIRef(self.ns[self._sanitize(rel['object']['id'])])
                
                pred_label = rel.get('predicate_clean', rel.get('predicate_raw'))
                pred_uri = URIRef(self.ns[self._sanitize(pred_label)])
                
                # Création du triplet
                self.graph.add((subj_uri, pred_uri, obj_uri))
                self.graph.add((pred_uri, RDF.type, RDF.Property))
                self.graph.add((pred_uri, RDFS.label, Literal(pred_label)))

    def serialize(self, format="turtle"):
        # Section 10.3 : Formats d'export
        return self.graph.serialize(format=format)
