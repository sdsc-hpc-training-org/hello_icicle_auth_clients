import psycopg2


if __name__ != "__main__":
    from .. import baseCommand, decorators
    from ..arguments import argument


class postgres(baseCommand.BaseQuery):
    """
    @help: integrated CLI to interface with Postgres pods
    """
    required_arguments = [
        argument.Argument('id', positional=True),
        argument.Argument('expression', arg_type='expression')
    ]
    async def run(self, *args, **kwargs) -> str:
        uname, pword = self.get_pod_credentials(kwargs['id'])
        with psycopg2.connect(user=uname, password=pword, host=f"{kwargs['id']}.pods.{self.t.base_url.split('https://')[1]}", port=443, database=kwargs['id'], connect_timeout=10) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(query=kwargs['expression'])
                return_value = cur.fetchall()
        return str(f'[+][{kwargs["id"]}] {return_value}')