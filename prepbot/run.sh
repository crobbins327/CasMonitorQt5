source activate py36

(trap 'kill 0' SIGINT; crossbar start & cd web && ./run.sh & python controller.py)
