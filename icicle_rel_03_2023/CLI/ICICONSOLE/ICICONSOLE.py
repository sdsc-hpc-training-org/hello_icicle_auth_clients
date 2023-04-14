# We need pandas to display the results of Cypher queries to the Neo4j Pod
import pandas as pd
# py2neo is the python library that allows for input to be read as Cypher by the Neo4j interface
from py2neo import Graph, Node, Relationship
from py2neo import GraphService
from py2neo import wiring
# These are optional
import time
import datetime
# This is used to securely get user password for initial authentication to TAPIS
from getpass import getpass
# This is how we actually connect to TAPIS and get the required information to connect to a Pod
from tapipy.tapis import Tapis
# These are to clear the screen
import os
import signal
import BasicCypherCommands as bcc
import json

# Recording login time
start = time.time()

# This class handles exiting the console application at any time.
class GracefulExiter():
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        print("\nPress Ctrl+C again to exit.")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state

 
# Base URL for Tapis
base_url = "https://icicle.tapis.io"
# Global variable to store pod id
pod_id = ""
# Global variable to store username, set upon initial input from login to TAPIS
user = ""

flag = GracefulExiter()

# This function formats a message to be like a title
def heavyFormat(message):
    print("*" * len(message))
    print("-" * len(message))
    print(message)
    print("-" * len(message))
    print("*" * len(message))

# This function formats a message to be like a subititle 
def lightFormat(message):
    print("-" * len(message))
    print(message)
    print("-" * len(message))

# Welcome message, formatted with the heavyFormat function
heavyFormat("Welcome to ICICONSOLE. Login to get started. ")

# Loads help for cypher commands
def helpCypher():
    print("\n")
    with open('helpCypher.json') as f:
        help_data = json.load(f)
    for key, value in help_data.items():
        print(key + ' : ' + value + '\n')

# The console function is the actual cypher console that you see after logging in and choosing a pod.
# The console allows you to type in cypher, and run it on the Neo4j pod you are connected to.
# The console function needs to parameters: a Neo4j graph object, and a pod id. 
# The graph object allows for queries to be interpreted as Cypher and passed into the Neo4j pod.
# The pod id is only needed here so that the user can see what pod they are connected to.
        
def console(graph, pod_id):
    # Instructions message, formatted with the lightFormat function
    lightFormat("Type \"new\" to access a different pod, or type \"exit\" to leave ICICONSOLE. Type \"clear\" to clear the screen. Type \"help\" for help!")

    # Loop so that the console keeps prompting the user for commands, until the user exits
    while(True):
        # This is reading the actual input from the user; the input message shows the username and the pod id
        query = str(input("[" + user + "@" + pod_id + "] "))

        executeCypher = True

        # This is a switch statement that allows for the user to type in a command, and the console will execute the command.
        match query:
            case "exit":
                os._exit(0)
                executeCypher = False
            # The command to pick a new pod to connect to. Calls the choosePod function, defined below.
            case "new":
                choosePod()
                executeCypher = False
            # The command to clear the screen. Has a recursive call to itself so that the user is once again prompted, and the instruction message is still shown.
            case "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                console(graph, pod_id)
                executeCypher = False
            case "help":
                helpCypher()
                executeCypher = False
            case "all":
                query = bcc.getAll()
            case "allNames":
                query = bcc.getAllNames()
            case "oneByName":
                query = bcc.getOneByName()
            case "allProperty":
                query = bcc.allProperty()
            case "allProperties":
                query = bcc.allProperties()
            case "allPropertiesForNode":
                query = bcc.allPropertiesForNode()
            case _:
                pass

        if (executeCypher):
            # This tries to read the input as Cypher and apply the command to the Neo4j graph object.
            try: 
                # Storing the results of the query as a pandas dataframe
                df = graph.run(query).to_data_frame()
                # Displaying the result
                with pd.option_context('expand_frame_repr', False, 'display.max_rows', None): 
                    print(df)


            # Error catching, if the Cypher was not executed properly
            except:
                if flag.exit():
                    break
                print("Something went wrong")


# This is the function that allows the user to pick a pod to connect to. It needs no paramters.
def choosePod():

    heavyFormat("Here are the IDs for your available TAPIS Pods: ")

    # The below loop prints the pod id for all pods that the TACC user is authorized to. If there are no pods, then the user is notified.
    i = 1
    # t.pods.getpods() returns a list of all of the pods with more information about each pod
    for pod in t.pods.get_pods():
        # pod.pod_id takes each element of the list, representing each pod, and extracts only the pod id
        # This is done because connecting to a Neo4j pod only requires the pod id.
        if pod.pod_template == "neo4j":
            print(str(i) + ". " + pod.pod_id)
            i += 1
    if (i == 1):
        print("You don't have access to any TAPIS Neo4j pods. Try again after you have verified access to at least one pod.")
        os._exit(0)
    i = 1

    while(True):
        try: 
            # The user gets a list of available pod ids from the above loop, and then enters the id they wish to connect to.
            # This input is stored in the pod_id variable
            pod_id = str(input("Enter the ID of the pod you want to access: ")).lower()
            # If the use has no pods or doesn't see what they are looking for, they can exit
            if(pod_id == "exit"):
                os._exit(0)
            # Securely getting the username and password associated with the pod for later authentication to connect
            pod_username, password = t.pods.get_pod_credentials(pod_id=pod_id).user_username, t.pods.get_pod_credentials(pod_id=pod_id).user_password
            break
        # This is if there is trouble getting the username and password
        except:
            if flag.exit():
                break
            print("Invalid Pod ID. Make sure you have access to this Pod.")

    # This is the standard format for the link that connects to the Neo4j Pod
    graph_link = f"bolt+ssc://{pod_id}.pods.icicle.tapis.io:443"

    while(True):
        try:
            # A graph object is created that authenticates with the previously gotten username and password. 
            graph = Graph(graph_link, auth=(pod_username, password), secure=True, verify=True)
            # Entering into the cypher console
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(0.25)
            heavyFormat(f"Hey there {user}! Welcome to the Neo4j Cypher Console for: " + str(pod_id))
            # Passing in the graph object and the current pod_id to the cypher console, and calling the console function
            console(graph, pod_id)
        # This catches the error where there is an issue connecting or authenticating to the Pod.
        except:
            if flag.exit():
                break
            print("There was a connection error.")
            break
            
# The below loop handles initial login.
while(True):
    try:
        try:
            t
            if t.base_url == base_url and t.username == user and t.access_token:
                print("Tapis object already exists.")
                if t.access_token.expires_at < datetime.datetime.now(pytz.utc):
                    raise
            else:
                raise
        except:
            try:
                user = str(input("Enter Your TACC Username: "))
                t = Tapis(base_url = base_url, username=user,
                        password = getpass('Enter Your TACC Password: '))
                t.get_tokens()
                # After logging in, choosePod is called to begin the workflow for the user.
                choosePod()
                break
            except Exception as e:
                raise
    except:
        if flag.exit():
            break
        print("An error occurred, likely due to mistyped login. Try again. ")



