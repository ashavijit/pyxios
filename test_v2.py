import asyncio
import os
import axios_python

def test_sync():
    print("--- Testing Sync ---")
    print("1. Module-level get()")
    res = axios_python.get("https://httpbin.org/get", params={"test": "v2"})
    res.raise_for_status()
    print("OK, args:", res.json()["args"])

    print("2. raise_for_status() error handling")
    try:
        err_res = axios_python.get("https://httpbin.org/status/404")
        err_res.raise_for_status()
    except axios_python.HTTPStatusError as e:
        print("Caught expected HTTPStatusError:", e)

    print("3. File upload")
    with open("dummy.txt", "w") as f:
        f.write("Hello world!")
    
    with open("dummy.txt", "rb") as f:
        upload_res = axios_python.post("https://httpbin.org/post", files={"file": ("dummy.txt", f, "text/plain")})
        upload_res.raise_for_status()
        print("OK, files:", upload_res.json()["files"])
    
    os.remove("dummy.txt")

async def test_async():
    print("\n--- Testing Async ---")
    print("1. Module-level async_get()")
    res = await axios_python.async_get("https://httpbin.org/get", params={"async_test": "v2"})
    res.raise_for_status()
    print("OK, args:", res.json()["args"])

    print("2. File upload async")
    with open("dummy2.txt", "w") as f:
        f.write("Async hello!")
        
    with open("dummy2.txt", "rb") as f:
        upload_res = await axios_python.async_post("https://httpbin.org/post", files={"file": f})
        upload_res.raise_for_status()
        print("OK, files:", upload_res.json()["files"])
        
    os.remove("dummy2.txt")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
