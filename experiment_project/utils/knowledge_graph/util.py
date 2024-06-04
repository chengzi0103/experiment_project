def generate_cypher_statements(entities:list[dict])->str:
    cypher_statements = []

    # Create nodes
    for entity in entities:
        node_statement = f'CREATE ({entity["entity_name"]}:{entity["entity_type"]} ' \
                         f'{{entity_name: "{entity["entity_name"]}", entity_type: "{entity["entity_type"]}", ' \
                         f'description: "{entity["description"]}"}})'
        cypher_statements.append(node_statement)

    # Create relationships
    for entity in entities:
        for relationship in entity["relationships"]:
            relationship_statement = f'CREATE ({entity["entity_name"]})-[:{relationship["relation_type"]}]->' \
                                     f'({relationship["related_entity"]})'
            cypher_statements.append(relationship_statement)

    return "\n".join(cypher_statements)