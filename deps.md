Your `pip install -r requirements.txt` is slow because it is pulling **PyTorch 2.7.1 plus sixteen separate NVIDIA CUDA 12.6 wheels** (cuBLAS, cuDNN, NCCL, etc.). The combined payload is well over **2 GB** – at 1 ‑ 2 MB /s that is 20‑40 minutes on every rebuild. The good news is that you can cut this to a single 780 MB wheel and finish in a few minutes, with no loss of GPU functionality.

---

## 1  Why the download is so large

* From PyTorch 2.7 the project switched to a **split‑package model**: `torch‑2.7.*` no longer bundles the CUDA libraries; you must install the extra `nvidia‑*‑cu12` wheels yourself. ([PyTorch][1])
* Your requirements file asks for `torch>=1.11.0`, so pip selects the newest 2.7.1 build and then resolves every `nvidia‑*.whl` listed as hard pins. Example sizes: cuBLAS 393 MB, cuDNN 571 MB. ([PyPI][2])
* The `externally‑managed‑environment` error you saw earlier comes from **PEP 668**; it disappears once you stay inside a proper virtual environment. ([Python Packaging][3])

---

## 2  Quickest fix – use the integrated wheel

1. Open `backend/requirements.txt`.
2. Replace the Torch block **and delete every `nvidia‑*` line**:

```diff
- torch>=1.11.0
- nvidia-cublas-cu12==12.6.4.1
- nvidia-cudnn-cu12==9.5.1.17
- nvidia-cusolver-cu12==11.7.1.2
- ... (remove the rest of the nvidia‑* pins)
+ torch==2.5.1+cu121
+ torchvision==0.20.1+cu121
+ torchaudio==2.5.1+cu121
```

3. Install with the extra index, still inside your activated `.venv`:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt \
  --extra-index-url https://download.pytorch.org/whl/cu121 \
  --no-cache-dir
```

* `torch‑2.5.1+cu121` already contains cuBLAS, cuDNN, NCCL, and friends – no extra wheels needed.
* Total download: about **790 MB** in one file, plus 120 MB for torchvision and torchaudio.

---

## 3  If you really need PyTorch 2.7

Keep the split model but avoid pulling it every time:

```bash
mkdir -p ~/wheelhouse
pip download torch==2.7.1+cu126 \
  torchvision==0.22.0+cu126 \
  torchaudio==2.7.1+cu126 \
  --extra-index-url https://download.pytorch.org/whl/cu126 \
  --dest ~/wheelhouse

# later, for offline or repeated installs:
pip install --no-index --find-links ~/wheelhouse \
  torch==2.7.1+cu126 torchvision==0.22.0+cu126 torchaudio==2.7.1+cu126
