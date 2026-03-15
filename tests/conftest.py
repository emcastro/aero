import geodata_dump


def pytest_sessionfinish():
    geodata_dump.flush()
