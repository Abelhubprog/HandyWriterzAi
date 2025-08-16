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
PS D:\HandyWriterzAi> .\backend\scripts\test-win.ps1
== HandyWriterzAI Windows test runner ==
Creating .venv using available Python...
Activating venv...
Installing deps from backend\requirements.txt...
Collecting agentic-doc==0.3.1 (from -r backend\requirements.txt (line 7))
  Using cached agentic_doc-0.3.1-py3-none-any.whl.metadata (19 kB)
Collecting aiohappyeyeballs==2.6.1 (from -r backend\requirements.txt (line 9))
  Using cached aiohappyeyeballs-2.6.1-py3-none-any.whl.metadata (5.9 kB)
Collecting aiohttp==3.12.14 (from -r backend\requirements.txt (line 11))
  Using cached aiohttp-3.12.14-cp312-cp312-win_amd64.whl.metadata (7.9 kB)
Collecting aioredis==2.0.1 (from -r backend\requirements.txt (line 13))
  Using cached aioredis-2.0.1-py3-none-any.whl.metadata (15 kB)
Collecting aiosignal==1.4.0 (from -r backend\requirements.txt (line 15))
  Using cached aiosignal-1.4.0-py3-none-any.whl.metadata (3.7 kB)
Collecting alembic==1.16.4 (from -r backend\requirements.txt (line 17))
  Using cached alembic-1.16.4-py3-none-any.whl.metadata (7.3 kB)
Collecting amqp==5.3.1 (from -r backend\requirements.txt (line 19))
  Using cached amqp-5.3.1-py3-none-any.whl.metadata (8.9 kB)
Collecting annotated-types==0.7.0 (from -r backend\requirements.txt (line 21))
  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting anthropic==0.58.2 (from -r backend\requirements.txt (line 23))
  Using cached anthropic-0.58.2-py3-none-any.whl.metadata (27 kB)
Collecting anyio==4.9.0 (from -r backend\requirements.txt (line 25))
  Using cached anyio-4.9.0-py3-none-any.whl.metadata (4.7 kB)
Collecting arxiv==2.2.0 (from -r backend\requirements.txt (line 35))
  Using cached arxiv-2.2.0-py3-none-any.whl.metadata (6.3 kB)
Collecting async-timeout==5.0.1 (from -r backend\requirements.txt (line 37))
  Using cached async_timeout-5.0.1-py3-none-any.whl.metadata (5.1 kB)
Collecting asyncpg==0.30.0 (from -r backend\requirements.txt (line 39))
  Using cached asyncpg-0.30.0-cp312-cp312-win_amd64.whl.metadata (5.2 kB)
Collecting attrs==25.3.0 (from -r backend\requirements.txt (line 41))
  Using cached attrs-25.3.0-py3-none-any.whl.metadata (10 kB)
Collecting azure-core==1.35.0 (from -r backend\requirements.txt (line 46))
  Using cached azure_core-1.35.0-py3-none-any.whl.metadata (44 kB)
Collecting azure-storage-blob==12.26.0 (from -r backend\requirements.txt (line 48))
  Using cached azure_storage_blob-12.26.0-py3-none-any.whl.metadata (26 kB)
Collecting backoff==2.2.1 (from -r backend\requirements.txt (line 50))
  Using cached backoff-2.2.1-py3-none-any.whl.metadata (14 kB)
Collecting bcrypt==4.3.0 (from -r backend\requirements.txt (line 52))
  Using cached bcrypt-4.3.0-cp39-abi3-win_amd64.whl.metadata (10 kB)
Collecting beautifulsoup4==4.13.4 (from -r backend\requirements.txt (line 57))
  Using cached beautifulsoup4-4.13.4-py3-none-any.whl.metadata (3.8 kB)
Collecting billiard==4.2.1 (from -r backend\requirements.txt (line 59))
  Using cached billiard-4.2.1-py3-none-any.whl.metadata (4.4 kB)
Collecting blockbuster==1.5.25 (from -r backend\requirements.txt (line 61))
  Using cached blockbuster-1.5.25-py3-none-any.whl.metadata (10 kB)
Collecting boto3==1.39.10 (from -r backend\requirements.txt (line 63))
  Using cached boto3-1.39.10-py3-none-any.whl.metadata (6.7 kB)
Collecting botocore==1.39.10 (from -r backend\requirements.txt (line 67))
  Using cached botocore-1.39.10-py3-none-any.whl.metadata (5.7 kB)
Collecting brotli==1.1.0 (from -r backend\requirements.txt (line 71))
  Using cached Brotli-1.1.0-cp312-cp312-win_amd64.whl.metadata (5.6 kB)
Collecting build==1.2.2.post1 (from -r backend\requirements.txt (line 73))
  Using cached build-1.2.2.post1-py3-none-any.whl.metadata (6.5 kB)
Collecting cachetools==5.5.2 (from -r backend\requirements.txt (line 75))
  Using cached cachetools-5.5.2-py3-none-any.whl.metadata (5.4 kB)
Collecting celery==5.5.3 (from celery[redis]==5.5.3->-r backend\requirements.txt (line 77))
  Using cached celery-5.5.3-py3-none-any.whl.metadata (22 kB)
Collecting certifi==2025.7.14 (from -r backend\requirements.txt (line 79))
  Using cached certifi-2025.7.14-py3-none-any.whl.metadata (2.4 kB)
Collecting cffi==1.17.1 (from -r backend\requirements.txt (line 85))
  Using cached cffi-1.17.1-cp312-cp312-win_amd64.whl.metadata (1.6 kB)
Collecting charset-normalizer==3.4.2 (from -r backend\requirements.txt (line 87))
  Using cached charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl.metadata (36 kB)
Collecting chromadb==1.0.15 (from -r backend\requirements.txt (line 89))
  Using cached chromadb-1.0.15-cp39-abi3-win_amd64.whl.metadata (7.1 kB)
Collecting click==8.2.1 (from -r backend\requirements.txt (line 91))
  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting click-didyoumean==0.3.1 (from -r backend\requirements.txt (line 100))
  Using cached click_didyoumean-0.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting click-plugins==1.1.1.2 (from -r backend\requirements.txt (line 102))
  Using cached click_plugins-1.1.1.2-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting click-repl==0.3.0 (from -r backend\requirements.txt (line 104))
  Using cached click_repl-0.3.0-py3-none-any.whl.metadata (3.6 kB)
Collecting cloudpickle==3.1.1 (from -r backend\requirements.txt (line 106))
  Using cached cloudpickle-3.1.1-py3-none-any.whl.metadata (7.1 kB)
Collecting coloredlogs==15.0.1 (from -r backend\requirements.txt (line 108))
  Using cached coloredlogs-15.0.1-py2.py3-none-any.whl.metadata (12 kB)
Collecting cryptography==44.0.3 (from -r backend\requirements.txt (line 110))
  Using cached cryptography-44.0.3-cp39-abi3-win_amd64.whl.metadata (5.7 kB)
Collecting deprecation==2.1.0 (from -r backend\requirements.txt (line 116))
  Using cached deprecation-2.1.0-py2.py3-none-any.whl.metadata (4.6 kB)
Collecting distro==1.9.0 (from -r backend\requirements.txt (line 120))
  Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
Collecting docstring-parser==0.17.0 (from -r backend\requirements.txt (line 126))
  Using cached docstring_parser-0.17.0-py3-none-any.whl.metadata (3.5 kB)
Collecting docx2txt==0.9 (from -r backend\requirements.txt (line 128))
  Using cached docx2txt-0.9-py3-none-any.whl.metadata (529 bytes)
Collecting durationpy==0.10 (from -r backend\requirements.txt (line 130))
  Using cached durationpy-0.10-py3-none-any.whl.metadata (340 bytes)
Collecting ecdsa==0.19.1 (from -r backend\requirements.txt (line 132))
  Using cached ecdsa-0.19.1-py2.py3-none-any.whl.metadata (29 kB)
Collecting et-xmlfile==2.0.0 (from -r backend\requirements.txt (line 134))
  Using cached et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
Collecting fastapi==0.116.1 (from -r backend\requirements.txt (line 136))
  Using cached fastapi-0.116.1-py3-none-any.whl.metadata (28 kB)
Collecting feedparser==6.0.11 (from -r backend\requirements.txt (line 138))
  Using cached feedparser-6.0.11-py3-none-any.whl.metadata (2.4 kB)
Collecting filelock==3.18.0 (from -r backend\requirements.txt (line 142))
  Using cached filelock-3.18.0-py3-none-any.whl.metadata (2.9 kB)
Collecting filetype==1.2.0 (from -r backend\requirements.txt (line 148))
  Using cached filetype-1.2.0-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting flatbuffers==25.2.10 (from -r backend\requirements.txt (line 150))
  Using cached flatbuffers-25.2.10-py2.py3-none-any.whl.metadata (875 bytes)
Collecting forbiddenfruit==0.1.4 (from -r backend\requirements.txt (line 152))
  Using cached forbiddenfruit-0.1.4-py3-none-any.whl
Collecting fpdf==1.7.2 (from -r backend\requirements.txt (line 154))
  Using cached fpdf-1.7.2-py2.py3-none-any.whl
Collecting frozenlist==1.7.0 (from -r backend\requirements.txt (line 156))
  Using cached frozenlist-1.7.0-cp312-cp312-win_amd64.whl.metadata (19 kB)
Collecting fsspec==2025.7.0 (from -r backend\requirements.txt (line 160))
  Using cached fsspec-2025.7.0-py3-none-any.whl.metadata (12 kB)
Collecting google-ai-generativelanguage==0.6.18 (from -r backend\requirements.txt (line 164))
  Using cached google_ai_generativelanguage-0.6.18-py3-none-any.whl.metadata (9.8 kB)Collecting google-api-core==2.25.1 (from google-api-core[grpc]==2.25.1->-r backend\requirements.txt (line 166))
  Using cached google_api_core-2.25.1-py3-none-any.whl.metadata (3.0 kB)
Collecting google-api-python-client==2.176.0 (from -r backend\requirements.txt (line 
175))
  Using cached google_api_python_client-2.176.0-py3-none-any.whl.metadata (7.0 kB)
Collecting google-auth==2.40.3 (from -r backend\requirements.txt (line 177))
  Using cached google_auth-2.40.3-py2.py3-none-any.whl.metadata (6.2 kB)
Collecting google-auth-httplib2==0.2.0 (from -r backend\requirements.txt (line 192))
  Using cached google_auth_httplib2-0.2.0-py2.py3-none-any.whl.metadata (2.2 kB)
Collecting google-auth-oauthlib==1.2.2 (from -r backend\requirements.txt (line 194))
  Using cached google_auth_oauthlib-1.2.2-py3-none-any.whl.metadata (2.7 kB)
Collecting google-cloud-aiplatform==1.104.0 (from -r backend\requirements.txt (line 196))
  Using cached google_cloud_aiplatform-1.104.0-py2.py3-none-any.whl.metadata (38 kB)
Collecting google-cloud-bigquery==3.35.0 (from -r backend\requirements.txt (line 198))
  Using cached google_cloud_bigquery-3.35.0-py3-none-any.whl.metadata (8.0 kB)
Collecting google-cloud-core==2.4.3 (from -r backend\requirements.txt (line 200))
  Using cached google_cloud_core-2.4.3-py2.py3-none-any.whl.metadata (2.7 kB)
Collecting google-cloud-resource-manager==1.14.2 (from -r backend\requirements.txt (line 204))
  Using cached google_cloud_resource_manager-1.14.2-py3-none-any.whl.metadata (9.6 kB)
