from tapipy.tapis import Tapis
import sys

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject


class Apps(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)

    def create_app(self, **kwargs): # create a tapis app taking a json descriptor file path
        try:
            with open(kwargs['file'], 'r') as f:
                app_def = json.loads(f.read())
            url = self.t.apps.createAppVersion(**app_def)
            return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}"
        except Exception as e:
            raise e

    def get_app(self, **kwargs): # returns app information with an id and version as arguments
        try:
            app = self.t.apps.getApp(appId=kwargs['id'], appVersion=kwargs['version'])
            return app
        except Exception as e:
            raise e

    def run_job(self, **kwargs): # run a job using an app. Takes a job descriptor json file path
        try:
            with open(kwargs['file'], 'r') as f:
                app_args = json.loads(f.read())

            job = {
                "name": kwargs['name'],
                "appId": kwargs['id'], 
                "appVersion": kwargs['version'],
                "parameterSet": {"appArgs": [app_args]        
                                }
            }
            job = self.t.jobs.submitJob(**job)
            return job.uuid
        except Exception as e:
            raise e

    def get_job_status(self, **kwargs): # return a job status with its Uuid
        try:
            job_status = self.t.jobs.getJobStatus(jobUuid=kwargs['uuid'])
            return job_status
        except Exception as e:
            raise e

    def download_job_output(self, **kwargs): # download the output of a job with its Uuid
        try:
            jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=kwargs['uuid'], outputPath='tapisjob.out')
            with open(kwargs['file'], 'w') as f:
                f.write(jobs_output)
            return f"Successfully downloaded job output to {kwargs['file']}"
        except Exception as e:
            raise e

    def jobs_cli(self, **kwargs): # function to manage all jobs
        command = kwargs['command']
        try:
            if command == 'create_app':
                return self.create_app(**kwargs)
            if command == 'get_app_info':
                return self.get_app(**kwargs)
            if command == 'run_app':
                return self.run_job(**kwargs)
            if command == 'get_app_status':
                return self.get_job_status(**kwargs)
            if command == 'download_app_results':
                return self.download_job_output(**kwargs)
            else:
                raise Exception('Command not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")
        except Exception as e:
            raise e