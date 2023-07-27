from tapipy.tapis import errors as TapisErrors


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    from . import commandOpts
    Argument = argument.Argument


class get_snapshots(baseCommand.BaseCommand):
    """
    @help: get a list of snapshots on the tenant you have access to
    """
    async def run(self, *args, **kwargs):
        return self.t.pods.get_snapshots()
    

class create_snapshot(baseCommand.BaseCommand):
    """
    @help: create a backup of the volume selected or specific files in the volume
    """
    supports_config_file=True
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('source_volume_id'), commandOpts.CHECK_PWD(('source_volume_path', 'destination_path'))]
    required_arguments = [
        Argument('snapshot_id', positional=True),
        Argument('source_volume_id', positional=True),
        Argument('source_volume_path')
    ]
    optional_arguments = [
        Argument('destination_path', description="Required if your snapshot is of a single file"),
        Argument('description', arg_type='str_input'),
        Argument('size_limit', data_type='int', description='maximum size in megabytes of the snapshot'),
        Argument('cron'),
        Argument('retention_policy')
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.create_snapshot(**kwargs)
    

class get_snapshot(baseCommand.BaseCommand):
    """
    @help: get snapshot information
    """
    required_arguments = [
        Argument('snapshot_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.get_snapshot(**kwargs)
    

class update_snapshot(baseCommand.BaseCommand):
    """
    @help: update snapshot information
    """
    supports_config_file=True
    required_arguments = [
        Argument('snapshot_id', positional=True)
    ]
    optional_arguments = [
        Argument('description', arg_type='str_input'),
        Argument('size_limit', data_type='int'),
        Argument('cron'),
        Argument('retention_policy')
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.update_snapshot(**kwargs)
    

class delete_snapshot(baseCommand.BaseCommand):
    """
    @help: delete snapshot information
    """
    required_arguments = [
        Argument('snapshot_id', positional=True),
        Argument('confirm', arg_type='confirmation')
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.delete_snapshot(**kwargs)
    

class list_snapshot_files(baseCommand.BaseCommand):
    """
    @help: list the files in a snapshot
    """
    required_arguments = [
        Argument('snapshot_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.list_snapshot_files(**kwargs)
    