Collecting google-cloud-storage==2.19.0 (from -r backend\requirements.txt (line 206))  Using cached google_cloud_storage-2.19.0-py2.py3-none-any.whl.metadata (9.1 kB)
Collecting google-crc32c==1.7.1 (from -r backend\requirements.txt (line 208))
  Using cached google_crc32c-1.7.1-cp312-cp312-win_amd64.whl.metadata (2.4 kB)
Collecting google-genai==1.26.0 (from -r backend\requirements.txt (line 212))
  Using cached google_genai-1.26.0-py3-none-any.whl.metadata (42 kB)
Collecting google-resumable-media==2.7.2 (from -r backend\requirements.txt (line 216))
  Using cached google_resumable_media-2.7.2-py2.py3-none-any.whl.metadata (2.2 kB)
Collecting googleapis-common-protos==1.70.0 (from googleapis-common-protos[grpc]==1.70.0->-r backend\requirements.txt (line 220))
  Using cached googleapis_common_protos-1.70.0-py3-none-any.whl.metadata (9.3 kB)
Collecting gotrue==2.12.3 (from -r backend\requirements.txt (line 226))
  Using cached gotrue-2.12.3-py3-none-any.whl.metadata (6.5 kB)
Collecting greenlet==3.2.3 (from -r backend\requirements.txt (line 228))
  Using cached greenlet-3.2.3-cp312-cp312-win_amd64.whl.metadata (4.2 kB)
Collecting groq==0.30.0 (from -r backend\requirements.txt (line 230))
  Using cached groq-0.30.0-py3-none-any.whl.metadata (16 kB)
Collecting grpc-google-iam-v1==0.14.2 (from -r backend\requirements.txt (line 232))
  Using cached grpc_google_iam_v1-0.14.2-py3-none-any.whl.metadata (9.1 kB)
Collecting grpcio==1.73.1 (from -r backend\requirements.txt (line 234))
  Using cached grpcio-1.73.1-cp312-cp312-win_amd64.whl.metadata (4.0 kB)
Collecting grpcio-status==1.73.1 (from -r backend\requirements.txt (line 242))
  Using cached grpcio_status-1.73.1-py3-none-any.whl.metadata (1.1 kB)
Collecting h11==0.16.0 (from -r backend\requirements.txt (line 244))
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting h2==4.2.0 (from -r backend\requirements.txt (line 248))
  Using cached h2-4.2.0-py3-none-any.whl.metadata (5.1 kB)
Collecting hf-xet==1.1.5 (from -r backend\requirements.txt (line 250))
  Using cached hf_xet-1.1.5-cp37-abi3-win_amd64.whl.metadata (883 bytes)
Collecting hpack==4.1.0 (from -r backend\requirements.txt (line 252))
  Using cached hpack-4.1.0-py3-none-any.whl.metadata (4.6 kB)
Collecting httpcore==1.0.9 (from -r backend\requirements.txt (line 254))
  Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Collecting httplib2==0.22.0 (from -r backend\requirements.txt (line 256))
  Using cached httplib2-0.22.0-py3-none-any.whl.metadata (2.6 kB)
Collecting httptools==0.6.4 (from -r backend\requirements.txt (line 260))
  Using cached httptools-0.6.4-cp312-cp312-win_amd64.whl.metadata (3.7 kB)
Collecting httpx==0.28.1 (from httpx[http2]==0.28.1->-r backend\requirements.txt (line 262))
  Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Collecting huggingface-hub==0.33.4 (from -r backend\requirements.txt (line 279))
  Using cached huggingface_hub-0.33.4-py3-none-any.whl.metadata (14 kB)
Collecting humanfriendly==10.0 (from -r backend\requirements.txt (line 284))
  Using cached humanfriendly-10.0-py2.py3-none-any.whl.metadata (9.2 kB)
Collecting hyperframe==6.1.0 (from -r backend\requirements.txt (line 286))
  Using cached hyperframe-6.1.0-py3-none-any.whl.metadata (4.3 kB)
Collecting idna==3.10 (from -r backend\requirements.txt (line 288))
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting importlib-metadata==8.7.0 (from -r backend\requirements.txt (line 294))
  Using cached importlib_metadata-8.7.0-py3-none-any.whl.metadata (4.8 kB)
Collecting importlib-resources==6.5.2 (from -r backend\requirements.txt (line 296))
  Using cached importlib_resources-6.5.2-py3-none-any.whl.metadata (3.9 kB)
Collecting iniconfig==2.1.0 (from -r backend\requirements.txt (line 298))
  Using cached iniconfig-2.1.0-py3-none-any.whl.metadata (2.7 kB)
Collecting isodate==0.7.2 (from -r backend\requirements.txt (line 300))
  Using cached isodate-0.7.2-py3-none-any.whl.metadata (11 kB)
Collecting jinja2==3.1.6 (from -r backend\requirements.txt (line 302))
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting jiter==0.10.0 (from -r backend\requirements.txt (line 304))
  Using cached jiter-0.10.0-cp312-cp312-win_amd64.whl.metadata (5.3 kB)
Collecting jmespath==1.0.1 (from -r backend\requirements.txt (line 308))
  Using cached jmespath-1.0.1-py3-none-any.whl.metadata (7.6 kB)
Collecting joblib==1.5.1 (from -r backend\requirements.txt (line 312))
  Using cached joblib-1.5.1-py3-none-any.whl.metadata (5.6 kB)
Collecting jsonpatch==1.33 (from -r backend\requirements.txt (line 314))
  Using cached jsonpatch-1.33-py2.py3-none-any.whl.metadata (3.0 kB)
Collecting jsonpointer==3.0.0 (from -r backend\requirements.txt (line 316))
  Using cached jsonpointer-3.0.0-py2.py3-none-any.whl.metadata (2.3 kB)
Collecting jsonschema==4.25.0 (from -r backend\requirements.txt (line 318))
  Using cached jsonschema-4.25.0-py3-none-any.whl.metadata (7.7 kB)
Collecting jsonschema-rs==0.29.1 (from -r backend\requirements.txt (line 322))
  Using cached jsonschema_rs-0.29.1-cp312-cp312-win_amd64.whl.metadata (14 kB)
Collecting jsonschema-specifications==2025.4.1 (from -r backend\requirements.txt (line 324))
  Using cached jsonschema_specifications-2025.4.1-py3-none-any.whl.metadata (2.9 kB)
Collecting kombu==5.5.4 (from kombu[redis]==5.5.4->-r backend\requirements.txt (line 
326))
  Using cached kombu-5.5.4-py3-none-any.whl.metadata (3.5 kB)
Collecting kubernetes==33.1.0 (from -r backend\requirements.txt (line 328))
  Using cached kubernetes-33.1.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting langchain==0.3.26 (from -r backend\requirements.txt (line 330))
  Using cached langchain-0.3.26-py3-none-any.whl.metadata (7.8 kB)
Collecting langchain-community==0.3.27 (from -r backend\requirements.txt (line 332))
  Using cached langchain_community-0.3.27-py3-none-any.whl.metadata (2.9 kB)
Collecting langchain-core==0.3.70 (from -r backend\requirements.txt (line 334))
  Using cached langchain_core-0.3.70-py3-none-any.whl.metadata (5.8 kB)
Collecting langchain-google-genai==2.1.8 (from -r backend\requirements.txt (line 346))
  Using cached langchain_google_genai-2.1.8-py3-none-any.whl.metadata (7.0 kB)
Collecting langchain-groq==0.3.6 (from -r backend\requirements.txt (line 348))
  Using cached langchain_groq-0.3.6-py3-none-any.whl.metadata (2.6 kB)
Collecting langchain-openai==0.3.28 (from -r backend\requirements.txt (line 350))
  Using cached langchain_openai-0.3.28-py3-none-any.whl.metadata (2.3 kB)
Collecting langchain-text-splitters==0.3.8 (from -r backend\requirements.txt (line 352))
  Using cached langchain_text_splitters-0.3.8-py3-none-any.whl.metadata (1.9 kB)
Collecting langgraph==0.5.4 (from -r backend\requirements.txt (line 354))
  Using cached langgraph-0.5.4-py3-none-any.whl.metadata (6.8 kB)
Collecting langgraph-api==0.2.98 (from -r backend\requirements.txt (line 359))
  Using cached langgraph_api-0.2.98-py3-none-any.whl.metadata (3.9 kB)
Collecting langgraph-checkpoint==2.1.1 (from -r backend\requirements.txt (line 363))
  Using cached langgraph_checkpoint-2.1.1-py3-none-any.whl.metadata (4.2 kB)
Collecting langgraph-cli==0.3.5 (from langgraph-cli[inmem]==0.3.5->-r backend\requirements.txt (line 369))
  Using cached langgraph_cli-0.3.5-py3-none-any.whl.metadata (3.8 kB)
Collecting langgraph-prebuilt==0.5.2 (from -r backend\requirements.txt (line 371))
  Using cached langgraph_prebuilt-0.5.2-py3-none-any.whl.metadata (4.5 kB)
Collecting langgraph-runtime-inmem==0.6.0 (from -r backend\requirements.txt (line 373))
  Using cached langgraph_runtime_inmem-0.6.0-py3-none-any.whl.metadata (565 bytes)
Collecting langgraph-sdk==0.1.74 (from -r backend\requirements.txt (line 377))
  Using cached langgraph_sdk-0.1.74-py3-none-any.whl.metadata (1.5 kB)
Collecting langsmith==0.4.8 (from -r backend\requirements.txt (line 382))
  Using cached langsmith-0.4.8-py3-none-any.whl.metadata (15 kB)
Collecting lxml==6.0.0 (from -r backend\requirements.txt (line 387))
  Using cached lxml-6.0.0-cp312-cp312-win_amd64.whl.metadata (6.8 kB)
Collecting mako==1.3.10 (from -r backend\requirements.txt (line 391))
  Using cached mako-1.3.10-py3-none-any.whl.metadata (2.9 kB)
Collecting markdown-it-py==3.0.0 (from -r backend\requirements.txt (line 393))
  Using cached markdown_it_py-3.0.0-py3-none-any.whl.metadata (6.9 kB)
Collecting markupsafe==3.0.2 (from -r backend\requirements.txt (line 395))
  Using cached MarkupSafe-3.0.2-cp312-cp312-win_amd64.whl.metadata (4.1 kB)
Collecting mdurl==0.1.2 (from -r backend\requirements.txt (line 399))
  Using cached mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Collecting mmh3==5.1.0 (from -r backend\requirements.txt (line 401))
  Using cached mmh3-5.1.0-cp312-cp312-win_amd64.whl.metadata (16 kB)
Collecting mpmath==1.3.0 (from -r backend\requirements.txt (line 403))
  Using cached mpmath-1.3.0-py3-none-any.whl.metadata (8.6 kB)
Collecting multidict==6.6.3 (from -r backend\requirements.txt (line 405))
  Using cached multidict-6.6.3-cp312-cp312-win_amd64.whl.metadata (5.4 kB)
Collecting mypy==1.17.0 (from -r backend\requirements.txt (line 409))
  Using cached mypy-1.17.0-cp312-cp312-win_amd64.whl.metadata (2.2 kB)
Collecting mypy-extensions==1.1.0 (from -r backend\requirements.txt (line 411))
  Using cached mypy_extensions-1.1.0-py3-none-any.whl.metadata (1.1 kB)
Collecting networkx==3.5 (from -r backend\requirements.txt (line 413))
  Using cached networkx-3.5-py3-none-any.whl.metadata (6.3 kB)
