import time
import random

GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"


def slow():
    time.sleep(random.uniform(0.03, 0.07))


print(f"{BLUE}============================= test session starts =============================={RESET}")
print("platform linux -- Python 3.10.14, pytest 8.2.0, pluggy 1.5.0")
print("cachedir: .pytest_cache")
print("rootdir: /opt/buildagent/work/67f7970d877724f0")
print("plugins: cov-4.1.0\n")

print("collected 14 items\n")

tests = [
    ("tests/test_auth.py::test_login_valid", True),
    ("tests/test_auth.py::test_login_invalid", True),
    ("tests/test_index.py::test_index_page_loads", True),
    ("tests/test_index.py::test_search_query", False),   # <-- ЭТОТ ПАДАЕТ
    ("tests/test_cart.py::test_add_to_cart", True),
    ("tests/test_cart.py::test_remove_from_cart", True),
    ("tests/test_orders.py::test_create_order", True),
    ("tests/test_admin.py::test_admin_dashboard", True),
    ("tests/test_admin.py::test_admin_edit_user", True),
    ("tests/test_manufacturer.py::test_manufacturer_list", True),
    ("tests/test_manufacturer.py::test_manufacturer_detail", True),
    ("tests/test_manufacturer.py::test_manufacturer_create", True),
    ("tests/test_manufacturer.py::test_manufacturer_delete", True),
    ("tests/test_manufacturer.py::test_manufacturer_update", True),
]

percent = 0
step = 100 // len(tests)

for name, ok in tests:
    slow()
    percent += step
    if ok:
        print(f"{name} {GREEN}PASSED{RESET}                                 [{percent}%]")
    else:
        print(f"{name} {RED}FAILED{RESET}                                 [{percent}%]")

print(f"""
=================================== FAILURES ===================================
___________________________ test_search_query ____________________________

client = <FlaskClient <Flask '__main__'>>

    def test_search_query(client):
        r = client.get('/index?search=beatles')
>       assert r.status_code == 200
E       assert 500 == 200
E        +  where 500 = <Response streamed [500 INTERNAL SERVER ERROR]>.status_code

tests/test_index.py:10: AssertionError
------------------------------ Captured log ------------------------------------
ERROR    app.routes:routes.py:144 Ошибка в обработчике /index: AttributeError: 'NoneType' object has no attribute 'filter'
""")

print(f"{YELLOW}=============================== warnings summary ==============================={RESET}")
print("tests/test_routes.py:45")
print(f"  {YELLOW}DeprecationWarning:{RESET} 'werkzeug.urls' is deprecated, use 'urllib.parse'\n")

print("=========================== short test summary info ============================")
print(f"{RED}FAILED{RESET} tests/test_index.py::test_search_query - assert 500 == 200")
print("13 passed, 1 failed, 1 warning in 0.73s\n")

print("Process exited with code 1")
