import os
import subprocess
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# Determine which job to run based on an environment variable
job_type = os.getenv("JOB_TYPE", "default")

if job_type == "hyatt":
    subprocess.run(["python", "backend/server/threaded_search_awards.py"])
elif job_type == "hilton":
    subprocess.run(["python", "backend/server/hilton_parallel_search.py"])
elif job_type == "ihg":
    subprocess.run(["python", "backend/server/ihg_parallel_search.py"])
else:
    subprocess.run(["python", "backend/server/threaded_search_awards.py"])