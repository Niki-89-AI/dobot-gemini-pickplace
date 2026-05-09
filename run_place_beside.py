import subprocess
import sys


def main():
    if len(sys.argv) != 4:
        print("Usage: python run_place_beside.py <source_label> <target_label> <direction>")
        print("Example: python run_place_beside.py blue1 red1 right")
        print("Directions: front, back, left, right")
        return

    source_label, target_label, direction = sys.argv[1], sys.argv[2], sys.argv[3]
    prompt = (
        f"Pick {source_label} and place it beside {target_label} on the {direction}. "
        "If the scene is unknown, capture it first and then perform the task."
    )
    subprocess.run([sys.executable, "LLM_ROBOT.py", prompt], check=False)


if __name__ == "__main__":
    main()
