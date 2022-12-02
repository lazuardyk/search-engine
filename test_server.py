import time
import requests

total_time = 0
n = 1000
for i in range(n):
    start = time.perf_counter()
    url = "http://jft.web.id/search-engine/api/v1.0/overall_ranking/similarity?keyword=presiden&sort=similarity&start=0&length=100"
    response = requests.get(url)
    request_time = time.perf_counter() - start
    total_time += request_time
    print(total_time, request_time, i)
print("~")
print(total_time / n)
# store request_time in persistent data store
