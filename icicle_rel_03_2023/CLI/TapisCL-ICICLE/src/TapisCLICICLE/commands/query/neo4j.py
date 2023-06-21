from py2neo import Graph


if __name__ != "__main__":
    from .. import baseCommand, decorators
    from ..arguments import argument


class neo4j(baseCommand.BaseQuery):
    """
    @help: integrated CLI to interface with Neo4j pods
    """
    required_arguments = [
        argument.Argument('id'),
        argument.Argument('expression', arg_type='expression')
    ]
    async def run(self, *args, **kwargs) -> str: # function to submit queries to a Neo4j knowledge graph
        uname, pword = self.get_pod_credentials(kwargs["id"])
        graph = Graph(f"bolt+ssc://{kwargs['id']}.pods.{self.t.base_url.split('https://')[1]}:443", auth=(uname, pword), secure=True, verify=True)

        return_value = graph.run(kwargs['expression'])
        print(type(return_value))
        if str(return_value) == '(No data)' and 'create' in kwargs['expression'].lower(): # if no data is returned (mostly if something is created) then just say 'success'
            return f'[+][{kwargs["id"]}@pods.{self.t.base_url.split("https://")[1]}:443] Success'
        elif str(return_value) == '(No data)':
            return f'[-][{kwargs["id"]}@pods.{self.t.base_url.split("https://")[1]}:443] KG is empty'

        print(return_value)
        print(type(return_value))
        return str(f'[+][{kwargs["id"]}] {return_value}')