import psycopg2


if __name__ != "__main__":
    from .. import baseCommand, decorators
    from ..arguments import argument


class postgres(baseCommand.BaseQuery):
    """
    @help: integrated CLI to interface with Postgres pods
    """
    required_arguments = [
        argument.Argument('id'),
        argument.Argument('expression', arg_type='expression')
    ]
    async def run(self, *args, **kwargs) -> str:
        uname, pword = self.get_pod_credentials(kwargs['id'])
        db_con_params = {"host": f"{kwargs['id']}.pods.icicle.tapis.io",
           "port":  443,
           "database": "postgres",
           "user": uname,
           "password": pword}
        with psycopg2.connect(**db_con_params) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(query=kwargs['expression'])
                return_value = cur.fetchall()
        return str(f'[+][{kwargs["id"]}] {return_value}')