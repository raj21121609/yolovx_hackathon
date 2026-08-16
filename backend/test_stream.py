import urllib.request
import json
import sqlite3

# Get latest active session
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT id FROM sessions_attendancesession WHERE status='ACTIVE' ORDER BY created_at DESC LIMIT 1")
row = cur.fetchone()
if not row:
    print("No active session found.")
    exit(1)
session_id = row[0]
print(f"Testing session: {session_id}")

# 1. Fetch status to check if it's active
try:
    req = urllib.request.Request(f"http://localhost:8000/api/sessions/{session_id}/status/")
    resp = urllib.request.urlopen(req)
    status_data = json.loads(resp.read().decode())
    print("Status:", status_data)
except Exception as e:
    print("Failed to get status:", e)

try:
    print(f"Connecting to stream for session {session_id}...")
    req2 = urllib.request.Request(f"http://localhost:8000/api/sessions/{session_id}/stream/")
    resp2 = urllib.request.urlopen(req2, timeout=5)
    print("Stream HTTP Status:", resp2.getcode())
    print("Headers:", resp2.headers)
    chunk = resp2.read(200)
    print("First chunk:", chunk)
except Exception as e:
    print("Failed to get stream:", e)

