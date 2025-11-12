"""
Knowledge graph for storing and querying structured knowledge
"""

import os
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timezone
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
from loguru import logger

from ..core.config import KnowledgeConfig


class KnowledgeGraph:
    """Knowledge graph for storing entities and their relationships"""
    
    def __init__(self, config: KnowledgeConfig, memory_path: str = "./memory"):
        self.config = config
        self.memory_path = memory_path
        self._ensure_memory_directory()
        
        # Graph structure
        self.graph = nx.MultiDiGraph()
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: Dict[str, Dict[str, Any]] = {}
        
        # Indexes for efficient querying
        self.type_index: Dict[str, Set[str]] = {}
        self.attribute_index: Dict[str, Dict[str, Set[str]]] = {}
        
        # Statistics
        self.creation_time = datetime.now(timezone.utc)
        self.last_updated = datetime.now(timezone.utc)
        
        # Load existing knowledge graph
        self._load_knowledge_graph()
        
        logger.info("Knowledge graph initialized")
        
    def _ensure_memory_directory(self):
        """Ensure knowledge graph directory exists"""
        os.makedirs(self.memory_path, exist_ok=True)
        
    def _load_knowledge_graph(self):
        """Load existing knowledge graph from disk (JSON format for security)"""
        graph_file = os.path.join(self.memory_path, "knowledge_graph.json")
        entities_file = os.path.join(self.memory_path, "entities.json")
        indexes_file = os.path.join(self.memory_path, "kg_indexes.json")

        # Legacy pickle file (migrate to JSON if exists)
        legacy_graph_file = os.path.join(self.memory_path, "knowledge_graph.pkl")

        if os.path.exists(graph_file):
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                    self.graph = json_graph.node_link_graph(graph_data)

                with open(entities_file, 'r', encoding='utf-8') as f:
                    self.entities = json.load(f)

                with open(indexes_file, 'r', encoding='utf-8') as f:
                    indexes_data = json.load(f)
                    self.type_index = {k: set(v) for k, v in indexes_data.get("type_index", {}).items()}
                    self.attribute_index = {
                        k: {attr: set(vals) for attr, vals in v.items()}
                        for k, v in indexes_data.get("attribute_index", {}).items()
                    }

                logger.info("Knowledge graph loaded from disk (JSON)")

            except Exception as e:
                logger.warning(f"Failed to load knowledge graph: {e}")

        elif os.path.exists(legacy_graph_file):
            logger.warning("Legacy pickle format detected. Please run migration to JSON format.")
            logger.warning("For security, pickle format is no longer supported.")
                
    def _save_knowledge_graph(self):
        """Save knowledge graph to disk (secure JSON format)"""
        graph_file = os.path.join(self.memory_path, "knowledge_graph.json")
        entities_file = os.path.join(self.memory_path, "entities.json")
        indexes_file = os.path.join(self.memory_path, "kg_indexes.json")

        try:
            # Use atomic write (write to temp file, then rename)
            graph_temp = graph_file + ".tmp"
            entities_temp = entities_file + ".tmp"
            indexes_temp = indexes_file + ".tmp"

            # Save graph structure as JSON
            with open(graph_temp, 'w', encoding='utf-8') as f:
                graph_data = json_graph.node_link_data(self.graph)
                json.dump(graph_data, f, indent=2, default=str)

            # Save entities
            with open(entities_temp, 'w', encoding='utf-8') as f:
                json.dump(self.entities, f, indent=2, default=str, ensure_ascii=False)

            # Save indexes
            with open(indexes_temp, 'w', encoding='utf-8') as f:
                indexes_data = {
                    "type_index": {k: list(v) for k, v in self.type_index.items()},
                    "attribute_index": {
                        k: {attr: list(vals) for attr, vals in v.items()}
                        for k, v in self.attribute_index.items()
                    }
                }
                json.dump(indexes_data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            os.replace(graph_temp, graph_file)
            os.replace(entities_temp, entities_file)
            os.replace(indexes_temp, indexes_file)

            logger.debug("Knowledge graph saved to disk (JSON)")

        except Exception as e:
            logger.warning(f"Failed to save knowledge graph: {e}")
            # Clean up temp files
            for temp_file in [graph_temp, entities_temp, indexes_temp]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
    def add_entity(self, entity_data: Dict[str, Any]) -> str:
        """Add a new entity to the knowledge graph"""
        
        # Check capacity
        if len(self.entities) >= self.config.max_entities:
            self._remove_least_important_entity()
            
        # Generate entity ID if not provided
        entity_id = entity_data.get("id") or f"entity_{datetime.now(timezone.utc).timestamp()}"
        
        # Create entity
        entity = {
            "id": entity_id,
            "name": entity_data.get("name", ""),
            "type": entity_data.get("type", "unknown"),
            "attributes": entity_data.get("attributes", {}),
            "description": entity_data.get("description", ""),
            "importance": entity_data.get("importance", 0.5),
            "created_at": datetime.now(timezone.utc),
            "last_accessed": datetime.now(timezone.utc),
            "access_count": 0,
            "confidence": entity_data.get("confidence", 1.0)
        }
        
        # Add to storage
        self.entities[entity_id] = entity
        
        # Add to graph
        self.graph.add_node(entity_id, **entity)
        
        # Update indexes
        self._update_entity_indexes(entity_id, entity)
        
        self.last_updated = datetime.now(timezone.utc)
        self._save_knowledge_graph()

        logger.info(f"Added entity: {entity_id}")
        return entity_id
        
    def add_relation(self, relation_data: Dict[str, Any]) -> str:
        """Add a new relation between entities"""
        
        # Check capacity
        if len(self.relations) >= self.config.max_relations:
            self._remove_least_important_relation()
            
        # Validate entities exist
        source_id = relation_data.get("source")
        target_id = relation_data.get("target")
        
        if source_id not in self.entities or target_id not in self.entities:
            raise ValueError("Source or target entity does not exist")
            
        # Generate relation ID
        relation_id = f"rel_{datetime.now(timezone.utc).timestamp()}"
        
        # Create relation
        relation = {
            "id": relation_id,
            "source": source_id,
            "target": target_id,
            "type": relation_data.get("type", "related_to"),
            "attributes": relation_data.get("attributes", {}),
            "importance": relation_data.get("importance", 0.5),
            "confidence": relation_data.get("confidence", 1.0),
            "created_at": datetime.now(timezone.utc),
            "bidirectional": relation_data.get("bidirectional", False)
        }
        
        # Add to storage
        self.relations[relation_id] = relation
        
        # Add to graph
        self.graph.add_edge(
            source_id, target_id,
            key=relation_id,
            **relation
        )
        
        # Add reverse edge if bidirectional
        if relation["bidirectional"]:
            reverse_relation = relation.copy()
            reverse_relation["source"] = target_id
            reverse_relation["target"] = source_id
            reverse_relation["id"] = f"reverse_{relation_id}"
            
            self.graph.add_edge(
                target_id, source_id,
                key=reverse_relation["id"],
                **reverse_relation
            )
            
        self.last_updated = datetime.now(timezone.utc)
        self._save_knowledge_graph()

        logger.info(f"Added relation: {relation_id}")
        return relation_id
        
    def _update_entity_indexes(self, entity_id: str, entity: Dict[str, Any]) -> None:
        """Update indexes for efficient entity querying"""
        
        # Type index
        entity_type = entity["type"]
        if entity_type not in self.type_index:
            self.type_index[entity_type] = set()
        self.type_index[entity_type].add(entity_id)
        
        # Attribute index
        for attr_name, attr_value in entity["attributes"].items():
            if attr_name not in self.attribute_index:
                self.attribute_index[attr_name] = {}
            if attr_value not in self.attribute_index[attr_name]:
                self.attribute_index[attr_name][attr_value] = set()
            self.attribute_index[attr_name][attr_value].add(entity_id)
            
    def _remove_least_important_entity(self) -> None:
        """Remove the least important entity to make space"""
        
        if not self.entities:
            return
            
        least_important_id = min(
            self.entities.keys(),
            key=lambda eid: self.entities[eid]["importance"] * 
                          (1 + self.entities[eid]["access_count"] * 0.1)
        )
        
        self.remove_entity(least_important_id)
        
    def _remove_least_important_relation(self) -> None:
        """Remove the least important relation to make space"""
        
        if not self.relations:
            return
            
        least_important_id = min(
            self.relations.keys(),
            key=lambda rid: self.relations[rid]["importance"]
        )
        
        self.remove_relation(least_important_id)
        
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID"""
        
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity["last_accessed"] = datetime.now(timezone.utc)
            entity["access_count"] += 1
            return entity.copy()
            
        return None
        
    def get_relation(self, relation_id: str) -> Optional[Dict[str, Any]]:
        """Get a relation by ID"""
        
        return self.relations.get(relation_id)
        
    def query(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query the knowledge graph for relevant entities and relations"""
        
        query_lower = query_text.lower()
        results = []
        
        # Search entities
        for entity_id, entity in self.entities.items():
            relevance = 0.0
            
            # Name matching
            if query_lower in entity["name"].lower():
                relevance += 1.0
                
            # Description matching
            if query_lower in entity["description"].lower():
                relevance += 0.8
                
            # Attribute matching
            for attr_value in entity["attributes"].values():
                if query_lower in str(attr_value).lower():
                    relevance += 0.5
                    
            # Type matching
            if query_lower in entity["type"].lower():
                relevance += 0.3
                
            # Boost by importance
            relevance += entity["importance"] * 0.3
            
            if relevance > 0:
                results.append({
                    **entity,
                    "type": "entity",
                    "relevance": relevance
                })
                
        # Search relations
        for relation in self.relations.values():
            relevance = 0.0
            
            # Relation type matching
            if query_lower in relation["type"].lower():
                relevance += 0.8
                
            # Boost by importance
            relevance += relation["importance"] * 0.2
            
            if relevance > 0:
                # Get source and target entity names
                source_entity = self.entities.get(relation["source"], {})
                target_entity = self.entities.get(relation["target"], {})
                
                results.append({
                    **relation,
                    "type": "relation",
                    "source_name": source_entity.get("name", "Unknown"),
                    "target_name": target_entity.get("name", "Unknown"),
                    "relevance": relevance
                })
                
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]
        
    def find_related_entities(self, entity_id: str, relation_types: Optional[List[str]] = None,
                             max_depth: int = 2) -> List[Dict[str, Any]]:
        """Find entities related to a given entity"""
        
        if entity_id not in self.entities:
            return []
            
        related_entities = []
        
        try:
            # Use networkx to find related entities
            for target_id, path_info in nx.single_source_shortest_path_length(
                self.graph, entity_id, cutoff=max_depth
            ).items():
                
                if target_id == entity_id or target_id not in self.entities:
                    continue
                    
                # Check if path has valid relations
                path = nx.shortest_path(self.graph, entity_id, target_id)
                
                if len(path) < 2:
                    continue
                    
                # Check relation types if specified
                if relation_types:
                    valid_path = False
                    for i in range(len(path) - 1):
                        edges = self.graph[path[i]][path[target_id]]
                        for edge_data in edges.values():
                            if edge_data.get("type") in relation_types:
                                valid_path = True
                                break
                        if valid_path:
                            break
                            
                    if not valid_path:
                        continue
                        
                entity = self.get_entity(target_id)
                if entity:
                    entity["relationship_distance"] = path_info
                    entity["relationship_strength"] = 1.0 / (path_info + 1)
                    related_entities.append(entity)
                    
        except nx.NetworkXError:
            pass
            
        # Sort by relationship strength
        related_entities.sort(key=lambda x: x["relationship_strength"], reverse=True)
        return related_entities
        
    def find_entities_by_type(self, entity_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find entities by type"""
        
        if entity_type not in self.type_index:
            return []
            
        entities = []
        for entity_id in self.type_index[entity_type]:
            entity = self.get_entity(entity_id)
            if entity:
                entities.append(entity)
                
        # Sort by importance and return top results
        entities.sort(key=lambda x: x["importance"], reverse=True)
        return entities[:limit]
        
    def find_entities_by_attribute(self, attribute_name: str, attribute_value: str,
                                  limit: int = 10) -> List[Dict[str, Any]]:
        """Find entities by attribute value"""
        
        if (attribute_name not in self.attribute_index or 
            attribute_value not in self.attribute_index[attribute_name]):
            return []
            
        entities = []
        for entity_id in self.attribute_index[attribute_name][attribute_value]:
            entity = self.get_entity(entity_id)
            if entity:
                entities.append(entity)
                
        # Sort by importance and return top results
        entities.sort(key=lambda x: x["importance"], reverse=True)
        return entities[:limit]
        
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity and all its relations"""
        
        if entity_id not in self.entities:
            return False
            
        entity = self.entities[entity_id]
        
        # Remove from indexes
        entity_type = entity["type"]
        if entity_type in self.type_index:
            self.type_index[entity_type].discard(entity_id)
            
        for attr_name, attr_value in entity["attributes"].items():
            if (attr_name in self.attribute_index and 
                attr_value in self.attribute_index[attr_name]):
                self.attribute_index[attr_name][attr_value].discard(entity_id)
                
        # Remove relations
        relations_to_remove = []
        for relation_id, relation in self.relations.items():
            if relation["source"] == entity_id or relation["target"] == entity_id:
                relations_to_remove.append(relation_id)
                
        for relation_id in relations_to_remove:
            self.remove_relation(relation_id)
            
        # Remove from graph and storage
        if entity_id in self.graph:
            self.graph.remove_node(entity_id)
            
        del self.entities[entity_id]

        self.last_updated = datetime.now(timezone.utc)
        self._save_knowledge_graph()

        return True
        
    def remove_relation(self, relation_id: str) -> bool:
        """Remove a relation"""
        
        if relation_id not in self.relations:
            return False
            
        relation = self.relations[relation_id]
        
        # Remove from graph
        if self.graph.has_edge(relation["source"], relation["target"], key=relation_id):
            self.graph.remove_edge(relation["source"], relation["target"], key=relation_id)
            
        # Remove reverse edge if exists
        reverse_id = f"reverse_{relation_id}"
        if self.graph.has_edge(relation["target"], relation["source"], key=reverse_id):
            self.graph.remove_edge(relation["target"], relation["source"], key=reverse_id)
            
        # Remove from storage
        del self.relations[relation_id]

        self.last_updated = datetime.now(timezone.utc)
        self._save_knowledge_graph()

        return True
        
    def cleanup(self) -> None:
        """Clean up the knowledge graph by removing low-importance items"""
        
        logger.info("Cleaning up knowledge graph")
        
        # Remove entities with very low importance
        entities_to_remove = []
        for entity_id, entity in self.entities.items():
            if entity["importance"] < 0.1 and entity["access_count"] == 0:
                entities_to_remove.append(entity_id)
                
        for entity_id in entities_to_remove:
            self.remove_entity(entity_id)
            
        # Remove relations with very low importance
        relations_to_remove = []
        for relation_id, relation in self.relations.items():
            if relation["importance"] < 0.1:
                relations_to_remove.append(relation_id)
                
        for relation_id in relations_to_remove:
            self.remove_relation(relation_id)
            
        logger.info(f"Cleaned up {len(entities_to_remove)} entities and {len(relations_to_remove)} relations")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "graph_nodes": self.graph.number_of_nodes(),
            "graph_edges": self.graph.number_of_edges(),
            "entity_types": len(self.type_index),
            "indexed_attributes": len(self.attribute_index),
            "creation_time": self.creation_time.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "average_entity_importance": np.mean([
                e["importance"] for e in self.entities.values()
            ]) if self.entities else 0.0,
            "average_relation_importance": np.mean([
                r["importance"] for r in self.relations.values()
            ]) if self.relations else 0.0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert knowledge graph to dictionary for serialization"""
        
        serializable_entities = {}
        for entity_id, entity in self.entities.items():
            serializable_entity = entity.copy()
            serializable_entity["created_at"] = entity["created_at"].isoformat()
            serializable_entity["last_accessed"] = entity["last_accessed"].isoformat()
            serializable_entities[entity_id] = serializable_entity
            
        serializable_relations = {}
        for relation_id, relation in self.relations.items():
            serializable_relation = relation.copy()
            serializable_relation["created_at"] = relation["created_at"].isoformat()
            serializable_relations[relation_id] = serializable_relation
            
        return {
            "entities": serializable_entities,
            "relations": serializable_relations,
            "type_index": {k: list(v) for k, v in self.type_index.items()},
            "attribute_index": {
                k: {attr: list(vals) for attr, vals in v.items()}
                for k, v in self.attribute_index.items()
            },
            "statistics": self.get_statistics()
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load knowledge graph from dictionary"""
        
        # Load entities
        self.entities.clear()
        for entity_id, entity_data in data.get("entities", {}).items():
            entity = entity_data.copy()
            entity["created_at"] = datetime.fromisoformat(entity["created_at"])
            entity["last_accessed"] = datetime.fromisoformat(entity["last_accessed"])
            self.entities[entity_id] = entity
            
        # Load relations
        self.relations.clear()
        for relation_id, relation_data in data.get("relations", {}).items():
            relation = relation_data.copy()
            relation["created_at"] = datetime.fromisoformat(relation["created_at"])
            self.relations[relation_id] = relation
            
        # Rebuild indexes
        self.type_index = {k: set(v) for k, v in data.get("type_index", {}).items()}
        self.attribute_index = {
            k: {attr: set(vals) for attr, vals in v.items()}
            for k, v in data.get("attribute_index", {}).items()
        }
        
        # Rebuild graph
        self.graph = nx.MultiDiGraph()
        
        # Add nodes
        for entity_id, entity in self.entities.items():
            self.graph.add_node(entity_id, **entity)
            
        # Add edges
        for relation in self.relations.values():
            self.graph.add_edge(
                relation["source"],
                relation["target"],
                key=relation["id"],
                **relation
            )
            
        logger.info("Knowledge graph loaded from dictionary")
