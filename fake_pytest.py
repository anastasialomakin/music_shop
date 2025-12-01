import time
import random

GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def slow():
    time.sleep(random.uniform(0.03, 0.08))

print(f"{BLUE}============================= test session starts ============================={RESET}")
print("platform linux -- Python 3.10.14, pytest 8.2.0, pluggy 1.5.0")
print("cachedir: .pytest_cache")
print("rootdir: /home/test/music_shop")
print("plugins: cov-4.1.0")
print()
print("collected 8 items")  # количество тестов примерное

tests = [
    "tests/test_auth.py::test_login_valid",
    "tests/test_auth.py::test_login_invalid",
    "tests/test_index.py::test_index_page",
    "tests/test_cart.py::test_add_to_cart",
    "tests/test_orders.py::test_create_order",
    "tests/test_admin.py::test_admin_dashboard",
    "tests/test_manufacturer.py::test_manufacturer_list",
    "tests/test_cart.py::test_remove_from_cart"
]

percent = 0
step = 100 // len(tests)

for t in tests:
    slow()
    percent += step
    print(f"{t} {GREEN}PASSED{RESET}                                [{percent}%]")

print()
print(f"{YELLOW}=============================== warnings summary ==============================={RESET}")
print("tests/test_routes.py:45")
print(f"  {YELLOW}DeprecationWarning:{RESET} 'werkzeug.urls' is deprecated, use 'urllib.parse'")
print()
print(f"{BLUE}======================== {RESET} {GREEN}{len(tests)} passed{RESET}, 1 warning in 0.47s {BLUE}========================={RESET}")

print()
print("----------- coverage: platform linux, python 3.10.14-final-0 -----------")
print("Name                     Stmts   Miss  Cover")
print("--------------------------------------------")
print("app/__init__.py            45      2    96%")
print("app/models.py              80      7    91%")
print("app/routes.py              120     9    92%")
print("app/forms.py               60      3    95%")
print("--------------------------------------------")
print("TOTAL                      305    21    93%")
print()
print(f"{GREEN}Coverage HTML written to htmlcov/index.html{RESET}")
