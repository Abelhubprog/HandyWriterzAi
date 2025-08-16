PS D:\HandyWriterzAi> .\backend\scripts\test-win.ps1
== HandyWriterzAI Windows test runner ==
Creating .venv with Python 3.11...
Unable to create process using 'C:\Python311\python.exe -m venv .venv': The system cannot find the file specified.

Write-Error: Failed to activate venv at .venv\Scripts\Activate.ps1
PS D:\HandyWriterzAi> .\backend\scripts\test-win.ps1 -All
== HandyWriterzAI Windows test runner ==
Creating .venv with Python 3.11...
Unable to create process using 'C:\Python311\python.exe -m venv .venv': The system cannot find the file specified.

Write-Error: Failed to activate venv at .venv\Scripts\Activate.ps1
PS D:\HandyWriterzAi> py -3.11 -m venv .venv
Unable to create process using 'C:\Python311\python.exe -m venv .venv': The system cannot find the file specified.

PS D:\HandyWriterzAi> .\.venv\Scripts\Activate.ps1
.\.venv\Scripts\Activate.ps1: The term '.\.venv\Scripts\Activate.ps1' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS D:\HandyWriterzAi> python -m pip install -r backend\requirements.txt
Requirement already satisfied: agentic-doc==0.3.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 7)) (0.3.1)
Requirement already satisfied: aiohappyeyeballs==2.6.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 9)) (2.6.1)
Requirement already satisfied: aiohttp==3.12.14 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 11)) (3.12.14)
Requirement already satisfied: aioredis==2.0.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 13)) (2.0.1)
Requirement already satisfied: aiosignal==1.4.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 15)) (1.4.0)
Requirement already satisfied: alembic==1.16.4 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 17)) (1.16.4)
Requirement already satisfied: amqp==5.3.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 19)) (5.3.1)
Requirement already satisfied: annotated-types==0.7.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 21)) (0.7.0)
Requirement already satisfied: anthropic==0.58.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 23)) (0.58.2)
Requirement already satisfied: anyio==4.9.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 25)) (4.9.0)
Requirement already satisfied: arxiv==2.2.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 35)) (2.2.0)
Requirement already satisfied: async-timeout==5.0.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 37)) (5.0.1)
Requirement already satisfied: asyncpg==0.30.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 39)) (0.30.0)
Requirement already satisfied: attrs==25.3.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 41)) (25.3.0)
Requirement already satisfied: azure-core==1.35.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 46)) (1.35.0)
Requirement already satisfied: azure-storage-blob==12.26.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 48)) (12.26.0)      
Requirement already satisfied: backoff==2.2.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 50)) (2.2.1)
Requirement already satisfied: bcrypt==4.3.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 52)) (4.3.0)
Requirement already satisfied: beautifulsoup4==4.13.4 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 57)) (4.13.4)
Requirement already satisfied: billiard==4.2.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 59)) (4.2.1)
Requirement already satisfied: blockbuster==1.5.25 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 61)) (1.5.25)
Requirement already satisfied: boto3==1.39.10 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 63)) (1.39.10)
Requirement already satisfied: botocore==1.39.10 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 67)) (1.39.10)
Requirement already satisfied: brotli==1.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 71)) (1.1.0)
Requirement already satisfied: build==1.2.2.post1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 73)) (1.2.2.post1)
Requirement already satisfied: cachetools==5.5.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 75)) (5.5.2)
Requirement already satisfied: celery==5.5.3 in d:\handywriterzai\backend_env\lib\site-packages (from celery[redis]==5.5.3->-r backend\requirements.txt (line 77)) (5.5.3)Collecting certifi==2025.7.14 (from -r backend\requirements.txt (line 79))
  Using cached certifi-2025.7.14-py3-none-any.whl.metadata (2.4 kB)
Requirement already satisfied: cffi==1.17.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 85)) (1.17.1)
Collecting charset-normalizer==3.4.2 (from -r backend\requirements.txt (line 87))
  Using cached charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl.metadata (36 kB)
