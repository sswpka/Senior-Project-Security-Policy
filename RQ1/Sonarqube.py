import threading
import time
import subprocess
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
import tqdm 
import json
import csv
import os
import requests

load_dotenv()
sonarToken = os.getenv('SONAR_TOKEN')
git_token = os.getenv('git_token')
projectKey = os.getenv('project_key')
username = os.getenv('username')
password = os.getenv('password')

environmentPath = "/sonarCloud/box/"
resultPath = "/sonarCloud/collected_sonarqube/"

app = Flask(__name__)
scanComplete = False

@app.route('/sonar-webhook', methods=['POST'])
def sonar_webhook():
    global scanComplete
    payload = request.json
    print(f"Received webhook: {payload}")
    
    if payload.get('status') == 'SUCCESS':
        print("SUCCESS check webhook")
        scanComplete = True
    
    return jsonify({'status': 'received'}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)

webhookThread = threading.Thread(target=run_flask)
webhookThread.daemon = True
webhookThread.start()

def clonerepo(repoLink):
    cmd = f"cd box && git clone https://github.com/{repoLink}.git"
    subprocess.run(cmd, shell=True, text=True)

def deleteRepo(repoPath):
    repoInternalPath = f"{repoPath}".split('/')[-1]
    cmd = f"cd box && rm -fr {repoInternalPath}"
    subprocess.run(cmd, shell=True, text=True)

def sq_scan(dirscan):

    command = [
        "docker", "run",
        "--rm", 
        "-e", "SONAR_HOST_URL=http://xxx.xxx.xxx.xxx:9000",
        "-e", f"SONAR_SCANNER_OPTS=-Xms15g -Xmx30g -Dsonar.projectKey={projectKey} -Dsonar.token={sonarToken} -Dsonar.exclusions=**/*.java",
        "-v", f"{dirscan}:/usr/src",
        "sonarsource/sonar-scanner-cli"
    ]


    subprocess.run(command)

def getSqResult(skipWebhook=False):

    global scanComplete
    
    if not scanComplete and not skipWebhook:
        i = 0
        while not scanComplete:
            print(f"waiting... {i}/600")
            time.sleep(15)
            i += 15
            if i > 600:
                return False
    
    print("requesting result...")

    base_url = 'http://xxx.xxx.xxx.xxx:9000/api/issues/search'
    impactSeverities = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]
    issueTypes = ["CODE_SMELL", "BUG", "VULNERABILITY"]
    pageSize = 500  # Max allowed
    
    for issue_type in issueTypes:
        for severity in impactSeverities:
            url = (f"{base_url}?projectKeys={projectKey}&issueStatuses=OPEN"
                   f"&impactSeverities={severity}&types={issue_type}&p=1&ps={pageSize}")
            
            try:
                response = requests.get(url, auth=(username, password))
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error requesting SonarQube API for {issue_type}_{severity}: {e}")
                continue  # Skip this combination if request fails
            
            fileName = f"{sq_location}/{issue_type.lower()}_{severity.lower()}.json"
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
            
            with open(fileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            print(f"Saved {fileName}")
    
    return True

def read_csv_as_list(file_path):
    with open(file_path, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        data = [row[0] for row in reader] 
    return data


# Main processing loop

with open('AllPackages679_Starter.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

start_index = 0
errorList = []

for entry in tqdm.tqdm(data[start_index:], desc="Processing items"):


        repoName = entry.get("project_name").replace("/", "@")
        path = environmentPath + repoName
        sq_location = resultPath + repoName + ".json"
        
        clonerepo(entry.get("project_name"))
        sq_scan(environmentPath + f"{entry.get('project_name')}".split('/')[-1])

        # Wait for the webhook before proceeding
        flag = getSqResult(entry.get("project_name"), skipWebhook=False)
        
        if flag == False:
            errorList.append(entry.get("project_name"))
        
        deleteRepo(entry.get("project_name"))

print(errorList)

with open("errorList3.txt", "w") as f:
    f.writelines("\n".join(errorList))
