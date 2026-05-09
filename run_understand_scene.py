import subprocess
import sys


def main():
    prompt = "Understand the scene. Home the robot if needed, capture the scene, and summarize all detected blocks clearly."
    subprocess.run([sys.executable, "LLM_ROBOT.py", prompt], check=False)


if __name__ == "__main__":
    main()