Requirement already satisfied: chromadb==1.0.15 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 89)) (1.0.15)
Requirement already satisfied: click==8.2.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 91)) (8.2.1)
Requirement already satisfied: click-didyoumean==0.3.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 100)) (0.3.1)
Requirement already satisfied: click-plugins==1.1.1.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 102)) (1.1.1.2)
Requirement already satisfied: click-repl==0.3.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 104)) (0.3.0)
Requirement already satisfied: cloudpickle==3.1.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 106)) (3.1.1)
Requirement already satisfied: coloredlogs==15.0.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 108)) (15.0.1)
Requirement already satisfied: cryptography==44.0.3 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 110)) (44.0.3)
Requirement already satisfied: deprecation==2.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 116)) (2.1.0)
Requirement already satisfied: distro==1.9.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 120)) (1.9.0)
Requirement already satisfied: docstring-parser==0.17.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 126)) (0.17.0)
Requirement already satisfied: docx2txt==0.9 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 128)) (0.9)
Requirement already satisfied: durationpy==0.10 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 130)) (0.10)
Requirement already satisfied: ecdsa==0.19.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 132)) (0.19.1)
Requirement already satisfied: et-xmlfile==2.0.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 134)) (2.0.0)
Requirement already satisfied: fastapi==0.116.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 136)) (0.116.1)
Requirement already satisfied: feedparser==6.0.11 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 138)) (6.0.11)
Requirement already satisfied: filelock==3.18.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 142)) (3.18.0)
Requirement already satisfied: filetype==1.2.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 148)) (1.2.0)
Requirement already satisfied: flatbuffers==25.2.10 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 150)) (25.2.10)
Requirement already satisfied: forbiddenfruit==0.1.4 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 152)) (0.1.4)
Requirement already satisfied: fpdf==1.7.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 154)) (1.7.2)
Requirement already satisfied: frozenlist==1.7.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 156)) (1.7.0)
Requirement already satisfied: fsspec==2025.7.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 160)) (2025.7.0)
Requirement already satisfied: google-ai-generativelanguage==0.6.18 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 164)) (0.6.18)
Requirement already satisfied: google-api-core==2.25.1 in d:\handywriterzai\backend_env\lib\site-packages (from google-api-core[grpc]==2.25.1->-r backend\requirements.txt (line 166)) (2.25.1)
Collecting google-api-python-client==2.176.0 (from -r backend\requirements.txt (line 
175))
  Using cached google_api_python_client-2.176.0-py3-none-any.whl.metadata (7.0 kB)
Requirement already satisfied: google-auth==2.40.3 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 177)) (2.40.3)
Requirement already satisfied: google-auth-httplib2==0.2.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 192)) (0.2.0)       
Requirement already satisfied: google-auth-oauthlib==1.2.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 194)) (1.2.2)       
Requirement already satisfied: google-cloud-aiplatform==1.104.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 196)) (1.104.0)Requirement already satisfied: google-cloud-bigquery==3.35.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 198)) (3.35.0)    
Requirement already satisfied: google-cloud-core==2.4.3 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 200)) (2.4.3)
Requirement already satisfied: google-cloud-resource-manager==1.14.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 204)) (1.14.2)
Requirement already satisfied: google-cloud-storage==2.19.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 206)) (2.19.0)     
Requirement already satisfied: google-crc32c==1.7.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 208)) (1.7.1)
Requirement already satisfied: google-genai==1.26.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 212)) (1.26.0)
Requirement already satisfied: google-resumable-media==2.7.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 216)) (2.7.2)     
Requirement already satisfied: googleapis-common-protos==1.70.0 in d:\handywriterzai\backend_env\lib\site-packages (from googleapis-common-protos[grpc]==1.70.0->-r backend\requirements.txt (line 220)) (1.70.0)
Requirement already satisfied: gotrue==2.12.3 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 226)) (2.12.3)
Requirement already satisfied: greenlet==3.2.3 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 228)) (3.2.3)
Requirement already satisfied: groq==0.30.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 230)) (0.30.0)
Requirement already satisfied: grpc-google-iam-v1==0.14.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 232)) (0.14.2)       
Collecting grpcio==1.73.1 (from -r backend\requirements.txt (line 234))
  Using cached grpcio-1.73.1-cp312-cp312-win_amd64.whl.metadata (4.0 kB)
