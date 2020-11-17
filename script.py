import scaleapi
import requests
import json
import csv

client = scaleapi.ScaleClient('live_74275b9b2b8b44d8ad156db03d2008ed')

csv_rows = [["Row Number", "Task ID", "Severity", "UUID", "Associated Problem Description"]]
task_ids = ['5f127f6f26831d0010e985e5', '5f127f6c3a6b1000172320ad', 
            '5f127f699740b80017f9b170', '5f127f671ab28b001762c204', 
            '5f127f643a6b1000172320a5', '5f127f5f3a6b100017232099', 
            '5f127f5ab1cb1300109e4ffc', '5f127f55fdc4150010e37244']
possible_traffic_control_signs_colors_list = ["red", "green", "white", "orange", "other"]
querystring = {"customer_review_status":"","limit":"100"}
headers = {"Authorization": "Basic bGl2ZV83NDI3NWI5YjJiOGI0NGQ4YWQxNTZkYjAzZDIwMDhlZDo="}
counter = 1

for task_id in task_ids:
    url = "https://api.scale.com/v1/task/" + task_id
    response = requests.request("GET", url, headers=headers)
    obj = response.json()

    try:
        if (obj["audits"][0]["audit_result"] == 'rejected'):
            csv_rows.append([counter, task_id, "Critical", "Not Applicable", "Audit was rejected by " + obj["audits"][0]["audit_source"]])
            counter += 1
    except (SyntaxError, KeyError):
        print("Audits attribute is not found in " + obj["task_id"] + ". This picture has not been manually validated.")
    
    for itr in obj["response"]["annotations"]:
        if (itr["width"] > 450 or
            itr["height"] > 450):
                csv_rows.append([counter, task_id, "Critical", itr["uuid"], "Large entity covering a large portion of image indicates likely error."])
                counter += 1
        if (itr["top"] < 5 or
            itr["left"] < 5):
                csv_rows.append([counter, task_id, "Warning", itr["uuid"], "Item on the edge of screen can indicate a heavily truncated object or invalid labeling"])
                counter += 1
        if ((itr["attributes"]["occlusion"] != "0%" and 
            itr["attributes"]["occlusion"] != "25%") and
            itr["attributes"]["background_color"] == "not_applicable"):
                csv_rows.append([counter, task_id, "Warning", itr["uuid"], "Object with non-visible face, high occlusion, and no background color - Double check if object is a traffic sign"])
                counter += 1
        if (itr["geometry"] != "box"):
                csv_rows.append([counter, task_id, "Warning", itr["uuid"], "Geometry of object is not tightly fit"])
                counter += 1
        if (itr["label"] == "traffic_control_sign" and 
            itr["attributes"]["background_color"] not in possible_traffic_control_signs_colors_list):
                csv_rows.append([counter, task_id, "Critical", itr["uuid"], "Traffic control sign is a non-traditional color. Check if sign color is " + itr["attributes"]["background_color"]])
                counter += 1

with open('possible_errors.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(csv_rows)
print(csv_rows)
