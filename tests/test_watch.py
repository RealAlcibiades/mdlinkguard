from mdlinkguard.watch import watch


def test_watch_reruns_on_change(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("# A\n")
    runs = []
    step = {"n": 0}
    def sleep(_):
        step["n"] += 1
        if step["n"] == 2:
            (tmp_path / "b.md").write_text("new\n")
    watch([tmp_path], [], lambda: runs.append(1), max_cycles=3, sleep=sleep)
    assert len(runs) == 2  # initial run + one change