Collecting grpcio-status==1.73.1 (from -r backend\requirements.txt (line 242))
  Using cached grpcio_status-1.73.1-py3-none-any.whl.metadata (1.1 kB)
Requirement already satisfied: h11==0.16.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 244)) (0.16.0)
Requirement already satisfied: h2==4.2.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 248)) (4.2.0)
Requirement already satisfied: hf-xet==1.1.5 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 250)) (1.1.5)
Requirement already satisfied: hpack==4.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 252)) (4.1.0)
Requirement already satisfied: httpcore==1.0.9 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 254)) (1.0.9)
Requirement already satisfied: httplib2==0.22.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 256)) (0.22.0)
Requirement already satisfied: httptools==0.6.4 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 260)) (0.6.4)
Requirement already satisfied: httpx==0.28.1 in d:\handywriterzai\backend_env\lib\site-packages (from httpx[http2]==0.28.1->-r backend\requirements.txt (line 262)) (0.28.1)
Requirement already satisfied: huggingface-hub==0.33.4 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 279)) (0.33.4)
Requirement already satisfied: humanfriendly==10.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 284)) (10.0)
Requirement already satisfied: hyperframe==6.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 286)) (6.1.0)
Requirement already satisfied: idna==3.10 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 288)) (3.10)
Requirement already satisfied: importlib-metadata==8.7.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 294)) (8.7.0)
Requirement already satisfied: importlib-resources==6.5.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 296)) (6.5.2)        
Requirement already satisfied: iniconfig==2.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 298)) (2.1.0)
Requirement already satisfied: isodate==0.7.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 300)) (0.7.2)
Requirement already satisfied: jinja2==3.1.6 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 302)) (3.1.6)
Requirement already satisfied: jiter==0.10.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 304)) (0.10.0)
Requirement already satisfied: jmespath==1.0.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 308)) (1.0.1)
Requirement already satisfied: joblib==1.5.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 312)) (1.5.1)
Requirement already satisfied: jsonpatch==1.33 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 314)) (1.33)
Requirement already satisfied: jsonpointer==3.0.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 316)) (3.0.0)
Requirement already satisfied: jsonschema==4.25.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 318)) (4.25.0)
Requirement already satisfied: jsonschema-rs==0.29.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 322)) (0.29.1)
Requirement already satisfied: jsonschema-specifications==2025.4.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 324)) (2025.4.1)
Requirement already satisfied: kombu==5.5.4 in d:\handywriterzai\backend_env\lib\site-packages (from kombu[redis]==5.5.4->-r backend\requirements.txt (line 326)) (5.5.4) 
Requirement already satisfied: kubernetes==33.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 328)) (33.1.0)
Requirement already satisfied: langchain==0.3.26 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 330)) (0.3.26)
Requirement already satisfied: langchain-community==0.3.27 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 332)) (0.3.27)      
Requirement already satisfied: langchain-core==0.3.70 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 334)) (0.3.70)
Requirement already satisfied: langchain-google-genai==2.1.8 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 346)) (2.1.8)     
Requirement already satisfied: langchain-groq==0.3.6 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 348)) (0.3.6)
Requirement already satisfied: langchain-openai==0.3.28 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 350)) (0.3.28)
Requirement already satisfied: langchain-text-splitters==0.3.8 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 352)) (0.3.8)   
Requirement already satisfied: langgraph==0.5.4 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 354)) (0.5.4)
Requirement already satisfied: langgraph-api==0.2.98 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 359)) (0.2.98)
Requirement already satisfied: langgraph-checkpoint==2.1.1 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 363)) (2.1.1)       
Requirement already satisfied: langgraph-cli==0.3.5 in d:\handywriterzai\backend_env\lib\site-packages (from langgraph-cli[inmem]==0.3.5->-r backend\requirements.txt (line 369)) (0.3.5)
Requirement already satisfied: langgraph-prebuilt==0.5.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 371)) (0.5.2)
Requirement already satisfied: langgraph-runtime-inmem==0.6.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 373)) (0.6.0)    
Requirement already satisfied: langgraph-sdk==0.1.74 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 377)) (0.1.74)
Requirement already satisfied: langsmith==0.4.8 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 382)) (0.4.8)
Requirement already satisfied: lxml==6.0.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 387)) (6.0.0)
Requirement already satisfied: mako==1.3.10 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 391)) (1.3.10)
Requirement already satisfied: markdown-it-py==3.0.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 393)) (3.0.0)
Requirement already satisfied: markupsafe==3.0.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 395)) (3.0.2)
Requirement already satisfied: mdurl==0.1.2 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 399)) (0.1.2)
Requirement already satisfied: mmh3==5.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 401)) (5.1.0)
Requirement already satisfied: mpmath==1.3.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 403)) (1.3.0)
Requirement already satisfied: multidict==6.6.3 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 405)) (6.6.3)
Requirement already satisfied: mypy==1.17.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 409)) (1.17.0)
Requirement already satisfied: mypy-extensions==1.1.0 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 411)) (1.1.0)
Requirement already satisfied: networkx==3.5 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 413)) (3.5)
Requirement already satisfied: numpy==2.2.6 in d:\handywriterzai\backend_env\lib\site-packages (from -r backend\requirements.txt (line 415)) (2.2.6)
Collecting nvidia-cublas-cu12==12.4.5.8 (from -r backend\requirements.txt (line 425))  Using cached nvidia_cublas_cu12-12.4.5.8-py3-none-win_amd64.whl.metadata (1.5 kB)
Collecting nvidia-cuda-cupti-cu12==12.4.127 (from -r backend\requirements.txt (line 430))
  Using cached nvidia_cuda_cupti_cu12-12.4.127-py3-none-win_amd64.whl.metadata (1.6 kB)
