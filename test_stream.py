import asyncio
import axios_python

def test_stream_sync():
    print("--- Testing Stream Sync ---")
    
    # 1. Non-stream request (parity check)
    res_normal = axios_python.get("https://httpbin.org/get")
    assert res_normal.data is not None
    print("Normal GET OK")

    # 2. Stream request
    with axios_python.get("https://httpbin.org/stream-bytes/100", stream=True) as res:
        print("Stream GET response status:", res.status_code)
        assert res.data is None
        bytes_received = 0
        for chunk in res.iter_bytes(chunk_size=10):
            bytes_received += len(chunk)
        print(f"Stream iter_bytes OK, read {bytes_received} bytes")
        
    # 3. Stream text and lines
    with axios_python.get("https://httpbin.org/get", stream=True) as res:
        text_content = ""
        for text in res.iter_text(chunk_size=128):
            text_content += text
        print(f"Stream iter_text OK, length {len(text_content)}")

async def test_stream_async():
    print("\n--- Testing Stream Async ---")
    
    async with await axios_python.async_get("https://httpbin.org/stream-bytes/100", stream=True) as res:
        print("Async Stream GET response status:", res.status_code)
        assert res.data is None
        bytes_received = 0
        async for chunk in res.aiter_bytes(chunk_size=10):
            bytes_received += len(chunk)
        print(f"Async Stream aiter_bytes OK, read {bytes_received} bytes")

if __name__ == "__main__":
    test_stream_sync()
    asyncio.run(test_stream_async())
