import geodata_dump


def pytest_sessionfinish(_session, _exitstatus):
    geodata_dump.flush()
