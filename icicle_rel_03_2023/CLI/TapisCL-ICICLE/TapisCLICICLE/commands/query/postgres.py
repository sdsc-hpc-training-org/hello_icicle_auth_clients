import psycopg2
try:
    from ...utilities import decorators
    from .. import baseCommand
except:
    import utilities.decorators as decorators
    import commands.baseCommand as baseCommand


class postgres(baseCommand.BaseQuery):
    """
    @help: integrated CLI to interface with Postgres pods
    """
    decorator=decorators.RequiresExpression()
    async def run(self, id: str, expression: str=None, *args, **kwargs) -> str:
        uname, pword = self.get_pod_credentials(id)
        with psycopg2.connect(f"postgresql://{uname}:{pword}@{id}.pods.{self.t.base_url.split('https://')[1]}:443") as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(query=expression)
                return_value = cur.fetchall()
        return str(f'[+][{id}] {return_value}')