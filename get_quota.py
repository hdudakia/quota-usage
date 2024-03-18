import sys
import requests
import os

LOG_FILE = 'quota_usage.log'

def fetch_data(api_url, api_token):
    headers = {'Authorization': f'APIToken {api_token}'}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()

def extract_objects_data(data):
    objects_data = data.get('objects', {})
    return objects_data

def categorize_objects(objects_data):
    results = {'Less than 5': [], 'All': []}
    for object_name, object_info in objects_data.items():
        limit = object_info.get('limit', {}).get('maximum')
        if limit == -1:
            continue
        usage = object_info.get('usage', {}).get('current')
        if usage is None:
            continue
        difference = limit - usage
        result = f"Object Name: {object_name}, Limit: {limit}, Usage: {usage}, Difference: {difference}"
        if difference <= 5:
            results['Less than 5'].append(result)
        results['All'].append(result)
    return results

def update_log(results):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            existing_results = f.read()
    else:
        existing_results = ''

    with open(LOG_FILE, 'w') as f:
        if results['Less than 5']:
            f.write("Less than 5:\n")
            for result in results['Less than 5']:
                f.write(result + '\n')
            f.write('\n')
        f.write("All:\n")
        for result in results['All']:
            f.write(result + '\n')
        f.write('\n')
        f.write(existing_results)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <api_url> <api_token>")
        sys.exit(1)

    api_url = sys.argv[1]
    api_token = sys.argv[2]

    try:
        data = fetch_data(api_url, api_token)
        objects_data = extract_objects_data(data)
        results = categorize_objects(objects_data)
        update_log(results)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