Collecting nvidia-cuda-nvrtc-cu12==12.4.127 (from -r backend\requirements.txt (line 432))
  Using cached nvidia_cuda_nvrtc_cu12-12.4.127-py3-none-win_amd64.whl.metadata (1.5 kB)
Collecting nvidia-cuda-runtime-cu12==12.4.127 (from -r backend\requirements.txt (line 434))
  Using cached nvidia_cuda_runtime_cu12-12.4.127-py3-none-win_amd64.whl.metadata (1.5 kB)
Collecting nvidia-cudnn-cu12==9.1.0.70 (from -r backend\requirements.txt (line 436))
  Using cached nvidia_cudnn_cu12-9.1.0.70-py3-none-win_amd64.whl.metadata (1.6 kB)
Collecting nvidia-cufft-cu12==11.2.1.3 (from -r backend\requirements.txt (line 438))
  Using cached nvidia_cufft_cu12-11.2.1.3-py3-none-win_amd64.whl.metadata (1.5 kB)
Collecting nvidia-curand-cu12==10.3.5.147 (from -r backend\requirements.txt (line 440))
  Using cached nvidia_curand_cu12-10.3.5.147-py3-none-win_amd64.whl.metadata (1.5 kB)Collecting nvidia-cusolver-cu12==11.6.1.9 (from -r backend\requirements.txt (line 442))
  Using cached nvidia_cusolver_cu12-11.6.1.9-py3-none-win_amd64.whl.metadata (1.6 kB)Collecting nvidia-cusparse-cu12==12.3.1.170 (from -r backend\requirements.txt (line 444))
  Using cached nvidia_cusparse_cu12-12.3.1.170-py3-none-win_amd64.whl.metadata (1.6 kB)
ERROR: Could not find a version that satisfies the requirement nvidia-nccl-cu12==2.21.5 (from versions: 0.0.1.dev5)
ERROR: No matching distribution found for nvidia-nccl-cu12==2.21.5
PS D:\HandyWriterzAi> set PYTHONPATH=.;backend;backend\src
backend: The term 'backend' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
backend\src: The module 'backend' could not be loaded. For more information, run 'Import-Module backend'.
PS D:\HandyWriterzAi> pytest -q

====================================== ERRORS ======================================
_____________ ERROR collecting backend/src/tests/e2e/test_full_flow.py _____________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\e2e\test_full_flow.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\e2e\test_full_flow.py:15: in <module>
    from src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
