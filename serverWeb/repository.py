import logging
from neo4j import GraphDatabase

from config import URI, USER, PASSWORD

logger = logging.getLogger(__name__)

logger.warning("getting connection...")
_driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def close():
    logger.warning("closing connection...")
    _driver.close()


def getExpertsNodeList(edu, major):
    with _driver.session() as session:
        results = session.read_transaction(_create_and_return_greeting, edu, major)
        return results


def _create_and_return_greeting(tx, edu, major):
    result = tx.run(
        "MATCH (n:experts)-[:`所属领域`]->(m:field) "
        "WHERE n.degree = $edu AND m.research_field = $major "
        "RETURN n as experts,m as field", edu=edu, major=major)
    return result
