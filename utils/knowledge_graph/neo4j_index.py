from typing import List, Dict

from neo4j import GraphDatabase

def create_index_by_entities(uri: str, user: str, password: str,index_name: str, property_name: str) -> None:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        # Check if the index already exists
        result = session.run("SHOW INDEXES")
        existing_indexes = {record["name"] for record in result}

        if index_name not in existing_indexes:
            sql = f"CREATE INDEX {index_name} FOR (n) ON (n.{property_name})"
            print(f'create sql  {sql}')
            # Create a common index for the specified property across all labels
            session.run(sql)
            print(f"Index {index_name} created.")
        else:
            print(f"Index {index_name} already exists.")
    driver.close()