__________________ ERROR collecting backend/src/tests/test_api.py __________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_api.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_api.py:3: in <module>
    from backend.src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
______ ERROR collecting backend/src/tests/test_chat_init_returns_trace_id.py _______ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_chat_init_returns_trace_id.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/mnt/d/handywriterzai/backend/src/tests/test_chat_init_returns_trace_id.py:22: in <module>
    ???
backend\src\routes\chat_gateway.py:17: in <module>
    from ..services.model_selector import get_model_selector, SelectionContext, SelectionStrategy
backend\src\services\model_selector.py:17: in <module>
    from .model_policy import ModelPolicyRegistry, get_model_policy_registry, NodeCapabilityRequirement
backend\src\services\model_policy.py:20: in <module>
    from .gateway import ModelSpec, ModelCapability, ProviderType
E   ImportError: cannot import name 'ModelSpec' from '<unknown module name>' (unknown location)
__________ ERROR collecting backend/src/tests/test_memory_integration.py ___________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_memory_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_memory_integration.py:12: in <module>
    from services.memory_integrator import get_memory_integrator
backend\src\services\memory_integrator.py:15: in <module>
    from ..db.database import get_db_manager
E   ImportError: attempted relative import beyond top-level package
___________ ERROR collecting backend/src/tests/test_search_perplexity.py ___________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_search_perplexity.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_search_perplexity.py:3: in <module>
    from agent.nodes.search_perplexity import PerplexitySearchAgent
backend\src\agent\nodes\search_perplexity.py:17: in <module>
    from ...agent.handywriterz_state import HandyWriterzState
E   ImportError: attempted relative import beyond top-level package
_______________ ERROR collecting backend/src/tests/test_services.py ________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_services.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_services.py:3: in <module>
    from backend.src.services.chunk_splitter import chunk_splitter
backend\src\services\chunk_splitter.py:16: in <module>
    import aiofiles
E   ModuleNotFoundError: No module named 'aiofiles'
_________ ERROR collecting backend/src/tests/test_turnitin_idempotency.py __________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_turnitin_idempotency.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_turnitin_idempotency.py:6: in <module>
    from backend.src.db.database import get_db_manager
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
_____________ ERROR collecting backend/src/tests/test_user_journey.py ______________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_user_journey.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_user_journey.py:8: in <module>
    from src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
________________ ERROR collecting backend/src/tests/test_writer.py _________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_writer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\tests\test_writer.py:3: in <module>
    from agent.nodes.writer import RevolutionaryWriterAgent
backend\src\agent\nodes\writer.py:20: in <module>
    from src.services.llm_service import get_llm_client
backend\src\services\llm_service.py:5: in <module>
    from langchain_anthropic import ChatAnthropic
E   ModuleNotFoundError: No module named 'langchain_anthropic'
================================= warnings summary ================================= 
backend_env\Lib\site-packages\pydantic\fields.py:1093: 64 warnings
  d:\HandyWriterzAi\backend_env\Lib\site-packages\pydantic\fields.py:1093: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'env'). Deprecated in Pydantic 
V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

backend_env\Lib\site-packages\pydantic\_internal\_config.py:323
  d:\HandyWriterzAi\backend_env\Lib\site-packages\pydantic\_internal\_config.py:323: 
PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

backend\src\services\prompt_orchestrator.py:161
  D:\HandyWriterzAi\backend\src\services\prompt_orchestrator.py:161: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator('use_cases')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================= short test summary info ============================== 
ERROR backend/src/tests/e2e/test_full_flow.py
ERROR backend/src/tests/test_api.py
ERROR backend/src/tests/test_chat_init_returns_trace_id.py
ERROR backend/src/tests/test_memory_integration.py
ERROR backend/src/tests/test_search_perplexity.py
ERROR backend/src/tests/test_services.py
ERROR backend/src/tests/test_turnitin_idempotency.py
ERROR backend/src/tests/test_user_journey.py
ERROR backend/src/tests/test_writer.py
!!!!!!!!!!!!!!!!!!!!! Interrupted: 9 errors during collection !!!!!!!!!!!!!!!!!!!!!! 
PS D:\HandyWriterzAi> 