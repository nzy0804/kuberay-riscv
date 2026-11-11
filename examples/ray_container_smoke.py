import sys,time,json,requests,ray,traceback
from pathlib import Path
assert sys.prefix=="/opt/ray-venv",sys.prefix
try:
 ray.init(address="auto")
 session=requests.Session();session.trust_env=False
 for port,path in [(8265,"/api/gcs_healthz"),(52365,"/api/local_raylet_healthz")]:
  deadline=time.monotonic()+60
  while True:
   try:
    response=session.get("http://127.0.0.1:"+str(port)+path,timeout=5)
    response.raise_for_status();assert "success" in response.text.lower(),response.text
    print("PASS health",port,response.text,flush=True);break
   except Exception:
    if time.monotonic()>deadline:raise
    time.sleep(1)
 @ray.remote(num_cpus=1,max_retries=0)
 def square(x):return x*x
 assert ray.get(square.remote(3),timeout=60)==9
 print("RAY_CONTAINER_SMOKE_PASS",flush=True)
except BaseException:
 for name in ("dashboard_agent.log","dashboard_agent.err","dashboard.err","raylet.err"):
  p=Path("/tmp/ray/session_latest/logs")/name
  if p.exists():print("RAY_LOG",name,p.read_text(errors="replace")[-3000:],flush=True)
 raise
finally:
 ray.shutdown()

