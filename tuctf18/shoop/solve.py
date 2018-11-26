import angr

p = angr.Project('./shoop', auto_load_libs=False)
state = p.factory.entry_state()
sm = p.factory.simulation_manager(state)

sm.explore(find=lambda s: b'That\'s right!' in s.posix.dumps(1),
    avoid=lambda s: b'Close' in s.posix.dumps(1))

print(sm.found[0].posix.dumps(0))
