from py2neo import Graph


if __name__ != "__main__":
    from .. import baseCommand, decorators



class neo4j(baseCommand.BaseQuery):
    """
    @help: integrated CLI to interface with Neo4j pods
    """
    decorator=decorators.RequiresForm()
    async def run(self, id: str, expression: str = None, *args, **kwargs) -> str: # function to submit queries to a Neo4j knowledge graph
        uname, pword = self.get_pod_credentials(id)
        graph = Graph(f"bolt+ssc://{id}.pods.{self.t.base_url.split('https://')[1]}:443", auth=(uname, pword), secure=True, verify=True)

        try:
            return_value = graph.run(expression)
            print(type(return_value))
            if str(return_value) == '(No data)' and 'create' in expression.lower(): # if no data is returned (mostly if something is created) then just say 'success'
                return f'[+][{id}@pods.{self.t.base_url.split("https://")[1]}:443] Success'
            elif str(return_value) == '(No data)':
                return f'[-][{id}@pods.{self.t.base_url.split("https://")[1]}:443] KG is empty'

            print(return_value)
            print(type(return_value))
            return str(f'[+][{id}] {return_value}')
        except Exception as e:
            return str(e)