import json

import requests
import time

# 🔐 Replace this with your actual API key
API_KEY = "HG2vLJlM5LNFa4ezTxRw5Ht8UTz03Mt5"
BASE_URL = "https://openapi.weshop.ai/openapi/v1"

HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

def create_task(image_url):
    payload = {
        "agentName": "aipose",
        "agentVersion": "v1.0",
        "initParams": {
            "taskName": "PoseChangeExample",
            "batchCount": "1",
            "originalImage": image_url
        }
    }
    resp = requests.post(f"{BASE_URL}/agent/task/create", json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["data"]["taskId"]

def execute_task(task_id, textDescription):
    params = {
        "taskId": task_id,
        "params": {
            "generatedContent": "referToOrigin ", #"freeCreation",
            "maskType": "autoSubjectSegment",
            "pose" : "freePose",
            'textDescription' : textDescription,
        }
    }
    resp = requests.post(f"{BASE_URL}/agent/task/execute", json=params, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["data"]["executionId"]

def poll_execution(execution_id, timeout=60, interval=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.post(f"{BASE_URL}/agent/task/query", json={"executionId": execution_id}, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()["data"]["executions"][0]
        status = data["status"]
        if status.lower() == "success":
            return [r["image"] for r in data["result"] if r["status"].lower() == "success"]
        elif status.lower() in ("failed",):
            raise RuntimeError("Task failed:", data)
        time.sleep(interval)
    raise TimeoutError("Timed out waiting for execution result!")


def upload_image(local_path):
    url = "https://openapi.weshop.ai/openapi/v1/asset/upload/image"
    headers = {"Authorization": API_KEY}
    files = {"image": open(local_path, "rb")}

    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()["data"]["image"]



if __name__ == "__main__":
    # orig_img_url = "https://yourserver.com/my_input.jpg"
    # Step 1: Upload image
    local_img_path = "C:/Users/Lab/Downloads/background_image.png"
    # uploaded_url = upload_image(local_img_path)
    uploaded_url = 'https://ai-global-image.weshop.com/20250619_1_a0309eff-3880-4a10-aca0-d6cf0544398c_512x512.png'
    print("🖼 Uploaded image URL:", uploaded_url)

    # task_id = create_task(uploaded_url)
    task_id = '6853c1b0652b73c4d20c1b69'
    print("✅ Created task:", task_id)

    exec_id = execute_task(task_id, textDescription="change pose to profile (side view). keep same identity")
    print("🛠 Execution started:", exec_id)

    results = poll_execution(exec_id)
    print("🎯 Pose-changed image URLs:")
    for url in results:
        print("-", url)
