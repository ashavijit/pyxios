import axios_python

def main():
    api = axios_python.create({"base_url": "https://httpbin.org", "timeout": 10})
    res = api.get("/get")
    print("Sync status_code:", res.status_code)
    print("Sync ok:", res.ok)
    print("Sync response keys:", list(res.json().keys()))

if __name__ == "__main__":
    main()
