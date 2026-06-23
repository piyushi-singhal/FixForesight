import socket

def check_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except:
        return False

print("PostgreSQL port 5432 open?", check_port(5432))
print("Solr port 8983 open?", check_port(8983))
print("FastAPI port 8000 open?", check_port(8000))
