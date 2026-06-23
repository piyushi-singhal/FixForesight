import urllib.request
import urllib.parse
import json

def test_query(q, host="127.0.0.1", use_header=True):
    try:
        params = urllib.parse.urlencode({"q": q})
        url = f"http://{host}:8000/search?{params}"
        print(f"\nRequesting: {url} (Host header={use_header})")
        req = urllib.request.Request(url)
        if use_header:
            req.add_header("Host", "lvh.me")
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            data = json.loads(html)
            print(f"Status Code: {response.status}")
            print(f"numFound: {data.get('numFound')}")
            print(f"Docs count: {len(data.get('docs', []))}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        try:
            err_body = e.read().decode('utf-8')
            print(f"Response body: {err_body}")
        except:
            pass
    except Exception as e:
        print(f"Error querying: {e}")

test_query("*", host="127.0.0.1", use_header=True)
test_query("*", host="localhost", use_header=False)
test_query("*", host="lvh.me", use_header=False)
