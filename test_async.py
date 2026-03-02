import asyncio
import axiospy

async def main():
    api = axiospy.create({"base_url": "https://httpbin.org", "timeout": 10})
    res = await api.async_get("/get")
    print("Async status_code:", res.status_code)
    print("Async ok:", res.ok)
    print("Async response keys:", list(res.json().keys()))

if __name__ == "__main__":
    asyncio.run(main())