```

Download once, cache locally, install in seconds.

---

## 4  When bandwidth is critical

| Scenario                                 | Recommendation                                                        |
| ---------------------------------------- | --------------------------------------------------------------------- |
| Just need the code to run for unit tests | Use CPU wheels – `torch==2.5.1+cpu` etc. (65 MB total).               |
| Limited disk                             | Keep the integrated 2.5 wheel; delete `~/.cache/pip` after install.   |
| Slow connection but GPU required         | Pre‑download on a faster network (above), then copy via USB or rsync. |

---

### Summary

* The long wait is caused by the new split CUDA packaging in Torch 2.7.
* Switch to `torch==2.5.1+cu121` (integrated wheel) or pre‑download the 2.7 wheel set once.
* Remove all `nvidia‑*` pins unless you are deliberately using the split model.
* Always install inside a virtual environment to avoid PEP 668 blocks.

Apply the change, rerun `pip install`, and you should be up and running in a fraction of the time.

[1]: https://pytorch.org/blog/pytorch-2-7/?utm_source=chatgpt.com "PyTorch 2.7 Release"
[2]: https://pypi.org/project/nvidia-cublas-cu12/?utm_source=chatgpt.com "nvidia-cublas-cu12 - PyPI"
[3]: https://packaging.python.org/en/latest/specifications/externally-managed-environments/?utm_source=chatgpt.com "Externally Managed Environments - Python Packaging User Guide"

PS C:\WINDOWS\system32> cd D:\multiagentwriterz\backend
PS D:\multiagentwriterz\backend> # make the new one
PS D:\multiagentwriterz\backend> py -3.12 -m venv .venv
PS D:\multiagentwriterz\backend> . .\.venv\Scripts\Activate.ps1
(.venv) PS D:\multiagentwriterz\backend> python -V          # should show 3.12.x  ?
Python 3.12.3
(.venv) PS D:\multiagentwriterz\backend> $wheelhouse = "$HOME\wheelhouse"
(.venv) PS D:\multiagentwriterz\backend> pip install --no-index --find-links $wheelhouse -r .\requirements.txt
Looking in links: c:\Users\USER\wheelhouse
Processing c:\users\user\wheelhouse\langchain-0.3.26-py3-none-any.whl (from -r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\langgraph-0.5.4-py3-none-any.whl (from -r .\requirements.txt (line 3))
Processing c:\users\user\wheelhouse\langchain_google_genai-2.1.8-py3-none-any.whl (from -r .\requirements.txt (line 4))
Processing c:\users\user\wheelhouse\langgraph_sdk-0.1.74-py3-none-any.whl (from -r .\requirements.txt (line 5))
Processing c:\users\user\wheelhouse\langgraph_api-0.2.98-py3-none-any.whl (from -r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\fastapi-0.116.1-py3-none-any.whl (from -r .\requirements.txt (line 10))
Processing c:\users\user\wheelhouse\websockets-15.0.1-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 12))
Processing c:\users\user\wheelhouse\python_multipart-0.0.20-py3-none-any.whl (from -r .\requirements.txt (line 13))
Processing c:\users\user\wheelhouse\starlette_compress-1.6.1-py3-none-any.whl (from -r .\requirements.txt (line 14))
Processing c:\users\user\wheelhouse\google_genai-1.26.0-py3-none-any.whl (from -r .\requirements.txt (line 17))
Processing c:\users\user\wheelhouse\anthropic-0.58.2-py3-none-any.whl (from -r .\requirements.txt (line 18))
Processing c:\users\user\wheelhouse\openai-1.97.0-py3-none-any.whl (from -r .\requirements.txt (line 19))
Processing c:\users\user\wheelhouse\langchain_openai-0.3.28-py3-none-any.whl (from -r .\requirements.txt (line 20))
Processing c:\users\user\wheelhouse\langchain_groq-0.3.6-py3-none-any.whl (from -r .\requirements.txt (line 21))
Processing c:\users\user\wheelhouse\google_cloud_aiplatform-1.104.0-py2.py3-none-any.whl (from -r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\sqlalchemy-2.0.41-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 25))
Processing c:\users\user\wheelhouse\alembic-1.16.4-py3-none-any.whl (from -r .\requirements.txt (line 26))
Processing c:\users\user\wheelhouse\asyncpg-0.30.0-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 27))
Processing c:\users\user\wheelhouse\psycopg2_binary-2.9.10-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 28))
Processing c:\users\user\wheelhouse\supabase-2.17.0-py3-none-any.whl (from -r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\chromadb-1.0.15-cp39-abi3-win_amd64.whl (from -r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\redis-5.2.1-py3-none-any.whl (from -r .\requirements.txt (line 33))
Processing c:\users\user\wheelhouse\aioredis-2.0.1-py3-none-any.whl (from -r .\requirements.txt (line 34))
Processing c:\users\user\wheelhouse\python_dotenv-1.1.1-py3-none-any.whl (from -r .\requirements.txt (line 37))
Processing c:\users\user\wheelhouse\pydantic-2.11.7-py3-none-any.whl (from -r .\requirements.txt (line 38))
Processing c:\users\user\wheelhouse\aiohttp-3.12.14-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\pyjwt-2.10.1-py3-none-any.whl (from -r .\requirements.txt (line 42))
Processing c:\users\user\wheelhouse\agentic_doc-0.3.1-py3-none-any.whl (from -r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\pypdf2-3.0.1-py3-none-any.whl (from -r .\requirements.txt (line 46))
Processing c:\users\user\wheelhouse\docx2txt-0.9-py3-none-any.whl (from -r .\requirements.txt (line 47))
Processing c:\users\user\wheelhouse\python_docx-1.2.0-py3-none-any.whl (from -r .\requirements.txt (line 48))
Processing c:\users\user\wheelhouse\openpyxl-3.1.5-py2.py3-none-any.whl (from -r .\requirements.txt (line 49))
Processing c:\users\user\wheelhouse\pillow-11.3.0-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 50))
Processing c:\users\user\wheelhouse\fpdf-1.7.2.tar.gz (from -r .\requirements.txt (line 51))
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Processing c:\users\user\wheelhouse\pytrends-4.9.2-py3-none-any.whl (from -r .\requirements.txt (line 54))
Processing c:\users\user\wheelhouse\arxiv-2.2.0-py3-none-any.whl (from -r .\requirements.txt (line 55))
Processing c:\users\user\wheelhouse\beautifulsoup4-4.13.4-py3-none-any.whl (from -r .\requirements.txt (line 56))
Processing c:\users\user\wheelhouse\requests-2.32.4-py3-none-any.whl (from -r .\requirements.txt (line 57))
Processing c:\users\user\wheelhouse\feedparser-6.0.11-py3-none-any.whl (from -r .\requirements.txt (line 58))
Processing c:\users\user\wheelhouse\celery-5.5.3-py3-none-any.whl (from -r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\boto3-1.39.10-py3-none-any.whl (from -r .\requirements.txt (line 65))
Processing c:\users\user\wheelhouse\azure_storage_blob-12.26.0-py3-none-any.whl (from -r .\requirements.txt (line 66))
Processing c:\users\user\wheelhouse\prometheus_client-0.22.1-py3-none-any.whl (from -r .\requirements.txt (line 69))
Processing c:\users\user\wheelhouse\structlog-25.4.0-py3-none-any.whl (from -r .\requirements.txt (line 70))
Processing c:\users\user\wheelhouse\opentelemetry_api-1.35.0-py3-none-any.whl (from -r .\requirements.txt (line 71))
Processing c:\users\user\wheelhouse\opentelemetry_sdk-1.35.0-py3-none-any.whl (from -r .\requirements.txt (line 72))
Processing c:\users\user\wheelhouse\cryptography-44.0.3-cp39-abi3-win_amd64.whl (from -r .\requirements.txt (line 75))
Processing c:\users\user\wheelhouse\bcrypt-4.3.0-cp39-abi3-win_amd64.whl (from -r .\requirements.txt (line 76))
Processing c:\users\user\wheelhouse\mypy-1.17.0-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 79))
Processing c:\users\user\wheelhouse\ruff-0.12.4-py3-none-win_amd64.whl (from -r .\requirements.txt (line 80))
Processing c:\users\user\wheelhouse\pytest-8.4.1-py3-none-any.whl (from -r .\requirements.txt (line 81))
Processing c:\users\user\wheelhouse\pytest_asyncio-1.1.0-py3-none-any.whl (from -r .\requirements.txt (line 82))
Processing c:\users\user\wheelhouse\httpx-0.28.1-py3-none-any.whl (from -r .\requirements.txt (line 83))
Processing c:\users\user\wheelhouse\torch-2.5.1+cu121-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\torchvision-0.20.1+cu121-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 88))
Processing c:\users\user\wheelhouse\torchaudio-2.5.1+cu121-cp312-cp312-win_amd64.whl (from -r .\requirements.txt (line 89))
Processing c:\users\user\wheelhouse\sentence_transformers-5.0.0-py3-none-any.whl (from -r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\langgraph_cli-0.3.5-py3-none-any.whl (from -r .\requirements.txt (line 6))
Processing c:\users\user\wheelhouse\uvicorn-0.35.0-py3-none-any.whl (from -r .\requirements.txt (line 11))
Processing c:\users\user\wheelhouse\python_jose-3.5.0-py2.py3-none-any.whl (from -r .\requirements.txt (line 40))
Processing c:\users\user\wheelhouse\passlib-1.7.4-py2.py3-none-any.whl (from -r .\requirements.txt (line 41))
Processing c:\users\user\wheelhouse\filelock-3.18.0-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\typing_extensions-4.14.1-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\networkx-3.5-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\jinja2-3.1.6-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\fsspec-2025.7.0-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\setuptools-80.9.0-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\sympy-1.13.1-py3-none-any.whl (from torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\numpy-2.2.6-cp312-cp312-win_amd64.whl (from torchvision==0.20.1+cu121->-r .\requirements.txt (line 88))
Processing c:\users\user\wheelhouse\mpmath-1.3.0-py3-none-any.whl (from sympy==1.13.1->torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\langchain_core-0.3.70-py3-none-any.whl (from langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\langchain_text_splitters-0.3.8-py3-none-any.whl (from langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\langsmith-0.4.8-py3-none-any.whl (from langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\pyyaml-6.0.2-cp312-cp312-win_amd64.whl (from langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\langgraph_checkpoint-2.1.1-py3-none-any.whl (from langgraph->-r .\requirements.txt (line 3))
Processing c:\users\user\wheelhouse\langgraph_prebuilt-0.5.2-py3-none-any.whl (from langgraph->-r .\requirements.txt (line 3))
Processing c:\users\user\wheelhouse\xxhash-3.5.0-cp312-cp312-win_amd64.whl (from langgraph->-r .\requirements.txt (line 3))
Processing c:\users\user\wheelhouse\filetype-1.2.0-py2.py3-none-any.whl (from langchain-google-genai->-r .\requirements.txt (line 4))
Processing c:\users\user\wheelhouse\google_ai_generativelanguage-0.6.18-py3-none-any.whl (from langchain-google-genai->-r .\requirements.txt (line 4))
Processing c:\users\user\wheelhouse\orjson-3.11.0-cp312-cp312-win_amd64.whl (from langgraph-sdk->-r .\requirements.txt (line 5))
Processing c:\users\user\wheelhouse\click-8.2.1-py3-none-any.whl (from langgraph-cli[inmem]->-r .\requirements.txt (line 6))
Processing c:\users\user\wheelhouse\langgraph_runtime_inmem-0.6.0-py3-none-any.whl (from langgraph-cli[inmem]->-r .\requirements.txt (line 6))
Processing c:\users\user\wheelhouse\cloudpickle-3.1.1-py3-none-any.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\jsonschema_rs-0.29.1-cp312-cp312-win_amd64.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\sse_starlette-2.1.3-py3-none-any.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\starlette-0.47.2-py3-none-any.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\tenacity-8.5.0-py3-none-any.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\truststore-0.10.1-py3-none-any.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\watchfiles-1.1.0-cp312-cp312-win_amd64.whl (from langgraph-api->-r .\requirements.txt (line 7))
Processing c:\users\user\wheelhouse\h11-0.16.0-py3-none-any.whl (from uvicorn[standard]->-r .\requirements.txt (line 11))
Processing c:\users\user\wheelhouse\colorama-0.4.6-py2.py3-none-any.whl (from uvicorn[standard]->-r .\requirements.txt (line 11))
Processing c:\users\user\wheelhouse\httptools-0.6.4-cp312-cp312-win_amd64.whl (from uvicorn[standard]->-r .\requirements.txt (line 11))
Processing c:\users\user\wheelhouse\brotli-1.1.0-cp312-cp312-win_amd64.whl (from starlette-compress->-r .\requirements.txt (line 14))
Processing c:\users\user\wheelhouse\zstandard-0.23.0-cp312-cp312-win_amd64.whl (from starlette-compress->-r .\requirements.txt (line 14))
Processing c:\users\user\wheelhouse\anyio-4.9.0-py3-none-any.whl (from google-genai->-r .\requirements.txt (line 17))
Processing c:\users\user\wheelhouse\google_auth-2.40.3-py2.py3-none-any.whl (from google-genai->-r .\requirements.txt (line 17))
Processing c:\users\user\wheelhouse\distro-1.9.0-py3-none-any.whl (from anthropic->-r .\requirements.txt (line 18))
Processing c:\users\user\wheelhouse\jiter-0.10.0-cp312-cp312-win_amd64.whl (from anthropic->-r .\requirements.txt (line 18))
Processing c:\users\user\wheelhouse\sniffio-1.3.1-py3-none-any.whl (from anthropic->-r .\requirements.txt (line 18))
Processing c:\users\user\wheelhouse\tqdm-4.67.1-py3-none-any.whl (from openai->-r .\requirements.txt (line 19))
Processing c:\users\user\wheelhouse\tiktoken-0.9.0-cp312-cp312-win_amd64.whl (from langchain-openai->-r .\requirements.txt (line 20))
Processing c:\users\user\wheelhouse\groq-0.30.0-py3-none-any.whl (from langchain-groq->-r .\requirements.txt (line 21))
Processing c:\users\user\wheelhouse\google_api_core-2.25.1-py3-none-any.whl (from google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,<3.0.0,>=1.34.1->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\proto_plus-1.26.1-py3-none-any.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\protobuf-6.31.1-cp310-abi3-win_amd64.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\packaging-25.0-py3-none-any.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\google_cloud_storage-2.19.0-py2.py3-none-any.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\google_cloud_bigquery-3.35.0-py3-none-any.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\google_cloud_resource_manager-1.14.2-py3-none-any.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\shapely-2.1.1-cp312-cp312-win_amd64.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\docstring_parser-0.17.0-py3-none-any.whl (from google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\greenlet-3.2.3-cp312-cp312-win_amd64.whl (from sqlalchemy->-r .\requirements.txt (line 25))
Processing c:\users\user\wheelhouse\mako-1.3.10-py3-none-any.whl (from alembic->-r .\requirements.txt (line 26))
Processing c:\users\user\wheelhouse\gotrue-2.12.3-py3-none-any.whl (from supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\postgrest-1.1.1-py3-none-any.whl (from supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\realtime-2.6.0-py3-none-any.whl (from supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\storage3-0.12.0-py3-none-any.whl (from supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\supafunc-0.10.1-py3-none-any.whl (from supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\deprecation-2.1.0-py2.py3-none-any.whl (from postgrest==1.1.1->supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\python_dateutil-2.9.0.post0-py2.py3-none-any.whl (from storage3==0.12.0->supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\strenum-0.4.15-py3-none-any.whl (from supafunc==0.10.1->supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\build-1.2.2.post1-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\pybase64-1.4.1-cp312-cp312-win_amd64.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\posthog-5.4.0-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\onnxruntime-1.22.1-cp312-cp312-win_amd64.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\opentelemetry_exporter_otlp_proto_grpc-1.35.0-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\tokenizers-0.21.2-cp39-abi3-win_amd64.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\pypika-0.48.9.tar.gz (from chromadb->-r .\requirements.txt (line 30))
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Processing c:\users\user\wheelhouse\overrides-7.7.0-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\importlib_resources-6.5.2-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\grpcio-1.73.1-cp312-cp312-win_amd64.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\typer-0.16.0-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\kubernetes-33.1.0-py2.py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\mmh3-5.1.0-cp312-cp312-win_amd64.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\rich-14.0.0-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\jsonschema-4.25.0-py3-none-any.whl (from chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\async_timeout-5.0.1-py3-none-any.whl (from aioredis->-r .\requirements.txt (line 34))
Processing c:\users\user\wheelhouse\annotated_types-0.7.0-py3-none-any.whl (from pydantic->-r .\requirements.txt (line 38))
Processing c:\users\user\wheelhouse\pydantic_core-2.33.2-cp312-cp312-win_amd64.whl (from pydantic->-r .\requirements.txt (line 38))
Processing c:\users\user\wheelhouse\typing_inspection-0.4.1-py3-none-any.whl (from pydantic->-r .\requirements.txt (line 38))
Processing c:\users\user\wheelhouse\aiohappyeyeballs-2.6.1-py3-none-any.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\aiosignal-1.4.0-py3-none-any.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\attrs-25.3.0-py3-none-any.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\frozenlist-1.7.0-cp312-cp312-win_amd64.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\multidict-6.6.3-cp312-cp312-win_amd64.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\propcache-0.3.2-cp312-cp312-win_amd64.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\yarl-1.20.1-cp312-cp312-win_amd64.whl (from aiohttp->-r .\requirements.txt (line 39))
Processing c:\users\user\wheelhouse\ecdsa-0.19.1-py2.py3-none-any.whl (from python-jose[cryptography]->-r .\requirements.txt (line 40))
Processing c:\users\user\wheelhouse\rsa-4.9.1-py3-none-any.whl (from python-jose[cryptography]->-r .\requirements.txt (line 40))
Processing c:\users\user\wheelhouse\pyasn1-0.6.1-py3-none-any.whl (from python-jose[cryptography]->-r .\requirements.txt (line 40))
Processing c:\users\user\wheelhouse\google_api_python_client-2.176.0-py3-none-any.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\google_auth_oauthlib-1.2.2-py3-none-any.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\opencv_python_headless-4.12.0.88-cp37-abi3-win_amd64.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\pillow_heif-1.0.0-cp312-cp312-win_amd64.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\pydantic_settings-2.10.1-py3-none-any.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\pymupdf-1.26.3-cp39-abi3-win_amd64.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\pypdf-5.8.0-py3-none-any.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\types_jsonschema-4.25.0.20250720-py3-none-any.whl (from agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\lxml-6.0.0-cp312-cp312-win_amd64.whl (from python-docx->-r .\requirements.txt (line 48))
Processing c:\users\user\wheelhouse\et_xmlfile-2.0.0-py3-none-any.whl (from openpyxl->-r .\requirements.txt (line 49))
Processing c:\users\user\wheelhouse\pandas-2.3.1-cp312-cp312-win_amd64.whl (from pytrends->-r .\requirements.txt (line 54))
Processing c:\users\user\wheelhouse\soupsieve-2.7-py3-none-any.whl (from beautifulsoup4->-r .\requirements.txt (line 56))
Processing c:\users\user\wheelhouse\charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl (from requests->-r .\requirements.txt (line 57))
Processing c:\users\user\wheelhouse\idna-3.10-py3-none-any.whl (from requests->-r .\requirements.txt (line 57))
Processing c:\users\user\wheelhouse\urllib3-2.5.0-py3-none-any.whl (from requests->-r .\requirements.txt (line 57))
Processing c:\users\user\wheelhouse\certifi-2025.7.14-py3-none-any.whl (from requests->-r .\requirements.txt (line 57))
Processing c:\users\user\wheelhouse\sgmllib3k-1.0.0.tar.gz (from feedparser->-r .\requirements.txt (line 58))
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Processing c:\users\user\wheelhouse\billiard-4.2.1-py3-none-any.whl (from celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\kombu-5.5.4-py3-none-any.whl (from celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\vine-5.1.0-py3-none-any.whl (from celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\click_didyoumean-0.3.1-py3-none-any.whl (from celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\click_repl-0.3.0-py3-none-any.whl (from celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\click_plugins-1.1.1.2-py2.py3-none-any.whl (from celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\botocore-1.39.10-py3-none-any.whl (from boto3->-r .\requirements.txt (line 65))
Processing c:\users\user\wheelhouse\jmespath-1.0.1-py3-none-any.whl (from boto3->-r .\requirements.txt (line 65))
Processing c:\users\user\wheelhouse\s3transfer-0.13.1-py3-none-any.whl (from boto3->-r .\requirements.txt (line 65))
Processing c:\users\user\wheelhouse\azure_core-1.35.0-py3-none-any.whl (from azure-storage-blob->-r .\requirements.txt (line 66))
Processing c:\users\user\wheelhouse\isodate-0.7.2-py3-none-any.whl (from azure-storage-blob->-r .\requirements.txt (line 66))
Processing c:\users\user\wheelhouse\importlib_metadata-8.7.0-py3-none-any.whl (from opentelemetry-api->-r .\requirements.txt (line 71))
Processing c:\users\user\wheelhouse\opentelemetry_semantic_conventions-0.56b0-py3-none-any.whl (from opentelemetry-sdk->-r .\requirements.txt (line 72))
Processing c:\users\user\wheelhouse\cffi-1.17.1-cp312-cp312-win_amd64.whl (from cryptography->-r .\requirements.txt (line 75))
Processing c:\users\user\wheelhouse\mypy_extensions-1.1.0-py3-none-any.whl (from mypy->-r .\requirements.txt (line 79))
Processing c:\users\user\wheelhouse\pathspec-0.12.1-py3-none-any.whl (from mypy->-r .\requirements.txt (line 79))
Processing c:\users\user\wheelhouse\iniconfig-2.1.0-py3-none-any.whl (from pytest->-r .\requirements.txt (line 81))
Processing c:\users\user\wheelhouse\pluggy-1.6.0-py3-none-any.whl (from pytest->-r .\requirements.txt (line 81))
Processing c:\users\user\wheelhouse\pygments-2.19.2-py3-none-any.whl (from pytest->-r .\requirements.txt (line 81))
Processing c:\users\user\wheelhouse\httpcore-1.0.9-py3-none-any.whl (from httpx->-r .\requirements.txt (line 83))
Processing c:\users\user\wheelhouse\transformers-4.53.2-py3-none-any.whl (from sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\scikit_learn-1.7.1-cp312-cp312-win_amd64.whl (from sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\scipy-1.16.0-cp312-cp312-win_amd64.whl (from sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\huggingface_hub-0.33.4-py3-none-any.whl (from sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\six-1.17.0-py2.py3-none-any.whl (from azure-core>=1.30.0->azure-storage-blob->-r .\requirements.txt (line 66))
Processing c:\users\user\wheelhouse\pyproject_hooks-1.2.0-py3-none-any.whl (from build>=1.0.3->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\pycparser-2.22-py3-none-any.whl (from cffi>=1.12->cryptography->-r .\requirements.txt (line 75))
Processing c:\users\user\wheelhouse\prompt_toolkit-3.0.51-py3-none-any.whl (from click-repl>=0.2.0->celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\googleapis_common_protos-1.70.0-py3-none-any.whl (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,<3.0.0,>=1.34.1->google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,<3.0.0,>=1.34.1->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\grpcio_status-1.73.1-py3-none-any.whl (from google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,<3.0.0,>=1.34.1->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\httplib2-0.22.0-py3-none-any.whl (from google-api-python-client<3.0.0,>=2.170.0->agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\google_auth_httplib2-0.2.0-py2.py3-none-any.whl (from google-api-python-client<3.0.0,>=2.170.0->agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\uritemplate-4.2.0-py3-none-any.whl (from google-api-python-client<3.0.0,>=2.170.0->agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\cachetools-5.5.2-py3-none-any.whl (from google-auth<3.0.0,>=2.14.1->google-genai->-r .\requirements.txt (line 17))
Processing c:\users\user\wheelhouse\pyasn1_modules-0.4.2-py3-none-any.whl (from google-auth<3.0.0,>=2.14.1->google-genai->-r .\requirements.txt (line 17))
Processing c:\users\user\wheelhouse\requests_oauthlib-2.0.0-py2.py3-none-any.whl (from google-auth-oauthlib<2.0.0,>=1.2.2->agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\google_cloud_core-2.4.3-py2.py3-none-any.whl (from google-cloud-bigquery!=3.20.0,<4.0.0,>=1.15.0->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\google_resumable_media-2.7.2-py2.py3-none-any.whl (from google-cloud-bigquery!=3.20.0,<4.0.0,>=1.15.0->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\grpc_google_iam_v1-0.14.2-py3-none-any.whl (from google-cloud-resource-manager<3.0.0,>=1.3.3->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\google_crc32c-1.7.1-cp312-cp312-win_amd64.whl (from google-cloud-storage<3.0.0,>=1.32.0->google-cloud-aiplatform->-r .\requirements.txt (line 22))
Processing c:\users\user\wheelhouse\zipp-3.23.0-py3-none-any.whl (from importlib-metadata<8.8.0,>=6.0->opentelemetry-api->-r .\requirements.txt (line 71))
Processing c:\users\user\wheelhouse\jsonschema_specifications-2025.4.1-py3-none-any.whl (from jsonschema>=4.19.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\referencing-0.36.2-py3-none-any.whl (from jsonschema>=4.19.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\rpds_py-0.26.0-cp312-cp312-win_amd64.whl (from jsonschema>=4.19.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\amqp-5.3.1-py3-none-any.whl (from kombu<5.6,>=5.5.2->celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\tzdata-2025.2-py2.py3-none-any.whl (from kombu<5.6,>=5.5.2->celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\websocket_client-1.8.0-py3-none-any.whl (from kubernetes>=28.1.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\oauthlib-3.3.1-py3-none-any.whl (from kubernetes>=28.1.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\durationpy-0.10-py3-none-any.whl (from kubernetes>=28.1.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\jsonpatch-1.33-py2.py3-none-any.whl (from langchain-core<1.0.0,>=0.3.66->langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\ormsgpack-1.10.0-cp312-cp312-win_amd64.whl (from langgraph-checkpoint<3.0.0,>=2.1.0->langgraph->-r .\requirements.txt (line 3))
Processing c:\users\user\wheelhouse\blockbuster-1.5.25-py3-none-any.whl (from langgraph-runtime-inmem>=0.6.0->langgraph-cli[inmem]->-r .\requirements.txt (line 6))
Processing c:\users\user\wheelhouse\requests_toolbelt-1.0.0-py2.py3-none-any.whl (from langsmith>=0.1.17->langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\coloredlogs-15.0.1-py2.py3-none-any.whl (from onnxruntime>=1.14.1->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\flatbuffers-25.2.10-py2.py3-none-any.whl (from onnxruntime>=1.14.1->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\opentelemetry_exporter_otlp_proto_common-1.35.0-py3-none-any.whl (from opentelemetry-exporter-otlp-proto-grpc>=1.2.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\opentelemetry_proto-1.35.0-py3-none-any.whl (from opentelemetry-exporter-otlp-proto-grpc>=1.2.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\pytz-2025.2-py2.py3-none-any.whl (from pandas>=0.25->pytrends->-r .\requirements.txt (line 54))
Processing c:\users\user\wheelhouse\backoff-2.2.1-py3-none-any.whl (from posthog<6.0.0,>=2.4.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\markdown_it_py-3.0.0-py3-none-any.whl (from rich>=10.11.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\regex-2024.11.6-cp312-cp312-win_amd64.whl (from tiktoken<1,>=0.7->langchain-openai->-r .\requirements.txt (line 20))
Processing c:\users\user\wheelhouse\safetensors-0.5.3-cp38-abi3-win_amd64.whl (from transformers<5.0.0,>=4.41.0->sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\shellingham-1.5.4-py2.py3-none-any.whl (from typer>=0.9.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\markupsafe-3.0.2-cp312-cp312-win_amd64.whl (from jinja2->torch==2.5.1+cu121->-r .\requirements.txt (line 87))
Processing c:\users\user\wheelhouse\joblib-1.5.1-py3-none-any.whl (from scikit-learn->sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\threadpoolctl-3.6.0-py3-none-any.whl (from scikit-learn->sentence-transformers->-r .\requirements.txt (line 92))
Processing c:\users\user\wheelhouse\forbiddenfruit-0.1.4.tar.gz (from blockbuster<2.0.0,>=1.5.24->langgraph-runtime-inmem>=0.6.0->langgraph-cli[inmem]->-r .\requirements.txt (line 6))
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Processing c:\users\user\wheelhouse\pyparsing-3.2.3-py3-none-any.whl (from httplib2<1.0.0,>=0.19.0->google-api-python-client<3.0.0,>=2.170.0->agentic-doc->-r .\requirements.txt (line 45))
Processing c:\users\user\wheelhouse\h2-4.2.0-py3-none-any.whl (from httpx[http2]<0.29,>=0.26->gotrue==2.12.3->supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\jsonpointer-3.0.0-py2.py3-none-any.whl (from jsonpatch<2.0,>=1.33->langchain-core<1.0.0,>=0.3.66->langchain->-r .\requirements.txt (line 2))
Processing c:\users\user\wheelhouse\mdurl-0.1.2-py3-none-any.whl (from markdown-it-py>=2.2.0->rich>=10.11.0->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\wcwidth-0.2.13-py2.py3-none-any.whl (from prompt-toolkit>=3.0.36->click-repl>=0.2.0->celery->-r .\requirements.txt (line 61))
Processing c:\users\user\wheelhouse\humanfriendly-10.0-py2.py3-none-any.whl (from coloredlogs->onnxruntime>=1.14.1->chromadb->-r .\requirements.txt (line 30))
Processing c:\users\user\wheelhouse\hyperframe-6.1.0-py3-none-any.whl (from h2<5,>=3->httpx[http2]<0.29,>=0.26->gotrue==2.12.3->supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\hpack-4.1.0-py3-none-any.whl (from h2<5,>=3->httpx[http2]<0.29,>=0.26->gotrue==2.12.3->supabase->-r .\requirements.txt (line 29))
Processing c:\users\user\wheelhouse\pyreadline3-3.5.4-py3-none-any.whl (from humanfriendly>=9.1->coloredlogs->onnxruntime>=1.14.1->chromadb->-r .\requirements.txt (line 30))
Building wheels for collected packages: fpdf, pypika, sgmllib3k, forbiddenfruit
  Building wheel for fpdf (pyproject.toml) ... done
  Created wheel for fpdf: filename=fpdf-1.7.2-py2.py3-none-any.whl size=40769 sha256=85435a01545bdf80bd21f3f5b86d525a703abdecc83857707588eb10fee9cfe9
  Stored in directory: c:\users\user\appdata\local\pip\cache\wheels\6a\02\05\6d04d92dba0511e8edb2be7683e87f79bcf88b347e58314ca9
  Building wheel for pypika (pyproject.toml) ... done
  Created wheel for pypika: filename=pypika-0.48.9-py2.py3-none-any.whl size=53916 sha256=b8c65f0760676bdd0dc64b03e717c98d6a87022375296116589d6e6701384543
  Stored in directory: c:\users\user\appdata\local\pip\cache\wheels\9a\cd\09\cd84087b0a4ff7539a8a76ece1ec65ad5fd1705f43c208d70c
  Building wheel for sgmllib3k (pyproject.toml) ... done
  Created wheel for sgmllib3k: filename=sgmllib3k-1.0.0-py3-none-any.whl size=6105 sha256=bf719a16451b727c3704568572ebce64d6745134477e98c655066fc9931e94ac
  Stored in directory: c:\users\user\appdata\local\pip\cache\wheels\6f\87\64\f2392cefdc1fde7cbb82c80f128302e8e16864bed2537ed566
  Building wheel for forbiddenfruit (pyproject.toml) ... done
  Created wheel for forbiddenfruit: filename=forbiddenfruit-0.1.4-py3-none-any.whl size=21929 sha256=3fd077791195a896761f8fa0a2c84ec578d9315d170945f005f0d4cee68f18f4
  Stored in directory: c:\users\user\appdata\local\pip\cache\wheels\10\bb\bd\fac1457d2f96f01beb24901b20726c3836c4304d35aa8d5bae
Successfully built fpdf pypika sgmllib3k forbiddenfruit
Installing collected packages: wcwidth, strenum, sgmllib3k, pytz, pypika, passlib, mpmath, fpdf, forbiddenfruit, flatbuffers, filetype, durationpy, docx2txt, brotli, zstandard, zipp, xxhash, websockets, websocket-client, vine, urllib3, uritemplate, tzdata, typing-extensions, truststore, threadpoolctl, tenacity, sympy, structlog, soupsieve, sniffio, six, shellingham, setuptools, safetensors, ruff, rpds-py, regex, redis, PyYAML, python-multipart, python-dotenv, pyreadline3, pyproject_hooks, PyPDF2, pypdf, pyparsing, pymupdf, PyJWT, pygments, pycparser, pybase64, pyasn1, psycopg2-binary, protobuf, propcache, prompt-toolkit, prometheus-client, pluggy, Pillow, pathspec, packaging, overrides, ormsgpack, orjson, oauthlib, numpy, networkx, mypy_extensions, multidict, mmh3, mdurl, MarkupSafe, lxml, jsonschema-rs, jsonpointer, joblib, jmespath, jiter, isodate, iniconfig, importlib-resources, idna, hyperframe, httptools, hpack, h11, grpcio, greenlet, google-crc32c, fsspec, frozenlist, filelock, feedparser, et-xmlfile, docstring_parser, distro, colorama, cloudpickle, charset_normalizer, certifi, cachetools, blockbuster, billiard, bcrypt, backoff, attrs, asyncpg, async-timeout, annotated-types, aiohappyeyeballs, yarl, typing-inspection, tqdm, sqlalchemy, shapely, scipy, rsa, requests, referencing, python-docx, python-dateutil, pytest, pydantic-core, pyasn1-modules, proto-plus, pillow-heif, opentelemetry-proto, openpyxl, opencv-python-headless, mypy, markdown-it-py, Mako, jsonpatch, jinja2, importlib-metadata, humanfriendly, httplib2, httpcore, h2, googleapis-common-protos, google-resumable-media, ecdsa, deprecation, click, cffi, build, beautifulsoup4, anyio, amqp, aiosignal, aioredis, watchfiles, uvicorn, types-jsonschema, torch, tiktoken, starlette, scikit-learn, rich, requests-toolbelt, requests-oauthlib, python-jose, pytest-asyncio, pydantic, posthog, pandas, opentelemetry-exporter-otlp-proto-common, opentelemetry-api, kombu, jsonschema-specifications, huggingface-hub, httpx, grpcio-status, google-auth, cryptography, coloredlogs, click-repl, click-plugins, click-didyoumean, botocore, azure-core, arxiv, alembic, aiohttp, typer, torchvision, torchaudio, tokenizers, starlette-compress, sse-starlette, s3transfer, realtime, pytrends, pydantic-settings, opentelemetry-semantic-conventions, openai, onnxruntime, langsmith, langgraph-sdk, kubernetes, jsonschema, grpc-google-iam-v1, groq, google-genai, google-auth-oauthlib, google-auth-httplib2, google-api-core, fastapi, celery, azure-storage-blob, anthropic, transformers, supafunc, storage3, postgrest, opentelemetry-sdk, langgraph-cli, langchain-core, gotrue, google-cloud-core, google-api-python-client, boto3, supabase, sentence-transformers, opentelemetry-exporter-otlp-proto-grpc, langgraph-checkpoint, langchain-text-splitters, langchain-openai, langchain-groq, google-cloud-storage, google-cloud-resource-manager, google-cloud-bigquery, google-ai-generativelanguage, agentic-doc, langgraph-prebuilt, langchain-google-genai, langchain, google-cloud-aiplatform, chromadb, langgraph, langgraph-runtime-inmem, langgraph-api
Successfully installed Mako-1.3.10 MarkupSafe-3.0.2 Pillow-11.3.0 PyJWT-2.10.1 PyPDF2-3.0.1 PyYAML-6.0.2 agentic-doc-0.3.1 aiohappyeyeballs-2.6.1 aiohttp-3.12.14 aioredis-2.0.1 aiosignal-1.4.0 alembic-1.16.4 amqp-5.3.1 annotated-types-0.7.0 anthropic-0.58.2 anyio-4.9.0 arxiv-2.2.0 async-timeout-5.0.1 asyncpg-0.30.0 attrs-25.3.0 azure-core-1.35.0 azure-storage-blob-12.26.0 backoff-2.2.1 bcrypt-4.3.0 beautifulsoup4-4.13.4 billiard-4.2.1 blockbuster-1.5.25 boto3-1.39.10 botocore-1.39.10 brotli-1.1.0 build-1.2.2.post1 cachetools-5.5.2 celery-5.5.3 certifi-2025.7.14 cffi-1.17.1 charset_normalizer-3.4.2 chromadb-1.0.15 click-8.2.1 click-didyoumean-0.3.1 click-plugins-1.1.1.2 click-repl-0.3.0 cloudpickle-3.1.1 colorama-0.4.6 coloredlogs-15.0.1 cryptography-44.0.3 deprecation-2.1.0 distro-1.9.0 docstring_parser-0.17.0 docx2txt-0.9 durationpy-0.10 ecdsa-0.19.1 et-xmlfile-2.0.0 fastapi-0.116.1 feedparser-6.0.11 filelock-3.18.0 filetype-1.2.0 flatbuffers-25.2.10 forbiddenfruit-0.1.4 fpdf-1.7.2 frozenlist-1.7.0 fsspec-2025.7.0 google-ai-generativelanguage-0.6.18 google-api-core-2.25.1 google-api-python-client-2.176.0 google-auth-2.40.3 google-auth-httplib2-0.2.0 google-auth-oauthlib-1.2.2 google-cloud-aiplatform-1.104.0 google-cloud-bigquery-3.35.0 google-cloud-core-2.4.3 google-cloud-resource-manager-1.14.2 google-cloud-storage-2.19.0 google-crc32c-1.7.1 google-genai-1.26.0 google-resumable-media-2.7.2 googleapis-common-protos-1.70.0 gotrue-2.12.3 greenlet-3.2.3 groq-0.30.0 grpc-google-iam-v1-0.14.2 grpcio-1.73.1 grpcio-status-1.73.1 h11-0.16.0 h2-4.2.0 hpack-4.1.0 httpcore-1.0.9 httplib2-0.22.0 httptools-0.6.4 httpx-0.28.1 huggingface-hub-0.33.4 humanfriendly-10.0 hyperframe-6.1.0 idna-3.10 importlib-metadata-8.7.0 importlib-resources-6.5.2 iniconfig-2.1.0 isodate-0.7.2 jinja2-3.1.6 jiter-0.10.0 jmespath-1.0.1 joblib-1.5.1 jsonpatch-1.33 jsonpointer-3.0.0 jsonschema-4.25.0 jsonschema-rs-0.29.1 jsonschema-specifications-2025.4.1 kombu-5.5.4 kubernetes-33.1.0 langchain-0.3.26 langchain-core-0.3.70 langchain-google-genai-2.1.8 langchain-groq-0.3.6 langchain-openai-0.3.28 langchain-text-splitters-0.3.8 langgraph-0.5.4 langgraph-api-0.2.98 langgraph-checkpoint-2.1.1 langgraph-cli-0.3.5 langgraph-prebuilt-0.5.2 langgraph-runtime-inmem-0.6.0 langgraph-sdk-0.1.74 langsmith-0.4.8 lxml-6.0.0 markdown-it-py-3.0.0 mdurl-0.1.2 mmh3-5.1.0 mpmath-1.3.0 multidict-6.6.3 mypy-1.17.0 mypy_extensions-1.1.0 networkx-3.5 numpy-2.2.6 oauthlib-3.3.1 onnxruntime-1.22.1 openai-1.97.0 opencv-python-headless-4.12.0.88 openpyxl-3.1.5 opentelemetry-api-1.35.0 opentelemetry-exporter-otlp-proto-common-1.35.0 opentelemetry-exporter-otlp-proto-grpc-1.35.0 opentelemetry-proto-1.35.0 opentelemetry-sdk-1.35.0 opentelemetry-semantic-conventions-0.56b0 orjson-3.11.0 ormsgpack-1.10.0 overrides-7.7.0 packaging-25.0 pandas-2.3.1 passlib-1.7.4 pathspec-0.12.1 pillow-heif-1.0.0 pluggy-1.6.0 postgrest-1.1.1 posthog-5.4.0 prometheus-client-0.22.1 prompt-toolkit-3.0.51 propcache-0.3.2 proto-plus-1.26.1 protobuf-6.31.1 psycopg2-binary-2.9.10 pyasn1-0.6.1 pyasn1-modules-0.4.2 pybase64-1.4.1 pycparser-2.22 pydantic-2.11.7 pydantic-core-2.33.2 pydantic-settings-2.10.1 pygments-2.19.2 pymupdf-1.26.3 pyparsing-3.2.3 pypdf-5.8.0 pypika-0.48.9 pyproject_hooks-1.2.0 pyreadline3-3.5.4 pytest-8.4.1 pytest-asyncio-1.1.0 python-dateutil-2.9.0.post0 python-docx-1.2.0 python-dotenv-1.1.1 python-jose-3.5.0 python-multipart-0.0.20 pytrends-4.9.2 pytz-2025.2 realtime-2.6.0 redis-5.2.1 referencing-0.36.2 regex-2024.11.6 requests-2.32.4 requests-oauthlib-2.0.0 requests-toolbelt-1.0.0 rich-14.0.0 rpds-py-0.26.0 rsa-4.9.1 ruff-0.12.4 s3transfer-0.13.1 safetensors-0.5.3 scikit-learn-1.7.1 scipy-1.16.0 sentence-transformers-5.0.0 setuptools-80.9.0 sgmllib3k-1.0.0 shapely-2.1.1 shellingham-1.5.4 six-1.17.0 sniffio-1.3.1 soupsieve-2.7 sqlalchemy-2.0.41 sse-starlette-2.1.3 starlette-0.47.2 starlette-compress-1.6.1 storage3-0.12.0 strenum-0.4.15 structlog-25.4.0 supabase-2.17.0 supafunc-0.10.1 sympy-1.13.1 tenacity-8.5.0 threadpoolctl-3.6.0 tiktoken-0.9.0 tokenizers-0.21.2 torch-2.5.1+cu121 torchaudio-2.5.1+cu121 torchvision-0.20.1+cu121 tqdm-4.67.1 transformers-4.53.2 truststore-0.10.1 typer-0.16.0 types-jsonschema-4.25.0.20250720 typing-extensions-4.14.1 typing-inspection-0.4.1 tzdata-2025.2 uritemplate-4.2.0 urllib3-2.5.0 uvicorn-0.35.0 vine-5.1.0 watchfiles-1.1.0 wcwidth-0.2.13 websocket-client-1.8.0 websockets-15.0.1 xxhash-3.5.0 yarl-1.20.1 zipp-3.23.0 zstandard-0.23.0
(.venv) PS D:\multiagentwriterz\backend> python -c "import torch, platform, sys; \
>> print(f'torch {torch.__version__} | CUDA available? {torch.cuda.is_available()}'); \
>> print('python', sys.version.split()[0], 'on', platform.system()); \
>> print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
torch 2.5.1+cu121 | CUDA available? False
python 3.12.3 on Windows
GPU: CPU only
(.venv) PS D:\multiagentwriterz\backend> python -c "import torch, sys, platform; \
>> print(f'CUDA available? {torch.cuda.is_available()}'); \
>> print('torch', torch.__version__, '|', 'CUDA build', torch.version.cuda); \
>> print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); \
>> print('Driver API version:', torch.cuda.driver_version() if torch.cuda.is_available() else 'N/A')"
CUDA available? False
torch 2.5.1+cu121 | CUDA build 12.1
GPU: None
Driver API version: N/A
(.venv) PS D:\multiagentwriterz\backend>


