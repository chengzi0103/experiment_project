from neo4j import GraphDatabase
def execute_cypher_statements(uri: str, user: str, password: str,cypher: str, ) -> None:
    """
    uri = bolt://localhost:7687
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        session.write_transaction(lambda tx: tx.run(cypher))
    driver.close()
