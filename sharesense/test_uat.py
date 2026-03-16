"""
ShareSense UAT Test Script
Run with: py sharesense/test_uat.py
Make sure the server is running first (py sharesense/app.py)
"""
import json
import urllib.request
import sys

BASE = "http://localhost:3000"
PASS = 0
FAIL = 0


def req(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode()), e.code


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}")


print("\n=== ShareSense UAT Tests ===\n")

# Health
print("[Health Check]")
data, code = req("GET", "/health")
test("GET /health returns 200", code == 200)
test("Status is ok", data.get("status") == "ok")

# Register User 1
print("\n[Register Users]")
data, code = req("POST", "/api/auth/register", {"email": "alice@test.com", "password": "pass123", "name": "Alice"})
test("Register Alice -> 201", code == 201)
alice_id = data.get("user", {}).get("id")
test("Alice has an ID", alice_id is not None)

# Register User 2
data, code = req("POST", "/api/auth/register", {"email": "bob@test.com", "password": "pass123", "name": "Bob"})
test("Register Bob -> 201", code == 201)
bob_id = data.get("user", {}).get("id")

# Duplicate registration
data, code = req("POST", "/api/auth/register", {"email": "alice@test.com", "password": "pass123", "name": "Alice"})
test("Duplicate email -> 409", code == 409)

# Validation
data, code = req("POST", "/api/auth/register", {"email": "bad", "password": "pass123", "name": "X"})
test("Bad email -> 400", code == 400)
data, code = req("POST", "/api/auth/register", {"email": "x@x.com", "password": "12", "name": "X"})
test("Short password -> 400", code == 400)

# Login
print("\n[Login]")
data, code = req("POST", "/api/auth/login", {"email": "alice@test.com", "password": "pass123"})
test("Login Alice -> 200", code == 200)
alice_token = data.get("token")
test("Got JWT token", alice_token is not None)

data, code = req("POST", "/api/auth/login", {"email": "bob@test.com", "password": "pass123"})
bob_token = data.get("token")
test("Login Bob -> 200", code == 200)

data, code = req("POST", "/api/auth/login", {"email": "alice@test.com", "password": "wrong"})
test("Wrong password -> 401", code == 401)

# Me
print("\n[Profile]")
data, code = req("GET", "/api/auth/me", token=alice_token)
test("GET /me -> 200", code == 200)
test("Returns Alice's name", data.get("user", {}).get("name") == "Alice")

data, code = req("GET", "/api/auth/me")
test("No token -> 401", code == 401)

# Flats
print("\n[Flats]")
data, code = req("POST", "/api/flats", {"name": "Flat 101"}, alice_token)
test("Create flat -> 201", code == 201)
flat_id = data.get("flat", {}).get("id")
test("Flat has ID", flat_id is not None)

data, code = req("GET", "/api/flats", token=alice_token)
test("List flats -> 200", code == 200)
test("Alice has 1 flat", len(data.get("flats", [])) == 1)

data, code = req("GET", "/api/flats/" + flat_id, token=alice_token)
test("Get flat by ID -> 200", code == 200)

data, code = req("GET", "/api/flats/" + flat_id, token=bob_token)
test("Bob can't see Alice's flat -> 403", code == 403)

# Members
print("\n[Members]")
data, code = req("GET", "/api/flats/" + flat_id + "/members", token=alice_token)
test("Flat has 1 member (creator)", len(data.get("members", [])) == 1)

data, code = req("POST", "/api/flats/" + flat_id + "/members", {"email": "bob@test.com"}, alice_token)
test("Add Bob by email -> 201", code == 201)

data, code = req("GET", "/api/flats/" + flat_id + "/members", token=alice_token)
test("Flat now has 2 members", len(data.get("members", [])) == 2)

data, code = req("POST", "/api/flats/" + flat_id + "/members", {"email": "bob@test.com"}, alice_token)
test("Add duplicate -> 409", code == 409)

data, code = req("POST", "/api/flats/" + flat_id + "/members", {"email": "nobody@test.com"}, alice_token)
test("Add nonexistent user -> 404", code == 404)

# Expenses
print("\n[Expenses]")
data, code = req("POST", "/api/flats/" + flat_id + "/expenses", {
    "description": "Groceries", "amount": 50.00, "payerId": alice_id
}, alice_token)
test("Add expense -> 201", code == 201)
expense_id = data.get("expense", {}).get("id")

data, code = req("POST", "/api/flats/" + flat_id + "/expenses", {
    "description": "Electricity", "amount": 30.00, "payerId": bob_id
}, bob_token)
test("Bob adds expense -> 201", code == 201)

data, code = req("GET", "/api/flats/" + flat_id + "/expenses", token=alice_token)
test("List expenses -> 200", code == 200)
test("2 expenses exist", len(data.get("expenses", [])) == 2)

data, code = req("POST", "/api/flats/" + flat_id + "/expenses", {
    "description": "", "amount": 10
}, alice_token)
test("Empty description -> 400", code == 400)

data, code = req("POST", "/api/flats/" + flat_id + "/expenses", {
    "description": "Test", "amount": -5
}, alice_token)
test("Negative amount -> 400", code == 400)

# Balances
print("\n[Balances]")
data, code = req("GET", "/api/flats/" + flat_id + "/balances", token=alice_token)
test("Get balances -> 200", code == 200)
transfers = data.get("transfers", [])
test("1 transfer needed", len(transfers) == 1)
if transfers:
    t = transfers[0]
    test("Bob pays Alice ₹10", t["from_name"] == "Bob" and t["to_name"] == "Alice" and t["amount"] == 10.0)

# Settlements
print("\n[Settlements]")
data, code = req("POST", "/api/flats/" + flat_id + "/settlements", {
    "debtorId": bob_id, "creditorId": alice_id, "amount": 10.00
}, bob_token)
test("Propose settlement -> 201", code == 201)
settlement_id = data.get("settlement", {}).get("id")
test("Status is pending", data.get("settlement", {}).get("status") == "pending")

data, code = req("POST", "/api/flats/" + flat_id + "/settlements/" + settlement_id + "/confirm", token=bob_token)
test("Bob confirms -> 200", code == 200)
test("Still pending (need both)", data.get("settlement", {}).get("status") == "pending")

data, code = req("POST", "/api/flats/" + flat_id + "/settlements/" + settlement_id + "/confirm", token=alice_token)
test("Alice confirms -> 200", code == 200)
test("Now confirmed", data.get("settlement", {}).get("status") == "confirmed")

# Delete expense
print("\n[Cleanup]")
data, code = req("DELETE", "/api/flats/" + flat_id + "/expenses/" + expense_id, token=alice_token)
test("Delete expense -> 200", code == 200)

data, code = req("GET", "/api/flats/" + flat_id + "/expenses", token=alice_token)
test("1 expense remaining", len(data.get("expenses", [])) == 1)

# Remove member
data, code = req("DELETE", "/api/flats/" + flat_id + "/members/" + bob_id, token=alice_token)
test("Remove Bob -> 200", code == 200)

# Summary
print(f"\n{'='*40}")
print(f"Results: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
if FAIL == 0:
    print("All tests passed!")
else:
    print("Some tests failed.")
    sys.exit(1)