Collecting numpy==2.2.6 (from -r backend\requirements.txt (line 415))
  Using cached numpy-2.2.6-cp312-cp312-win_amd64.whl.metadata (60 kB)
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
ERROR: Ignored the following versions that require a different python version: 0.1.0 
Requires-Python >=3.9.0,<3.12; 0.1.1 Requires-Python >=3.9.0,<3.12; 0.1.2 Requires-Python >=3.9.0,<3.12; 0.1.3 Requires-Python >=3.9.0,<3.12; 0.1.4 Requires-Python >=3.9.0,<3.12; 0.1.5 Requires-Python >=3.9.0,<3.12; 0.1.6 Requires-Python >=3.9.0,<3.12; 0.1.7 Requires-Python >=3.9.0,<3.12; 1.21.2 Requires-Python >=3.7,<3.11; 1.21.3 Requires-Python >=3.7,<3.11; 1.21.4 Requires-Python >=3.7,<3.11; 1.21.5 Requires-Python >=3.7,<3.11; 1.21.6 Requires-Python >=3.7,<3.11; 2.10.0 Requires-Python >=3.6,<3.10; 2.11.0 Requires-Python >=3.6,<3.10; 2.12.0 Requires-Python >=3.6,<3.10; 2.13.0 Requires-Python >=3.6,<3.10; 2.13.1 Requires-Python >=3.6,<3.10; 2.14.0 Requires-Python >=3.6,<3.10; 2.15.0 Requires-Python >=3.6,<3.10; 2.16.0 Requires-Python >=3.6,<3.10; 2.16.1 
Requires-Python >=3.6,<3.10; 2.17.0 Requires-Python >=3.6,<3.10; 2.18.0 Requires-Python >=3.6,<3.10; 2.19.0 Requires-Python >=3.6,<3.10; 2.20.0 Requires-Python >=3.6,<3.10; 2.21.0 Requires-Python >=3.6,<3.10; 2.22.0 Requires-Python >=3.6,<3.10; 2.22.1 Requires-Python >=3.6,<3.10; 2.23.0 Requires-Python >=3.6,<3.10; 2.23.1 Requires-Python 
>=3.6,<3.10; 2.23.2 Requires-Python >=3.6,<3.10; 2.23.3 Requires-Python >=3.6,<3.10; 
2.24.0 Requires-Python >=3.6,<3.10; 2.24.1 Requires-Python >=3.6,<3.10; 2.25.0 Requires-Python >=3.6,<3.10; 2.25.1 Requires-Python >=3.6,<3.10; 2.25.2 Requires-Python >=3.6,<3.10; 2.26.0 Requires-Python >=3.6,<3.10; 2.27.0 Requires-Python >=3.6,<3.10; 2.27.1 Requires-Python >=3.6,<3.10; 2.28.0 Requires-Python >=3.6,<3.10; 2.28.1 Requires-Python >=3.6,<3.10; 2.29.0 Requires-Python >=3.6,<3.10; 2.30.0 Requires-Python >=3.6,<3.11; 2.30.1 Requires-Python >=3.6,<3.11; 2.31.0 Requires-Python >=3.6,<3.11; 2.32.0 Requires-Python >=3.6,<3.11; 2.33.0 Requires-Python >=3.6,<3.11; 2.34.0 Requires-Python >=3.6,<3.11; 2.34.1 Requires-Python >=3.6,<3.11; 2.34.2 Requires-Python >=3.6,<3.11; 2.34.3 Requires-Python >=3.6,<3.11; 2.34.4 Requires-Python >=3.6,<3.11; 2.6.2 Requires-Python >=3.6,<3.9; 2.7.0 Requires-Python >=3.6,<3.10; 2.8.0 Requires-Python >=3.6,<3.10; 2.9.0 Requires-Python >=3.6,<3.10; 3.0.0 Requires-Python >=3.6,<3.11; 3.0.0b1 Requires-Python >=3.6,<3.11; 3.0.1 Requires-Python >=3.6,<3.11; 3.1.0 Requires-Python >=3.6,<3.11; 3.2.0 Requires-Python >=3.6,<3.11; 3.3.0 Requires-Python >=3.7,<3.11; 3.3.1 Requires-Python >=3.7,<3.11; 3.3.2 Requires-Python >=3.7,<3.11; 3.3.3 Requires-Python >=3.7,<3.11; 3.3.5 Requires-Python >=3.7,<3.11; 3.3.6 Requires-Python >=3.7,<3.11
ERROR: Could not find a version that satisfies the requirement nvidia-nccl-cu12==2.21.5 (from versions: 0.0.1.dev5)
ERROR: No matching distribution found for nvidia-nccl-cu12==2.21.5
PYTHONPATH=.;backend;backend\src
Running unit tests only (service-heavy tests skipped). Use -All to include.
Running pytest...

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
______ ERROR collecting backend/tests/integration/test_memory_integration.py _______ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_memory_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\integration\test_memory_integration.py:8: in <module>
    from backend.src.agent.nodes.memory_demo_agent import MemoryDemoAgent
backend\src\agent\nodes\memory_demo_agent.py:5: in <module>
    from ..base_agent import BaseAgent
backend\src\agent\base_agent.py:5: in <module>
    from ..handywriterz_state import HandyWriterzState
