from __future__ import annotations

from breaklab.cli import attack_target


def demo() -> None:
    result = attack_target(
        "python://breaklab.example_local_target:safe_echo_target",
        judge_enabled=False,
    )
    print(result["summary"])
    for item in result["cases"][:3]:
        print(item["case"], item["passed"], item["rule"])


if __name__ == "__main__":
    demo()
