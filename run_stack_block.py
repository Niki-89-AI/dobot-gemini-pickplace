import subprocess
import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: python run_stack_block.py <source_label> <target_label>")
        print("Example: python run_stack_block.py blue1 red1")
        return

    source_label, target_label = sys.argv[1], sys.argv[2]
    prompt = (
        f"Pick {source_label} and place it on top of {target_label}. "
        "If the scene is unknown, capture it first and then perform the task."
    )
    subprocess.run([sys.executable, "LLM_ROBOT.py", prompt], check=False)


if __name__ == "__main__":
    main()
