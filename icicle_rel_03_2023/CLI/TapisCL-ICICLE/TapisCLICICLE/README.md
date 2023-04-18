## For those interested
###
### Design
TapisCLICICLE uses a localhost client server model to run the application. While this did introduce some complexites to the code, it has several benefits.
1. The Tapis objects, and all other initialization only needs to happen once when the server is turned on. Initialization takes both time, and resources
2. The user only has to log in once for a 5 minute extendable session, so if they want to run commands directly from a bash environment they do not have to log in for every command
3. The program doesnt have to continuously make new login requests to the Tapis service they are connecting to