E   ModuleNotFoundError: No module named 'backend.src.handywriterz_state'
_________ ERROR collecting backend/tests/integration/test_model_config.py __________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_model_config.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\integration\test_model_config.py:9: in <module>
    from backend.src.api.model_config import (
backend\src\api\model_config.py:14: in <module>
    from ..services.llm_service import get_all_llm_clients
backend\src\services\llm_service.py:5: in <module>
    from langchain_anthropic import ChatAnthropic
E   ModuleNotFoundError: No module named 'langchain_anthropic'
_______ ERROR collecting backend/tests/integration/test_streaming_client.py ________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_streaming_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\integration\test_streaming_client.py:11: in <module>
    from backend.src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
________ ERROR collecting backend/tests/test_chunk_splitter_integration.py _________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_chunk_splitter_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_chunk_splitter_integration.py:7: in <module>
    from src.services.chunk_splitter import ChunkSplitter, SplitConfig, SplitStrategybackend\src\services\chunk_splitter.py:16: in <module>
    import aiofiles
E   ModuleNotFoundError: No module named 'aiofiles'
___________ ERROR collecting backend/tests/test_dissertation_journey.py ____________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_dissertation_journey.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_dissertation_journey.py:6: in <module>
    from src.agent.handywriterz_graph import handywriterz_graph
backend\src\agent\handywriterz_graph.py:12: in <module>
    from .nodes.user_intent import UserIntentNode
backend\src\agent\nodes\user_intent.py:13: in <module>
    from ..base_agent import BaseAgent
backend\src\agent\base_agent.py:5: in <module>
    from ..handywriterz_state import HandyWriterzState
E   ModuleNotFoundError: No module named 'src.handywriterz_state'
____________________ ERROR collecting backend/tests/test_e2e.py ____________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_e2e.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_e2e.py:6: in <module>
    from main import app # Assuming your FastAPI app is in main.py
    ^^^^^^^^^^^^^^^^^^^^
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
______________ ERROR collecting backend/tests/test_evidence_guard.py _______________
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1331: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
backend_env\Lib\site-packages\_pytest\assertion\rewrite.py:186: in exec_module       
    exec(co, module.__dict__)
backend\tests\test_evidence_guard.py:9: in <module>
    with patch('agent.nodes.master_orchestrator.MasterOrchestratorAgent._initialize_ai_providers'):
C:\Python312\Lib\unittest\mock.py:1442: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
C:\Python312\Lib\pkgutil.py:528: in resolve_name
    result = getattr(result, p)
             ^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'agent.nodes' has no attribute 'master_orchestrator'      
__________________ ERROR collecting backend/tests/test_health.py ___________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_health.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_health.py:3: in <module>
    from backend.src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
_______________ ERROR collecting backend/tests/test_memory_writer.py _______________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_memory_writer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_memory_writer.py:5: in <module>
    from agent.nodes.memory_writer import MemoryWriter
backend\src\agent\nodes\memory_writer.py:10: in <module>
    from ...services.memory_integrator import get_memory_integrator
E   ImportError: attempted relative import beyond top-level package
__________________ ERROR collecting backend/tests/test_routing.py __________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_routing.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_routing.py:2: in <module>
    from agent.nodes.loader import load_graph   # helper that reads YAML → Graph     
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\agent\nodes\loader.py:2: in <module>
    from langgraph.graph import Graph
E   ImportError: cannot import name 'Graph' from 'langgraph.graph' (d:\HandyWriterzAi\backend_env\Lib\site-packages\langgraph\graph\__init__.py). Did you mean: 'graph'?  
___________________ ERROR collecting backend/tests/test_utils.py ___________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_utils.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_utils.py:5: in <module>
    from utils.chartify import create_chart_svg
backend\src\utils\chartify.py:2: in <module>
    from playwright.async_api import async_playwright
E   ModuleNotFoundError: No module named 'playwright'
_______________ ERROR collecting backend/tests/test_voice_upload.py ________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_voice_upload.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_voice_upload.py:8: in <module>
    from main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
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
ERROR backend/tests/integration/test_memory_integration.py
ERROR backend/tests/integration/test_model_config.py
ERROR backend/tests/integration/test_streaming_client.py
ERROR backend/tests/test_chunk_splitter_integration.py
ERROR backend/tests/test_dissertation_journey.py
ERROR backend/tests/test_e2e.py
ERROR backend/tests/test_evidence_guard.py - AttributeError: module 'agent.nodes' has no attribute 'master_orchestrator'
ERROR backend/tests/test_health.py
ERROR backend/tests/test_memory_writer.py
ERROR backend/tests/test_routing.py
ERROR backend/tests/test_utils.py
ERROR backend/tests/test_voice_upload.py
!!!!!!!!!!!!!!!!!!!!! Interrupted: 21 errors during collection !!!!!!!!!!!!!!!!!!!!! 
(.venv) PS D:\HandyWriterzAi> .\backend\scripts\test-win.ps1
== HandyWriterzAI Windows test runner ==
Activating venv...
Installing deps from backend\requirements.txt...
Collecting agentic-doc==0.3.1 (from -r backend\requirements.txt (line 7))
  Using cached agentic_doc-0.3.1-py3-none-any.whl.metadata (19 kB)
Collecting aiohappyeyeballs==2.6.1 (from -r backend\requirements.txt (line 9))
  Using cached aiohappyeyeballs-2.6.1-py3-none-any.whl.metadata (5.9 kB)
Collecting aiohttp==3.12.14 (from -r backend\requirements.txt (line 11))
  Using cached aiohttp-3.12.14-cp312-cp312-win_amd64.whl.metadata (7.9 kB)
Collecting aioredis==2.0.1 (from -r backend\requirements.txt (line 13))
  Using cached aioredis-2.0.1-py3-none-any.whl.metadata (15 kB)
Collecting aiosignal==1.4.0 (from -r backend\requirements.txt (line 15))
  Using cached aiosignal-1.4.0-py3-none-any.whl.metadata (3.7 kB)
Collecting alembic==1.16.4 (from -r backend\requirements.txt (line 17))
  Using cached alembic-1.16.4-py3-none-any.whl.metadata (7.3 kB)
Collecting amqp==5.3.1 (from -r backend\requirements.txt (line 19))
  Using cached amqp-5.3.1-py3-none-any.whl.metadata (8.9 kB)
Collecting annotated-types==0.7.0 (from -r backend\requirements.txt (line 21))
  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting anthropic==0.58.2 (from -r backend\requirements.txt (line 23))
  Using cached anthropic-0.58.2-py3-none-any.whl.metadata (27 kB)
Collecting anyio==4.9.0 (from -r backend\requirements.txt (line 25))
  Using cached anyio-4.9.0-py3-none-any.whl.metadata (4.7 kB)
Collecting arxiv==2.2.0 (from -r backend\requirements.txt (line 35))
  Using cached arxiv-2.2.0-py3-none-any.whl.metadata (6.3 kB)
Collecting async-timeout==5.0.1 (from -r backend\requirements.txt (line 37))
  Using cached async_timeout-5.0.1-py3-none-any.whl.metadata (5.1 kB)
Collecting asyncpg==0.30.0 (from -r backend\requirements.txt (line 39))
  Using cached asyncpg-0.30.0-cp312-cp312-win_amd64.whl.metadata (5.2 kB)
Collecting attrs==25.3.0 (from -r backend\requirements.txt (line 41))
  Using cached attrs-25.3.0-py3-none-any.whl.metadata (10 kB)
Collecting azure-core==1.35.0 (from -r backend\requirements.txt (line 46))
  Using cached azure_core-1.35.0-py3-none-any.whl.metadata (44 kB)
Collecting azure-storage-blob==12.26.0 (from -r backend\requirements.txt (line 48))
  Using cached azure_storage_blob-12.26.0-py3-none-any.whl.metadata (26 kB)
Collecting backoff==2.2.1 (from -r backend\requirements.txt (line 50))
  Using cached backoff-2.2.1-py3-none-any.whl.metadata (14 kB)
Collecting bcrypt==4.3.0 (from -r backend\requirements.txt (line 52))
  Using cached bcrypt-4.3.0-cp39-abi3-win_amd64.whl.metadata (10 kB)
Collecting beautifulsoup4==4.13.4 (from -r backend\requirements.txt (line 57))
  Using cached beautifulsoup4-4.13.4-py3-none-any.whl.metadata (3.8 kB)
Collecting billiard==4.2.1 (from -r backend\requirements.txt (line 59))
  Using cached billiard-4.2.1-py3-none-any.whl.metadata (4.4 kB)
Collecting blockbuster==1.5.25 (from -r backend\requirements.txt (line 61))
  Using cached blockbuster-1.5.25-py3-none-any.whl.metadata (10 kB)
Collecting boto3==1.39.10 (from -r backend\requirements.txt (line 63))
  Using cached boto3-1.39.10-py3-none-any.whl.metadata (6.7 kB)
Collecting botocore==1.39.10 (from -r backend\requirements.txt (line 67))
  Using cached botocore-1.39.10-py3-none-any.whl.metadata (5.7 kB)
Collecting brotli==1.1.0 (from -r backend\requirements.txt (line 71))
  Using cached Brotli-1.1.0-cp312-cp312-win_amd64.whl.metadata (5.6 kB)
Collecting build==1.2.2.post1 (from -r backend\requirements.txt (line 73))
  Using cached build-1.2.2.post1-py3-none-any.whl.metadata (6.5 kB)
Collecting cachetools==5.5.2 (from -r backend\requirements.txt (line 75))
  Using cached cachetools-5.5.2-py3-none-any.whl.metadata (5.4 kB)
Collecting celery==5.5.3 (from celery[redis]==5.5.3->-r backend\requirements.txt (line 77))
  Using cached celery-5.5.3-py3-none-any.whl.metadata (22 kB)
Collecting certifi==2025.7.14 (from -r backend\requirements.txt (line 79))
  Using cached certifi-2025.7.14-py3-none-any.whl.metadata (2.4 kB)
Collecting cffi==1.17.1 (from -r backend\requirements.txt (line 85))
  Using cached cffi-1.17.1-cp312-cp312-win_amd64.whl.metadata (1.6 kB)
Collecting charset-normalizer==3.4.2 (from -r backend\requirements.txt (line 87))
  Using cached charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl.metadata (36 kB)
Collecting chromadb==1.0.15 (from -r backend\requirements.txt (line 89))
  Using cached chromadb-1.0.15-cp39-abi3-win_amd64.whl.metadata (7.1 kB)
Collecting click==8.2.1 (from -r backend\requirements.txt (line 91))
  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting click-didyoumean==0.3.1 (from -r backend\requirements.txt (line 100))
  Using cached click_didyoumean-0.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting click-plugins==1.1.1.2 (from -r backend\requirements.txt (line 102))
  Using cached click_plugins-1.1.1.2-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting click-repl==0.3.0 (from -r backend\requirements.txt (line 104))
  Using cached click_repl-0.3.0-py3-none-any.whl.metadata (3.6 kB)
Collecting cloudpickle==3.1.1 (from -r backend\requirements.txt (line 106))
  Using cached cloudpickle-3.1.1-py3-none-any.whl.metadata (7.1 kB)
Collecting coloredlogs==15.0.1 (from -r backend\requirements.txt (line 108))
  Using cached coloredlogs-15.0.1-py2.py3-none-any.whl.metadata (12 kB)
Collecting cryptography==44.0.3 (from -r backend\requirements.txt (line 110))
  Using cached cryptography-44.0.3-cp39-abi3-win_amd64.whl.metadata (5.7 kB)
Collecting deprecation==2.1.0 (from -r backend\requirements.txt (line 116))
  Using cached deprecation-2.1.0-py2.py3-none-any.whl.metadata (4.6 kB)
Collecting distro==1.9.0 (from -r backend\requirements.txt (line 120))
  Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
Collecting docstring-parser==0.17.0 (from -r backend\requirements.txt (line 126))
  Using cached docstring_parser-0.17.0-py3-none-any.whl.metadata (3.5 kB)
Collecting docx2txt==0.9 (from -r backend\requirements.txt (line 128))
  Using cached docx2txt-0.9-py3-none-any.whl.metadata (529 bytes)
Collecting durationpy==0.10 (from -r backend\requirements.txt (line 130))
  Using cached durationpy-0.10-py3-none-any.whl.metadata (340 bytes)
Collecting ecdsa==0.19.1 (from -r backend\requirements.txt (line 132))
  Using cached ecdsa-0.19.1-py2.py3-none-any.whl.metadata (29 kB)
Collecting et-xmlfile==2.0.0 (from -r backend\requirements.txt (line 134))
  Using cached et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
Collecting fastapi==0.116.1 (from -r backend\requirements.txt (line 136))
  Using cached fastapi-0.116.1-py3-none-any.whl.metadata (28 kB)
Collecting feedparser==6.0.11 (from -r backend\requirements.txt (line 138))
  Using cached feedparser-6.0.11-py3-none-any.whl.metadata (2.4 kB)
Collecting filelock==3.18.0 (from -r backend\requirements.txt (line 142))
  Using cached filelock-3.18.0-py3-none-any.whl.metadata (2.9 kB)
Collecting filetype==1.2.0 (from -r backend\requirements.txt (line 148))
  Using cached filetype-1.2.0-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting flatbuffers==25.2.10 (from -r backend\requirements.txt (line 150))
  Using cached flatbuffers-25.2.10-py2.py3-none-any.whl.metadata (875 bytes)
Collecting forbiddenfruit==0.1.4 (from -r backend\requirements.txt (line 152))
  Using cached forbiddenfruit-0.1.4-py3-none-any.whl
Collecting fpdf==1.7.2 (from -r backend\requirements.txt (line 154))
  Using cached fpdf-1.7.2-py2.py3-none-any.whl
Collecting frozenlist==1.7.0 (from -r backend\requirements.txt (line 156))
  Using cached frozenlist-1.7.0-cp312-cp312-win_amd64.whl.metadata (19 kB)
Collecting fsspec==2025.7.0 (from -r backend\requirements.txt (line 160))
  Using cached fsspec-2025.7.0-py3-none-any.whl.metadata (12 kB)
Collecting google-ai-generativelanguage==0.6.18 (from -r backend\requirements.txt (line 164))
  Using cached google_ai_generativelanguage-0.6.18-py3-none-any.whl.metadata (9.8 kB)Collecting google-api-core==2.25.1 (from google-api-core[grpc]==2.25.1->-r backend\requirements.txt (line 166))
  Using cached google_api_core-2.25.1-py3-none-any.whl.metadata (3.0 kB)
Collecting google-api-python-client==2.176.0 (from -r backend\requirements.txt (line 
175))
  Using cached google_api_python_client-2.176.0-py3-none-any.whl.metadata (7.0 kB)
Collecting google-auth==2.40.3 (from -r backend\requirements.txt (line 177))
  Using cached google_auth-2.40.3-py2.py3-none-any.whl.metadata (6.2 kB)
Collecting google-auth-httplib2==0.2.0 (from -r backend\requirements.txt (line 192))
  Using cached google_auth_httplib2-0.2.0-py2.py3-none-any.whl.metadata (2.2 kB)
Collecting google-auth-oauthlib==1.2.2 (from -r backend\requirements.txt (line 194))
  Using cached google_auth_oauthlib-1.2.2-py3-none-any.whl.metadata (2.7 kB)
Collecting google-cloud-aiplatform==1.104.0 (from -r backend\requirements.txt (line 196))
  Using cached google_cloud_aiplatform-1.104.0-py2.py3-none-any.whl.metadata (38 kB)
Collecting google-cloud-bigquery==3.35.0 (from -r backend\requirements.txt (line 198))
  Using cached google_cloud_bigquery-3.35.0-py3-none-any.whl.metadata (8.0 kB)
Collecting google-cloud-core==2.4.3 (from -r backend\requirements.txt (line 200))
  Using cached google_cloud_core-2.4.3-py2.py3-none-any.whl.metadata (2.7 kB)
Collecting google-cloud-resource-manager==1.14.2 (from -r backend\requirements.txt (line 204))
  Using cached google_cloud_resource_manager-1.14.2-py3-none-any.whl.metadata (9.6 kB)
Collecting google-cloud-storage==2.19.0 (from -r backend\requirements.txt (line 206))  Using cached google_cloud_storage-2.19.0-py2.py3-none-any.whl.metadata (9.1 kB)
Collecting google-crc32c==1.7.1 (from -r backend\requirements.txt (line 208))
  Using cached google_crc32c-1.7.1-cp312-cp312-win_amd64.whl.metadata (2.4 kB)
Collecting google-genai==1.26.0 (from -r backend\requirements.txt (line 212))
  Using cached google_genai-1.26.0-py3-none-any.whl.metadata (42 kB)
Collecting google-resumable-media==2.7.2 (from -r backend\requirements.txt (line 216))
  Using cached google_resumable_media-2.7.2-py2.py3-none-any.whl.metadata (2.2 kB)
Collecting googleapis-common-protos==1.70.0 (from googleapis-common-protos[grpc]==1.70.0->-r backend\requirements.txt (line 220))
  Using cached googleapis_common_protos-1.70.0-py3-none-any.whl.metadata (9.3 kB)
Collecting gotrue==2.12.3 (from -r backend\requirements.txt (line 226))
  Using cached gotrue-2.12.3-py3-none-any.whl.metadata (6.5 kB)
Collecting greenlet==3.2.3 (from -r backend\requirements.txt (line 228))
  Using cached greenlet-3.2.3-cp312-cp312-win_amd64.whl.metadata (4.2 kB)
Collecting groq==0.30.0 (from -r backend\requirements.txt (line 230))
  Using cached groq-0.30.0-py3-none-any.whl.metadata (16 kB)
Collecting grpc-google-iam-v1==0.14.2 (from -r backend\requirements.txt (line 232))
  Using cached grpc_google_iam_v1-0.14.2-py3-none-any.whl.metadata (9.1 kB)
Collecting grpcio==1.73.1 (from -r backend\requirements.txt (line 234))
  Using cached grpcio-1.73.1-cp312-cp312-win_amd64.whl.metadata (4.0 kB)
Collecting grpcio-status==1.73.1 (from -r backend\requirements.txt (line 242))
  Using cached grpcio_status-1.73.1-py3-none-any.whl.metadata (1.1 kB)
Collecting h11==0.16.0 (from -r backend\requirements.txt (line 244))
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting h2==4.2.0 (from -r backend\requirements.txt (line 248))
  Using cached h2-4.2.0-py3-none-any.whl.metadata (5.1 kB)
Collecting hf-xet==1.1.5 (from -r backend\requirements.txt (line 250))
  Using cached hf_xet-1.1.5-cp37-abi3-win_amd64.whl.metadata (883 bytes)
Collecting hpack==4.1.0 (from -r backend\requirements.txt (line 252))
  Using cached hpack-4.1.0-py3-none-any.whl.metadata (4.6 kB)
Collecting httpcore==1.0.9 (from -r backend\requirements.txt (line 254))
  Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Collecting httplib2==0.22.0 (from -r backend\requirements.txt (line 256))
  Using cached httplib2-0.22.0-py3-none-any.whl.metadata (2.6 kB)
Collecting httptools==0.6.4 (from -r backend\requirements.txt (line 260))
  Using cached httptools-0.6.4-cp312-cp312-win_amd64.whl.metadata (3.7 kB)
Collecting httpx==0.28.1 (from httpx[http2]==0.28.1->-r backend\requirements.txt (line 262))
  Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Collecting huggingface-hub==0.33.4 (from -r backend\requirements.txt (line 279))
  Using cached huggingface_hub-0.33.4-py3-none-any.whl.metadata (14 kB)
Collecting humanfriendly==10.0 (from -r backend\requirements.txt (line 284))
  Using cached humanfriendly-10.0-py2.py3-none-any.whl.metadata (9.2 kB)
Collecting hyperframe==6.1.0 (from -r backend\requirements.txt (line 286))
  Using cached hyperframe-6.1.0-py3-none-any.whl.metadata (4.3 kB)
Collecting idna==3.10 (from -r backend\requirements.txt (line 288))
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting importlib-metadata==8.7.0 (from -r backend\requirements.txt (line 294))
  Using cached importlib_metadata-8.7.0-py3-none-any.whl.metadata (4.8 kB)
Collecting importlib-resources==6.5.2 (from -r backend\requirements.txt (line 296))
  Using cached importlib_resources-6.5.2-py3-none-any.whl.metadata (3.9 kB)
Collecting iniconfig==2.1.0 (from -r backend\requirements.txt (line 298))
  Using cached iniconfig-2.1.0-py3-none-any.whl.metadata (2.7 kB)
Collecting isodate==0.7.2 (from -r backend\requirements.txt (line 300))
  Using cached isodate-0.7.2-py3-none-any.whl.metadata (11 kB)
Collecting jinja2==3.1.6 (from -r backend\requirements.txt (line 302))
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting jiter==0.10.0 (from -r backend\requirements.txt (line 304))
  Using cached jiter-0.10.0-cp312-cp312-win_amd64.whl.metadata (5.3 kB)
Collecting jmespath==1.0.1 (from -r backend\requirements.txt (line 308))
  Using cached jmespath-1.0.1-py3-none-any.whl.metadata (7.6 kB)
Collecting joblib==1.5.1 (from -r backend\requirements.txt (line 312))
  Using cached joblib-1.5.1-py3-none-any.whl.metadata (5.6 kB)
Collecting jsonpatch==1.33 (from -r backend\requirements.txt (line 314))
  Using cached jsonpatch-1.33-py2.py3-none-any.whl.metadata (3.0 kB)
Collecting jsonpointer==3.0.0 (from -r backend\requirements.txt (line 316))
  Using cached jsonpointer-3.0.0-py2.py3-none-any.whl.metadata (2.3 kB)
Collecting jsonschema==4.25.0 (from -r backend\requirements.txt (line 318))
  Using cached jsonschema-4.25.0-py3-none-any.whl.metadata (7.7 kB)
Collecting jsonschema-rs==0.29.1 (from -r backend\requirements.txt (line 322))
  Using cached jsonschema_rs-0.29.1-cp312-cp312-win_amd64.whl.metadata (14 kB)
Collecting jsonschema-specifications==2025.4.1 (from -r backend\requirements.txt (line 324))
  Using cached jsonschema_specifications-2025.4.1-py3-none-any.whl.metadata (2.9 kB)
Collecting kombu==5.5.4 (from kombu[redis]==5.5.4->-r backend\requirements.txt (line 
326))
  Using cached kombu-5.5.4-py3-none-any.whl.metadata (3.5 kB)
Collecting kubernetes==33.1.0 (from -r backend\requirements.txt (line 328))
  Using cached kubernetes-33.1.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting langchain==0.3.26 (from -r backend\requirements.txt (line 330))
  Using cached langchain-0.3.26-py3-none-any.whl.metadata (7.8 kB)
Collecting langchain-community==0.3.27 (from -r backend\requirements.txt (line 332))
  Using cached langchain_community-0.3.27-py3-none-any.whl.metadata (2.9 kB)
Collecting langchain-core==0.3.70 (from -r backend\requirements.txt (line 334))
  Using cached langchain_core-0.3.70-py3-none-any.whl.metadata (5.8 kB)
Collecting langchain-google-genai==2.1.8 (from -r backend\requirements.txt (line 346))
  Using cached langchain_google_genai-2.1.8-py3-none-any.whl.metadata (7.0 kB)
Collecting langchain-groq==0.3.6 (from -r backend\requirements.txt (line 348))
  Using cached langchain_groq-0.3.6-py3-none-any.whl.metadata (2.6 kB)
Collecting langchain-openai==0.3.28 (from -r backend\requirements.txt (line 350))
  Using cached langchain_openai-0.3.28-py3-none-any.whl.metadata (2.3 kB)
Collecting langchain-text-splitters==0.3.8 (from -r backend\requirements.txt (line 352))
  Using cached langchain_text_splitters-0.3.8-py3-none-any.whl.metadata (1.9 kB)
Collecting langgraph==0.5.4 (from -r backend\requirements.txt (line 354))
  Using cached langgraph-0.5.4-py3-none-any.whl.metadata (6.8 kB)
Collecting langgraph-api==0.2.98 (from -r backend\requirements.txt (line 359))
  Using cached langgraph_api-0.2.98-py3-none-any.whl.metadata (3.9 kB)
Collecting langgraph-checkpoint==2.1.1 (from -r backend\requirements.txt (line 363))
  Using cached langgraph_checkpoint-2.1.1-py3-none-any.whl.metadata (4.2 kB)
Collecting langgraph-cli==0.3.5 (from langgraph-cli[inmem]==0.3.5->-r backend\requirements.txt (line 369))
  Using cached langgraph_cli-0.3.5-py3-none-any.whl.metadata (3.8 kB)
Collecting langgraph-prebuilt==0.5.2 (from -r backend\requirements.txt (line 371))
  Using cached langgraph_prebuilt-0.5.2-py3-none-any.whl.metadata (4.5 kB)
Collecting langgraph-runtime-inmem==0.6.0 (from -r backend\requirements.txt (line 373))
  Using cached langgraph_runtime_inmem-0.6.0-py3-none-any.whl.metadata (565 bytes)
Collecting langgraph-sdk==0.1.74 (from -r backend\requirements.txt (line 377))
  Using cached langgraph_sdk-0.1.74-py3-none-any.whl.metadata (1.5 kB)
Collecting langsmith==0.4.8 (from -r backend\requirements.txt (line 382))
  Using cached langsmith-0.4.8-py3-none-any.whl.metadata (15 kB)
Collecting lxml==6.0.0 (from -r backend\requirements.txt (line 387))
  Using cached lxml-6.0.0-cp312-cp312-win_amd64.whl.metadata (6.8 kB)
Collecting mako==1.3.10 (from -r backend\requirements.txt (line 391))
  Using cached mako-1.3.10-py3-none-any.whl.metadata (2.9 kB)
Collecting markdown-it-py==3.0.0 (from -r backend\requirements.txt (line 393))
  Using cached markdown_it_py-3.0.0-py3-none-any.whl.metadata (6.9 kB)
Collecting markupsafe==3.0.2 (from -r backend\requirements.txt (line 395))
  Using cached MarkupSafe-3.0.2-cp312-cp312-win_amd64.whl.metadata (4.1 kB)
Collecting mdurl==0.1.2 (from -r backend\requirements.txt (line 399))
  Using cached mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Collecting mmh3==5.1.0 (from -r backend\requirements.txt (line 401))
  Using cached mmh3-5.1.0-cp312-cp312-win_amd64.whl.metadata (16 kB)
Collecting mpmath==1.3.0 (from -r backend\requirements.txt (line 403))
  Using cached mpmath-1.3.0-py3-none-any.whl.metadata (8.6 kB)
Collecting multidict==6.6.3 (from -r backend\requirements.txt (line 405))
  Using cached multidict-6.6.3-cp312-cp312-win_amd64.whl.metadata (5.4 kB)
Collecting mypy==1.17.0 (from -r backend\requirements.txt (line 409))
  Using cached mypy-1.17.0-cp312-cp312-win_amd64.whl.metadata (2.2 kB)
Collecting mypy-extensions==1.1.0 (from -r backend\requirements.txt (line 411))
  Using cached mypy_extensions-1.1.0-py3-none-any.whl.metadata (1.1 kB)
Collecting networkx==3.5 (from -r backend\requirements.txt (line 413))
  Using cached networkx-3.5-py3-none-any.whl.metadata (6.3 kB)
Collecting numpy==2.2.6 (from -r backend\requirements.txt (line 415))
  Using cached numpy-2.2.6-cp312-cp312-win_amd64.whl.metadata (60 kB)
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
ERROR: Ignored the following versions that require a different python version: 0.1.0 
Requires-Python >=3.9.0,<3.12; 0.1.1 Requires-Python >=3.9.0,<3.12; 0.1.2 Requires-Python >=3.9.0,<3.12; 0.1.3 Requires-Python >=3.9.0,<3.12; 0.1.4 Requires-Python >=3.9.0,<3.12; 0.1.5 Requires-Python >=3.9.0,<3.12; 0.1.6 Requires-Python >=3.9.0,<3.12; 0.1.7 Requires-Python >=3.9.0,<3.12; 1.21.2 Requires-Python >=3.7,<3.11; 1.21.3 Requires-Python >=3.7,<3.11; 1.21.4 Requires-Python >=3.7,<3.11; 1.21.5 Requires-Python >=3.7,<3.11; 1.21.6 Requires-Python >=3.7,<3.11; 2.10.0 Requires-Python >=3.6,<3.10; 2.11.0 Requires-Python >=3.6,<3.10; 2.12.0 Requires-Python >=3.6,<3.10; 2.13.0 Requires-Python >=3.6,<3.10; 2.13.1 Requires-Python >=3.6,<3.10; 2.14.0 Requires-Python >=3.6,<3.10; 2.15.0 Requires-Python >=3.6,<3.10; 2.16.0 Requires-Python >=3.6,<3.10; 2.16.1 
Requires-Python >=3.6,<3.10; 2.17.0 Requires-Python >=3.6,<3.10; 2.18.0 Requires-Python >=3.6,<3.10; 2.19.0 Requires-Python >=3.6,<3.10; 2.20.0 Requires-Python >=3.6,<3.10; 2.21.0 Requires-Python >=3.6,<3.10; 2.22.0 Requires-Python >=3.6,<3.10; 2.22.1 Requires-Python >=3.6,<3.10; 2.23.0 Requires-Python >=3.6,<3.10; 2.23.1 Requires-Python 
>=3.6,<3.10; 2.23.2 Requires-Python >=3.6,<3.10; 2.23.3 Requires-Python >=3.6,<3.10; 
2.24.0 Requires-Python >=3.6,<3.10; 2.24.1 Requires-Python >=3.6,<3.10; 2.25.0 Requires-Python >=3.6,<3.10; 2.25.1 Requires-Python >=3.6,<3.10; 2.25.2 Requires-Python >=3.6,<3.10; 2.26.0 Requires-Python >=3.6,<3.10; 2.27.0 Requires-Python >=3.6,<3.10; 2.27.1 Requires-Python >=3.6,<3.10; 2.28.0 Requires-Python >=3.6,<3.10; 2.28.1 Requires-Python >=3.6,<3.10; 2.29.0 Requires-Python >=3.6,<3.10; 2.30.0 Requires-Python >=3.6,<3.11; 2.30.1 Requires-Python >=3.6,<3.11; 2.31.0 Requires-Python >=3.6,<3.11; 2.32.0 Requires-Python >=3.6,<3.11; 2.33.0 Requires-Python >=3.6,<3.11; 2.34.0 Requires-Python >=3.6,<3.11; 2.34.1 Requires-Python >=3.6,<3.11; 2.34.2 Requires-Python >=3.6,<3.11; 2.34.3 Requires-Python >=3.6,<3.11; 2.34.4 Requires-Python >=3.6,<3.11; 2.6.2 Requires-Python >=3.6,<3.9; 2.7.0 Requires-Python >=3.6,<3.10; 2.8.0 Requires-Python >=3.6,<3.10; 2.9.0 Requires-Python >=3.6,<3.10; 3.0.0 Requires-Python >=3.6,<3.11; 3.0.0b1 Requires-Python >=3.6,<3.11; 3.0.1 Requires-Python >=3.6,<3.11; 3.1.0 Requires-Python >=3.6,<3.11; 3.2.0 Requires-Python >=3.6,<3.11; 3.3.0 Requires-Python >=3.7,<3.11; 3.3.1 Requires-Python >=3.7,<3.11; 3.3.2 Requires-Python >=3.7,<3.11; 3.3.3 Requires-Python >=3.7,<3.11; 3.3.5 Requires-Python >=3.7,<3.11; 3.3.6 Requires-Python >=3.7,<3.11
ERROR: Could not find a version that satisfies the requirement nvidia-nccl-cu12==2.21.5 (from versions: 0.0.1.dev5)
ERROR: No matching distribution found for nvidia-nccl-cu12==2.21.5
PYTHONPATH=.;backend;backend\src
Running unit tests only (service-heavy tests skipped). Use -All to include.
Running pytest...

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
______ ERROR collecting backend/tests/integration/test_memory_integration.py _______ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_memory_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\integration\test_memory_integration.py:8: in <module>
    from backend.src.agent.nodes.memory_demo_agent import MemoryDemoAgent
backend\src\agent\nodes\memory_demo_agent.py:5: in <module>
    from ..base_agent import BaseAgent
backend\src\agent\base_agent.py:5: in <module>
    from ..handywriterz_state import HandyWriterzState
E   ModuleNotFoundError: No module named 'backend.src.handywriterz_state'
_________ ERROR collecting backend/tests/integration/test_model_config.py __________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_model_config.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\integration\test_model_config.py:9: in <module>
    from backend.src.api.model_config import (
backend\src\api\model_config.py:14: in <module>
    from ..services.llm_service import get_all_llm_clients
backend\src\services\llm_service.py:5: in <module>
    from langchain_anthropic import ChatAnthropic
E   ModuleNotFoundError: No module named 'langchain_anthropic'
_______ ERROR collecting backend/tests/integration/test_streaming_client.py ________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_streaming_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\integration\test_streaming_client.py:11: in <module>
    from backend.src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
________ ERROR collecting backend/tests/test_chunk_splitter_integration.py _________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_chunk_splitter_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_chunk_splitter_integration.py:7: in <module>
    from src.services.chunk_splitter import ChunkSplitter, SplitConfig, SplitStrategybackend\src\services\chunk_splitter.py:16: in <module>
    import aiofiles
E   ModuleNotFoundError: No module named 'aiofiles'
___________ ERROR collecting backend/tests/test_dissertation_journey.py ____________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_dissertation_journey.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_dissertation_journey.py:6: in <module>
    from src.agent.handywriterz_graph import handywriterz_graph
backend\src\agent\handywriterz_graph.py:12: in <module>
    from .nodes.user_intent import UserIntentNode
backend\src\agent\nodes\user_intent.py:13: in <module>
    from ..base_agent import BaseAgent
backend\src\agent\base_agent.py:5: in <module>
    from ..handywriterz_state import HandyWriterzState
E   ModuleNotFoundError: No module named 'src.handywriterz_state'
____________________ ERROR collecting backend/tests/test_e2e.py ____________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_e2e.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_e2e.py:6: in <module>
    from main import app # Assuming your FastAPI app is in main.py
    ^^^^^^^^^^^^^^^^^^^^
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
______________ ERROR collecting backend/tests/test_evidence_guard.py _______________ 
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1331: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
backend_env\Lib\site-packages\_pytest\assertion\rewrite.py:186: in exec_module       
    exec(co, module.__dict__)
backend\tests\test_evidence_guard.py:9: in <module>
    with patch('agent.nodes.master_orchestrator.MasterOrchestratorAgent._initialize_ai_providers'):
C:\Python312\Lib\unittest\mock.py:1442: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
C:\Python312\Lib\pkgutil.py:528: in resolve_name
    result = getattr(result, p)
             ^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'agent.nodes' has no attribute 'master_orchestrator'      
__________________ ERROR collecting backend/tests/test_health.py ___________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_health.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_health.py:3: in <module>
    from backend.src.main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
_______________ ERROR collecting backend/tests/test_memory_writer.py _______________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_memory_writer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_memory_writer.py:5: in <module>
    from agent.nodes.memory_writer import MemoryWriter
backend\src\agent\nodes\memory_writer.py:10: in <module>
    from ...services.memory_integrator import get_memory_integrator
E   ImportError: attempted relative import beyond top-level package
__________________ ERROR collecting backend/tests/test_routing.py __________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_routing.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_routing.py:2: in <module>
    from agent.nodes.loader import load_graph   # helper that reads YAML → Graph     
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\src\agent\nodes\loader.py:2: in <module>
    from langgraph.graph import Graph
E   ImportError: cannot import name 'Graph' from 'langgraph.graph' (d:\HandyWriterzAi\backend_env\Lib\site-packages\langgraph\graph\__init__.py). Did you mean: 'graph'?  
___________________ ERROR collecting backend/tests/test_utils.py ___________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_utils.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_utils.py:5: in <module>
    from utils.chartify import create_chart_svg
backend\src\utils\chartify.py:2: in <module>
    from playwright.async_api import async_playwright
E   ModuleNotFoundError: No module named 'playwright'
_______________ ERROR collecting backend/tests/test_voice_upload.py ________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_voice_upload.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend\tests\test_voice_upload.py:8: in <module>
    from main import app
backend\src\main.py:82: in <module>
    from src.db.database import (
backend\src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
backend\src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
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
ERROR backend/tests/integration/test_memory_integration.py
ERROR backend/tests/integration/test_model_config.py
ERROR backend/tests/integration/test_streaming_client.py
ERROR backend/tests/test_chunk_splitter_integration.py
ERROR backend/tests/test_dissertation_journey.py
ERROR backend/tests/test_e2e.py
ERROR backend/tests/test_evidence_guard.py - AttributeError: module 'agent.nodes' has no attribute 'master_orchestrator'
ERROR backend/tests/test_health.py
ERROR backend/tests/test_memory_writer.py
ERROR backend/tests/test_routing.py
ERROR backend/tests/test_utils.py
ERROR backend/tests/test_voice_upload.py
!!!!!!!!!!!!!!!!!!!!! Interrupted: 21 errors during collection !!!!!!!!!!!!!!!!!!!!! 
(.venv) PS D:\HandyWriterzAi> python -m pip install -r backend\requirements.txt
Collecting agentic-doc==0.3.1 (from -r backend\requirements.txt (line 7))
  Using cached agentic_doc-0.3.1-py3-none-any.whl.metadata (19 kB)
Collecting aiohappyeyeballs==2.6.1 (from -r backend\requirements.txt (line 9))
  Using cached aiohappyeyeballs-2.6.1-py3-none-any.whl.metadata (5.9 kB)
Collecting aiohttp==3.12.14 (from -r backend\requirements.txt (line 11))
  Using cached aiohttp-3.12.14-cp312-cp312-win_amd64.whl.metadata (7.9 kB)
Collecting aioredis==2.0.1 (from -r backend\requirements.txt (line 13))
  Using cached aioredis-2.0.1-py3-none-any.whl.metadata (15 kB)
Collecting aiosignal==1.4.0 (from -r backend\requirements.txt (line 15))
  Using cached aiosignal-1.4.0-py3-none-any.whl.metadata (3.7 kB)
Collecting alembic==1.16.4 (from -r backend\requirements.txt (line 17))
  Using cached alembic-1.16.4-py3-none-any.whl.metadata (7.3 kB)
Collecting amqp==5.3.1 (from -r backend\requirements.txt (line 19))
  Using cached amqp-5.3.1-py3-none-any.whl.metadata (8.9 kB)
Collecting annotated-types==0.7.0 (from -r backend\requirements.txt (line 21))
  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting anthropic==0.58.2 (from -r backend\requirements.txt (line 23))
  Using cached anthropic-0.58.2-py3-none-any.whl.metadata (27 kB)
Collecting anyio==4.9.0 (from -r backend\requirements.txt (line 25))
  Using cached anyio-4.9.0-py3-none-any.whl.metadata (4.7 kB)
Collecting arxiv==2.2.0 (from -r backend\requirements.txt (line 35))
  Using cached arxiv-2.2.0-py3-none-any.whl.metadata (6.3 kB)
Collecting async-timeout==5.0.1 (from -r backend\requirements.txt (line 37))
  Using cached async_timeout-5.0.1-py3-none-any.whl.metadata (5.1 kB)
Collecting asyncpg==0.30.0 (from -r backend\requirements.txt (line 39))
  Using cached asyncpg-0.30.0-cp312-cp312-win_amd64.whl.metadata (5.2 kB)
Collecting attrs==25.3.0 (from -r backend\requirements.txt (line 41))
  Using cached attrs-25.3.0-py3-none-any.whl.metadata (10 kB)
Collecting azure-core==1.35.0 (from -r backend\requirements.txt (line 46))
  Using cached azure_core-1.35.0-py3-none-any.whl.metadata (44 kB)
Collecting azure-storage-blob==12.26.0 (from -r backend\requirements.txt (line 48))
  Using cached azure_storage_blob-12.26.0-py3-none-any.whl.metadata (26 kB)
Collecting backoff==2.2.1 (from -r backend\requirements.txt (line 50))
  Using cached backoff-2.2.1-py3-none-any.whl.metadata (14 kB)
Collecting bcrypt==4.3.0 (from -r backend\requirements.txt (line 52))
  Using cached bcrypt-4.3.0-cp39-abi3-win_amd64.whl.metadata (10 kB)
Collecting beautifulsoup4==4.13.4 (from -r backend\requirements.txt (line 57))
  Using cached beautifulsoup4-4.13.4-py3-none-any.whl.metadata (3.8 kB)
Collecting billiard==4.2.1 (from -r backend\requirements.txt (line 59))
  Using cached billiard-4.2.1-py3-none-any.whl.metadata (4.4 kB)
Collecting blockbuster==1.5.25 (from -r backend\requirements.txt (line 61))
  Using cached blockbuster-1.5.25-py3-none-any.whl.metadata (10 kB)
Collecting boto3==1.39.10 (from -r backend\requirements.txt (line 63))
  Using cached boto3-1.39.10-py3-none-any.whl.metadata (6.7 kB)
Collecting botocore==1.39.10 (from -r backend\requirements.txt (line 67))
  Using cached botocore-1.39.10-py3-none-any.whl.metadata (5.7 kB)
Collecting brotli==1.1.0 (from -r backend\requirements.txt (line 71))
  Using cached Brotli-1.1.0-cp312-cp312-win_amd64.whl.metadata (5.6 kB)
Collecting build==1.2.2.post1 (from -r backend\requirements.txt (line 73))
  Using cached build-1.2.2.post1-py3-none-any.whl.metadata (6.5 kB)
Collecting cachetools==5.5.2 (from -r backend\requirements.txt (line 75))
  Using cached cachetools-5.5.2-py3-none-any.whl.metadata (5.4 kB)
Collecting celery==5.5.3 (from celery[redis]==5.5.3->-r backend\requirements.txt (line 77))
  Using cached celery-5.5.3-py3-none-any.whl.metadata (22 kB)
Collecting certifi==2025.7.14 (from -r backend\requirements.txt (line 79))
  Using cached certifi-2025.7.14-py3-none-any.whl.metadata (2.4 kB)
Collecting cffi==1.17.1 (from -r backend\requirements.txt (line 85))
  Using cached cffi-1.17.1-cp312-cp312-win_amd64.whl.metadata (1.6 kB)
Collecting charset-normalizer==3.4.2 (from -r backend\requirements.txt (line 87))
  Using cached charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl.metadata (36 kB)
Collecting chromadb==1.0.15 (from -r backend\requirements.txt (line 89))
  Using cached chromadb-1.0.15-cp39-abi3-win_amd64.whl.metadata (7.1 kB)
Collecting click==8.2.1 (from -r backend\requirements.txt (line 91))
  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting click-didyoumean==0.3.1 (from -r backend\requirements.txt (line 100))
  Using cached click_didyoumean-0.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting click-plugins==1.1.1.2 (from -r backend\requirements.txt (line 102))
  Using cached click_plugins-1.1.1.2-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting click-repl==0.3.0 (from -r backend\requirements.txt (line 104))
  Using cached click_repl-0.3.0-py3-none-any.whl.metadata (3.6 kB)
Collecting cloudpickle==3.1.1 (from -r backend\requirements.txt (line 106))
  Using cached cloudpickle-3.1.1-py3-none-any.whl.metadata (7.1 kB)
Collecting coloredlogs==15.0.1 (from -r backend\requirements.txt (line 108))
  Using cached coloredlogs-15.0.1-py2.py3-none-any.whl.metadata (12 kB)
Collecting cryptography==44.0.3 (from -r backend\requirements.txt (line 110))
  Using cached cryptography-44.0.3-cp39-abi3-win_amd64.whl.metadata (5.7 kB)
Collecting deprecation==2.1.0 (from -r backend\requirements.txt (line 116))
  Using cached deprecation-2.1.0-py2.py3-none-any.whl.metadata (4.6 kB)
Collecting distro==1.9.0 (from -r backend\requirements.txt (line 120))
  Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
Collecting docstring-parser==0.17.0 (from -r backend\requirements.txt (line 126))
  Using cached docstring_parser-0.17.0-py3-none-any.whl.metadata (3.5 kB)
Collecting docx2txt==0.9 (from -r backend\requirements.txt (line 128))
  Using cached docx2txt-0.9-py3-none-any.whl.metadata (529 bytes)
Collecting durationpy==0.10 (from -r backend\requirements.txt (line 130))
  Using cached durationpy-0.10-py3-none-any.whl.metadata (340 bytes)
Collecting ecdsa==0.19.1 (from -r backend\requirements.txt (line 132))
  Using cached ecdsa-0.19.1-py2.py3-none-any.whl.metadata (29 kB)
Collecting et-xmlfile==2.0.0 (from -r backend\requirements.txt (line 134))
  Using cached et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
Collecting fastapi==0.116.1 (from -r backend\requirements.txt (line 136))
  Using cached fastapi-0.116.1-py3-none-any.whl.metadata (28 kB)
Collecting feedparser==6.0.11 (from -r backend\requirements.txt (line 138))
  Using cached feedparser-6.0.11-py3-none-any.whl.metadata (2.4 kB)
Collecting filelock==3.18.0 (from -r backend\requirements.txt (line 142))
  Using cached filelock-3.18.0-py3-none-any.whl.metadata (2.9 kB)
Collecting filetype==1.2.0 (from -r backend\requirements.txt (line 148))
  Using cached filetype-1.2.0-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting flatbuffers==25.2.10 (from -r backend\requirements.txt (line 150))
  Using cached flatbuffers-25.2.10-py2.py3-none-any.whl.metadata (875 bytes)
Collecting forbiddenfruit==0.1.4 (from -r backend\requirements.txt (line 152))
  Using cached forbiddenfruit-0.1.4-py3-none-any.whl
Collecting fpdf==1.7.2 (from -r backend\requirements.txt (line 154))
  Using cached fpdf-1.7.2-py2.py3-none-any.whl
Collecting frozenlist==1.7.0 (from -r backend\requirements.txt (line 156))
  Using cached frozenlist-1.7.0-cp312-cp312-win_amd64.whl.metadata (19 kB)
Collecting fsspec==2025.7.0 (from -r backend\requirements.txt (line 160))
  Using cached fsspec-2025.7.0-py3-none-any.whl.metadata (12 kB)
Collecting google-ai-generativelanguage==0.6.18 (from -r backend\requirements.txt (line 164))
  Using cached google_ai_generativelanguage-0.6.18-py3-none-any.whl.metadata (9.8 kB)Collecting google-api-core==2.25.1 (from google-api-core[grpc]==2.25.1->-r backend\requirements.txt (line 166))
  Using cached google_api_core-2.25.1-py3-none-any.whl.metadata (3.0 kB)
Collecting google-api-python-client==2.176.0 (from -r backend\requirements.txt (line 
175))
  Using cached google_api_python_client-2.176.0-py3-none-any.whl.metadata (7.0 kB)
Collecting google-auth==2.40.3 (from -r backend\requirements.txt (line 177))
  Using cached google_auth-2.40.3-py2.py3-none-any.whl.metadata (6.2 kB)
Collecting google-auth-httplib2==0.2.0 (from -r backend\requirements.txt (line 192))
  Using cached google_auth_httplib2-0.2.0-py2.py3-none-any.whl.metadata (2.2 kB)
Collecting google-auth-oauthlib==1.2.2 (from -r backend\requirements.txt (line 194))
  Using cached google_auth_oauthlib-1.2.2-py3-none-any.whl.metadata (2.7 kB)
Collecting google-cloud-aiplatform==1.104.0 (from -r backend\requirements.txt (line 196))
  Using cached google_cloud_aiplatform-1.104.0-py2.py3-none-any.whl.metadata (38 kB)
Collecting google-cloud-bigquery==3.35.0 (from -r backend\requirements.txt (line 198))
  Using cached google_cloud_bigquery-3.35.0-py3-none-any.whl.metadata (8.0 kB)
Collecting google-cloud-core==2.4.3 (from -r backend\requirements.txt (line 200))
  Using cached google_cloud_core-2.4.3-py2.py3-none-any.whl.metadata (2.7 kB)
Collecting google-cloud-resource-manager==1.14.2 (from -r backend\requirements.txt (line 204))
  Using cached google_cloud_resource_manager-1.14.2-py3-none-any.whl.metadata (9.6 kB)
Collecting google-cloud-storage==2.19.0 (from -r backend\requirements.txt (line 206))  Using cached google_cloud_storage-2.19.0-py2.py3-none-any.whl.metadata (9.1 kB)
Collecting google-crc32c==1.7.1 (from -r backend\requirements.txt (line 208))
  Using cached google_crc32c-1.7.1-cp312-cp312-win_amd64.whl.metadata (2.4 kB)
Collecting google-genai==1.26.0 (from -r backend\requirements.txt (line 212))
  Using cached google_genai-1.26.0-py3-none-any.whl.metadata (42 kB)
Collecting google-resumable-media==2.7.2 (from -r backend\requirements.txt (line 216))
  Using cached google_resumable_media-2.7.2-py2.py3-none-any.whl.metadata (2.2 kB)
Collecting googleapis-common-protos==1.70.0 (from googleapis-common-protos[grpc]==1.70.0->-r backend\requirements.txt (line 220))
  Using cached googleapis_common_protos-1.70.0-py3-none-any.whl.metadata (9.3 kB)
Collecting gotrue==2.12.3 (from -r backend\requirements.txt (line 226))
  Using cached gotrue-2.12.3-py3-none-any.whl.metadata (6.5 kB)
Collecting greenlet==3.2.3 (from -r backend\requirements.txt (line 228))
  Using cached greenlet-3.2.3-cp312-cp312-win_amd64.whl.metadata (4.2 kB)
Collecting groq==0.30.0 (from -r backend\requirements.txt (line 230))
  Using cached groq-0.30.0-py3-none-any.whl.metadata (16 kB)
Collecting grpc-google-iam-v1==0.14.2 (from -r backend\requirements.txt (line 232))
  Using cached grpc_google_iam_v1-0.14.2-py3-none-any.whl.metadata (9.1 kB)
Collecting grpcio==1.73.1 (from -r backend\requirements.txt (line 234))
  Using cached grpcio-1.73.1-cp312-cp312-win_amd64.whl.metadata (4.0 kB)
Collecting grpcio-status==1.73.1 (from -r backend\requirements.txt (line 242))
  Using cached grpcio_status-1.73.1-py3-none-any.whl.metadata (1.1 kB)
Collecting h11==0.16.0 (from -r backend\requirements.txt (line 244))
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting h2==4.2.0 (from -r backend\requirements.txt (line 248))
  Using cached h2-4.2.0-py3-none-any.whl.metadata (5.1 kB)
Collecting hf-xet==1.1.5 (from -r backend\requirements.txt (line 250))
  Using cached hf_xet-1.1.5-cp37-abi3-win_amd64.whl.metadata (883 bytes)
Collecting hpack==4.1.0 (from -r backend\requirements.txt (line 252))
  Using cached hpack-4.1.0-py3-none-any.whl.metadata (4.6 kB)
Collecting httpcore==1.0.9 (from -r backend\requirements.txt (line 254))
  Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Collecting httplib2==0.22.0 (from -r backend\requirements.txt (line 256))
  Using cached httplib2-0.22.0-py3-none-any.whl.metadata (2.6 kB)
Collecting httptools==0.6.4 (from -r backend\requirements.txt (line 260))
  Using cached httptools-0.6.4-cp312-cp312-win_amd64.whl.metadata (3.7 kB)
Collecting httpx==0.28.1 (from httpx[http2]==0.28.1->-r backend\requirements.txt (line 262))
  Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Collecting huggingface-hub==0.33.4 (from -r backend\requirements.txt (line 279))
  Using cached huggingface_hub-0.33.4-py3-none-any.whl.metadata (14 kB)
Collecting humanfriendly==10.0 (from -r backend\requirements.txt (line 284))
  Using cached humanfriendly-10.0-py2.py3-none-any.whl.metadata (9.2 kB)
Collecting hyperframe==6.1.0 (from -r backend\requirements.txt (line 286))
  Using cached hyperframe-6.1.0-py3-none-any.whl.metadata (4.3 kB)
Collecting idna==3.10 (from -r backend\requirements.txt (line 288))
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting importlib-metadata==8.7.0 (from -r backend\requirements.txt (line 294))
  Using cached importlib_metadata-8.7.0-py3-none-any.whl.metadata (4.8 kB)
Collecting importlib-resources==6.5.2 (from -r backend\requirements.txt (line 296))
  Using cached importlib_resources-6.5.2-py3-none-any.whl.metadata (3.9 kB)
Collecting iniconfig==2.1.0 (from -r backend\requirements.txt (line 298))
  Using cached iniconfig-2.1.0-py3-none-any.whl.metadata (2.7 kB)
Collecting isodate==0.7.2 (from -r backend\requirements.txt (line 300))
  Using cached isodate-0.7.2-py3-none-any.whl.metadata (11 kB)
Collecting jinja2==3.1.6 (from -r backend\requirements.txt (line 302))
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting jiter==0.10.0 (from -r backend\requirements.txt (line 304))
  Using cached jiter-0.10.0-cp312-cp312-win_amd64.whl.metadata (5.3 kB)
Collecting jmespath==1.0.1 (from -r backend\requirements.txt (line 308))
  Using cached jmespath-1.0.1-py3-none-any.whl.metadata (7.6 kB)
Collecting joblib==1.5.1 (from -r backend\requirements.txt (line 312))
  Using cached joblib-1.5.1-py3-none-any.whl.metadata (5.6 kB)
Collecting jsonpatch==1.33 (from -r backend\requirements.txt (line 314))
  Using cached jsonpatch-1.33-py2.py3-none-any.whl.metadata (3.0 kB)
Collecting jsonpointer==3.0.0 (from -r backend\requirements.txt (line 316))
  Using cached jsonpointer-3.0.0-py2.py3-none-any.whl.metadata (2.3 kB)
Collecting jsonschema==4.25.0 (from -r backend\requirements.txt (line 318))
  Using cached jsonschema-4.25.0-py3-none-any.whl.metadata (7.7 kB)
Collecting jsonschema-rs==0.29.1 (from -r backend\requirements.txt (line 322))
  Using cached jsonschema_rs-0.29.1-cp312-cp312-win_amd64.whl.metadata (14 kB)
Collecting jsonschema-specifications==2025.4.1 (from -r backend\requirements.txt (line 324))
  Using cached jsonschema_specifications-2025.4.1-py3-none-any.whl.metadata (2.9 kB)
Collecting kombu==5.5.4 (from kombu[redis]==5.5.4->-r backend\requirements.txt (line 
326))
  Using cached kombu-5.5.4-py3-none-any.whl.metadata (3.5 kB)
Collecting kubernetes==33.1.0 (from -r backend\requirements.txt (line 328))
  Using cached kubernetes-33.1.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting langchain==0.3.26 (from -r backend\requirements.txt (line 330))
  Using cached langchain-0.3.26-py3-none-any.whl.metadata (7.8 kB)
Collecting langchain-community==0.3.27 (from -r backend\requirements.txt (line 332))
  Using cached langchain_community-0.3.27-py3-none-any.whl.metadata (2.9 kB)
Collecting langchain-core==0.3.70 (from -r backend\requirements.txt (line 334))
  Using cached langchain_core-0.3.70-py3-none-any.whl.metadata (5.8 kB)
Collecting langchain-google-genai==2.1.8 (from -r backend\requirements.txt (line 346))
  Using cached langchain_google_genai-2.1.8-py3-none-any.whl.metadata (7.0 kB)
Collecting langchain-groq==0.3.6 (from -r backend\requirements.txt (line 348))
  Using cached langchain_groq-0.3.6-py3-none-any.whl.metadata (2.6 kB)
Collecting langchain-openai==0.3.28 (from -r backend\requirements.txt (line 350))
  Using cached langchain_openai-0.3.28-py3-none-any.whl.metadata (2.3 kB)
Collecting langchain-text-splitters==0.3.8 (from -r backend\requirements.txt (line 352))
  Using cached langchain_text_splitters-0.3.8-py3-none-any.whl.metadata (1.9 kB)
Collecting langgraph==0.5.4 (from -r backend\requirements.txt (line 354))
  Using cached langgraph-0.5.4-py3-none-any.whl.metadata (6.8 kB)
Collecting langgraph-api==0.2.98 (from -r backend\requirements.txt (line 359))
  Using cached langgraph_api-0.2.98-py3-none-any.whl.metadata (3.9 kB)
Collecting langgraph-checkpoint==2.1.1 (from -r backend\requirements.txt (line 363))
  Using cached langgraph_checkpoint-2.1.1-py3-none-any.whl.metadata (4.2 kB)
Collecting langgraph-cli==0.3.5 (from langgraph-cli[inmem]==0.3.5->-r backend\requirements.txt (line 369))
  Using cached langgraph_cli-0.3.5-py3-none-any.whl.metadata (3.8 kB)
Collecting langgraph-prebuilt==0.5.2 (from -r backend\requirements.txt (line 371))
  Using cached langgraph_prebuilt-0.5.2-py3-none-any.whl.metadata (4.5 kB)
Collecting langgraph-runtime-inmem==0.6.0 (from -r backend\requirements.txt (line 373))
  Using cached langgraph_runtime_inmem-0.6.0-py3-none-any.whl.metadata (565 bytes)
Collecting langgraph-sdk==0.1.74 (from -r backend\requirements.txt (line 377))
  Using cached langgraph_sdk-0.1.74-py3-none-any.whl.metadata (1.5 kB)
Collecting langsmith==0.4.8 (from -r backend\requirements.txt (line 382))
  Using cached langsmith-0.4.8-py3-none-any.whl.metadata (15 kB)
Collecting lxml==6.0.0 (from -r backend\requirements.txt (line 387))
  Using cached lxml-6.0.0-cp312-cp312-win_amd64.whl.metadata (6.8 kB)
Collecting mako==1.3.10 (from -r backend\requirements.txt (line 391))
  Using cached mako-1.3.10-py3-none-any.whl.metadata (2.9 kB)
Collecting markdown-it-py==3.0.0 (from -r backend\requirements.txt (line 393))
  Using cached markdown_it_py-3.0.0-py3-none-any.whl.metadata (6.9 kB)
Collecting markupsafe==3.0.2 (from -r backend\requirements.txt (line 395))
  Using cached MarkupSafe-3.0.2-cp312-cp312-win_amd64.whl.metadata (4.1 kB)
Collecting mdurl==0.1.2 (from -r backend\requirements.txt (line 399))
  Using cached mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Collecting mmh3==5.1.0 (from -r backend\requirements.txt (line 401))
  Using cached mmh3-5.1.0-cp312-cp312-win_amd64.whl.metadata (16 kB)
Collecting mpmath==1.3.0 (from -r backend\requirements.txt (line 403))
  Using cached mpmath-1.3.0-py3-none-any.whl.metadata (8.6 kB)
Collecting multidict==6.6.3 (from -r backend\requirements.txt (line 405))
  Using cached multidict-6.6.3-cp312-cp312-win_amd64.whl.metadata (5.4 kB)
Collecting mypy==1.17.0 (from -r backend\requirements.txt (line 409))
  Using cached mypy-1.17.0-cp312-cp312-win_amd64.whl.metadata (2.2 kB)
Collecting mypy-extensions==1.1.0 (from -r backend\requirements.txt (line 411))
  Using cached mypy_extensions-1.1.0-py3-none-any.whl.metadata (1.1 kB)
Collecting networkx==3.5 (from -r backend\requirements.txt (line 413))
  Using cached networkx-3.5-py3-none-any.whl.metadata (6.3 kB)
Collecting numpy==2.2.6 (from -r backend\requirements.txt (line 415))
  Using cached numpy-2.2.6-cp312-cp312-win_amd64.whl.metadata (60 kB)
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
ERROR: Ignored the following versions that require a different python version: 0.1.0 
Requires-Python >=3.9.0,<3.12; 0.1.1 Requires-Python >=3.9.0,<3.12; 0.1.2 Requires-Python >=3.9.0,<3.12; 0.1.3 Requires-Python >=3.9.0,<3.12; 0.1.4 Requires-Python >=3.9.0,<3.12; 0.1.5 Requires-Python >=3.9.0,<3.12; 0.1.6 Requires-Python >=3.9.0,<3.12; 0.1.7 Requires-Python >=3.9.0,<3.12; 1.21.2 Requires-Python >=3.7,<3.11; 1.21.3 Requires-Python >=3.7,<3.11; 1.21.4 Requires-Python >=3.7,<3.11; 1.21.5 Requires-Python >=3.7,<3.11; 1.21.6 Requires-Python >=3.7,<3.11; 2.10.0 Requires-Python >=3.6,<3.10; 2.11.0 Requires-Python >=3.6,<3.10; 2.12.0 Requires-Python >=3.6,<3.10; 2.13.0 Requires-Python >=3.6,<3.10; 2.13.1 Requires-Python >=3.6,<3.10; 2.14.0 Requires-Python >=3.6,<3.10; 2.15.0 Requires-Python >=3.6,<3.10; 2.16.0 Requires-Python >=3.6,<3.10; 2.16.1 
Requires-Python >=3.6,<3.10; 2.17.0 Requires-Python >=3.6,<3.10; 2.18.0 Requires-Python >=3.6,<3.10; 2.19.0 Requires-Python >=3.6,<3.10; 2.20.0 Requires-Python >=3.6,<3.10; 2.21.0 Requires-Python >=3.6,<3.10; 2.22.0 Requires-Python >=3.6,<3.10; 2.22.1 Requires-Python >=3.6,<3.10; 2.23.0 Requires-Python >=3.6,<3.10; 2.23.1 Requires-Python 
>=3.6,<3.10; 2.23.2 Requires-Python >=3.6,<3.10; 2.23.3 Requires-Python >=3.6,<3.10; 
2.24.0 Requires-Python >=3.6,<3.10; 2.24.1 Requires-Python >=3.6,<3.10; 2.25.0 Requires-Python >=3.6,<3.10; 2.25.1 Requires-Python >=3.6,<3.10; 2.25.2 Requires-Python >=3.6,<3.10; 2.26.0 Requires-Python >=3.6,<3.10; 2.27.0 Requires-Python >=3.6,<3.10; 2.27.1 Requires-Python >=3.6,<3.10; 2.28.0 Requires-Python >=3.6,<3.10; 2.28.1 Requires-Python >=3.6,<3.10; 2.29.0 Requires-Python >=3.6,<3.10; 2.30.0 Requires-Python >=3.6,<3.11; 2.30.1 Requires-Python >=3.6,<3.11; 2.31.0 Requires-Python >=3.6,<3.11; 2.32.0 Requires-Python >=3.6,<3.11; 2.33.0 Requires-Python >=3.6,<3.11; 2.34.0 Requires-Python >=3.6,<3.11; 2.34.1 Requires-Python >=3.6,<3.11; 2.34.2 Requires-Python >=3.6,<3.11; 2.34.3 Requires-Python >=3.6,<3.11; 2.34.4 Requires-Python >=3.6,<3.11; 2.6.2 Requires-Python >=3.6,<3.9; 2.7.0 Requires-Python >=3.6,<3.10; 2.8.0 Requires-Python >=3.6,<3.10; 2.9.0 Requires-Python >=3.6,<3.10; 3.0.0 Requires-Python >=3.6,<3.11; 3.0.0b1 Requires-Python >=3.6,<3.11; 3.0.1 Requires-Python >=3.6,<3.11; 3.1.0 Requires-Python >=3.6,<3.11; 3.2.0 Requires-Python >=3.6,<3.11; 3.3.0 Requires-Python >=3.7,<3.11; 3.3.1 Requires-Python >=3.7,<3.11; 3.3.2 Requires-Python >=3.7,<3.11; 3.3.3 Requires-Python >=3.7,<3.11; 3.3.5 Requires-Python >=3.7,<3.11; 3.3.6 Requires-Python >=3.7,<3.11
ERROR: Could not find a version that satisfies the requirement nvidia-nccl-cu12==2.21.5 (from versions: 0.0.1.dev5)
ERROR: No matching distribution found for nvidia-nccl-cu12==2.21.5
(.venv) PS D:\HandyWriterzAi> set PYTHONPATH=.;backend;backend\src
backend: The term 'backend' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
backend\src: The module 'backend' could not be loaded. For more information, run 'Import-Module backend'.
(.venv) PS D:\HandyWriterzAi> pytest -q

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
(.venv) PS D:\HandyWriterzAi> 