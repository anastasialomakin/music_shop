#!/usr/bin/env python3
import time
import random
import sys

GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"

def slow():
    time.sleep(random.uniform(0.02, 0.06))

# Header
print(f"{BLUE}============================= test session starts =============================={RESET}")
print("platform linux -- Python 3.10.14, pytest 8.2.0, pluggy 1.5.0")
print("cachedir: .pytest_cache")
print("rootdir: /opt/buildagent/work/67f7970d877724f0")
print("plugins: cov-4.1.0\n")
sys.stdout.flush()

# Tests list (from your tests/ folder)
tests = [
    ("tests/test_auth.py::test_login_valid", True),
    ("tests/test_auth.py::test_login_invalid", True),
    ("tests/test_index.py::test_index_page_loads", True),
    ("tests/test_index.py::test_search_query", False),   # <-- падает
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

print(f"collected {len(tests)} items\n")
sys.stdout.flush()

percent = 0
step = 100 // len(tests)

for name, ok in tests:
    slow()
    percent += step
    if ok:
        print(f"{name} {GREEN}PASSED{RESET}                                 [{percent}%]")
    else:
        print(f"{name} {RED}FAILED{RESET}                                 [{percent}%]")
    sys.stdout.flush()

# Detailed failure block (realistic traceback-like text)
print(f"\n=================================== FAILURES ===================================")
print("___________________________ test_search_query ____________________________\n")
print("client = <FlaskClient <Flask '__main__'>>\n")
print("    def test_search_query(client):")
print("        r = client.get('/index?search=beatles')")
print(">", "       assert r.status_code == 200")
print("E       assert 500 == 200")
print("E        +  where 500 = <Response streamed [500 INTERNAL SERVER ERROR]>.status_code\n")
print("tests/test_index.py:10: AssertionError")
print("------------------------------ Captured log ------------------------------------")
print("ERROR    app.routes:routes.py:144 Ошибка в обработчике /index: AttributeError: 'NoneType' object has no attribute 'filter'")
sys.stdout.flush()

# Warnings summary
print(f"\n{YELLOW}=============================== warnings summary ==============================={RESET}")
print("tests/test_routes.py:45")
print(f"  {YELLOW}DeprecationWarning:{RESET} 'werkzeug.urls' is deprecated, use 'urllib.parse'")
sys.stdout.flush()

# Short summary
print(f"\n=========================== short test summary info ============================")
print(f"{RED}FAILED{RESET} tests/test_index.py::test_search_query - assert 500 == 200")
print(f"{len([t for t in tests if t[1]])} passed, 1 failed, 1 warning in 0.73s")
sys.stdout.flush()

# Coverage block
print("\n----------- coverage: platform linux, python 3.10.14-final-0 -----------")
print("Name                     Stmts   Miss  Cover")
print("--------------------------------------------")
print("app/__init__.py            45      2    96%")
print("app/models.py              80      7    91%")
print("app/routes.py              120    14    88%")
print("app/forms.py               60      3    95%")
print("--------------------------------------------")
print("TOTAL                      305    26    91%\n")
print("Coverage HTML written to htmlcov/index.html\n")
sys.stdout.flush()

# Exit non-zero so CI/build fails
sys.exit(1)
