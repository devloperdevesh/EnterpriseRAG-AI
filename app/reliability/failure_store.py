failed_requests = []

def save_failed_request(data):
    failed_requests.append(data)

def replay_failed_requests():

    for req in failed_requests:
        print("Replaying", req)