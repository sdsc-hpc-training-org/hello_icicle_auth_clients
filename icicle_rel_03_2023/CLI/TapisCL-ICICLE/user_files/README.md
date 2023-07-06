### Structure:
user --- user data
  |
  --- configs
  |
  --- tenant
        |
        --- pods --- pod config files, logs, 
        |
        --- systems --- system config files, system command error logs
                |
                --- apps --- app config files, app command error logs
                |    |
                |    --- jobs --- job config files, job command error logs, job output files
                |
                --- files