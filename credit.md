below are model prices from providers. the Handywriterzai uses these models but must optimise for performance and cost reductions. we want to ensure users pays based on credits used, the frontend has
has pricing tiers with credits.  
openai/gpt-5 (https://openrouter.ai/openai/gpt-5) 
GPT-5 Chat is designed for advanced, natural, multimodal, and context-aware conversations for enterprise applications.

by openai
400K context
$1.25/M input tokens
$10/M output tokens

openai/o3
o3 is a well-rounded and powerful model across domains. It sets a new standard for math, science, coding, and visual reasoning tasks. It also excels at technical writing and instruction-following. Use it to think through multi-step problems that involve analysis across text, code, and images. Note that BYOK is required for this model. Set up here: https://openrouter.ai/settings/integrations
Context
200K
Max Output
100K
Input
$2
Output
$8
Latency
3.49
s
Throughput
37.93
tps
Uptime


openai/gpt-5-chat 

GPT-5 Chat is designed for advanced, natural, multimodal, and context-aware conversations for enterprise applications.

by openai
400K context
$1.25/M input tokens
$10/M output tokens


openai/o3-pro (this is expensive we cannot use!)
The o-series of models are trained with reinforcement learning to think before they answer and perform complex reasoning. The o3-pro model uses more compute to think harder and provide consistently better answers.  Note that BYOK is required for this model. Set up here: https://openrouter.ai/settings/integrations

by openai
200K context
$20/M input tokens
$80/M output tokens
$15.30/K input imgs


openai/o4-mini-high 
OpenAI o4-mini-high is the same model as o4-mini with reasoning_effort set to high.

OpenAI o4-mini is a compact reasoning model in the o-series, optimized for fast, cost-efficient performance while retaining strong multimodal and agentic capabilities. It supports tool use and demonstrates competitive reasoning and coding performance across benchmarks like AIME (99.5% with Python) and SWE-bench, outperforming its predecessor o3-mini and even approaching o3 in some domains.

Despite its smaller size, o4-mini exhibits high accuracy in STEM tasks, visual problem solving (e.g., MathVista, MMMU), and code editing. It is especially well-suited for high-throughput scenarios where latency or cost is critical. Thanks to its efficient architecture and refined reinforcement learning training, o4-mini can chain tools, generate structured outputs, and solve multi-step tasks with minimal delay—often in under a minute.



google/gemini-2.5-pro
Gemini 2.5 Pro is Google’s state-of-the-art AI model designed for advanced reasoning, coding, mathematics, and scientific tasks. It employs “thinking” capabilities, enabling it to reason through responses with enhanced accuracy and nuanced context handling. Gemini 2.5 Pro achieves top-tier performance on multiple benchmarks, including first-place positioning on the LMArena leaderboard, reflecting superior human-preference alignment and complex problem-solving abilities.
Created Jun 17, 2025
1,048,576 context
Starting at $1.25/M input tokens
Starting at $10/M output tokens
$5.16/K input imgs

google/gemini-2.5-flash
Gemini 2.5 Flash is Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. It includes built-in "thinking" capabilities, enabling it to provide responses with greater accuracy and nuanced context handling.

Additionally, Gemini 2.5 Flash is configurable through the "max tokens for reasoning" parameter, as described in the documentation 
Created Jun 17, 2025
1,048,576 context
$0.30/M input tokens
$2.50/M output tokens
$1.238/K input imgs

moonshotai/kimi-k2
Created Jul 11, 2025
63,000 context
$0.14/M input tokens
$2.49/M output tokens
Kimi K2 Instruct is a large-scale Mixture-of-Experts (MoE) language model developed by Moonshot AI, featuring 1 trillion total parameters with 32 billion active per forward pass. It is optimized for agentic capabilities, including advanced tool use, reasoning, and code synthesis. Kimi K2 excels across a broad range of benchmarks, particularly in coding (LiveCodeBench, SWE-bench), reasoning (ZebraLogic, GPQA), and tool-use (Tau2, AceBench) tasks. It supports long-context inference up to 128K tokens and is designed with a novel training stack that includes the MuonClip optimizer for stable large-scale MoE training.

anthropic/claude-sonnet-4
Claude Sonnet 4 significantly enhances the capabilities of its predecessor, Sonnet 3.7, excelling in both coding and reasoning tasks with improved precision and controllability. Achieving state-of-the-art performance on SWE-bench (72.7%), Sonnet 4 balances capability and computational efficiency, making it suitable for a broad range of applications from routine coding tasks to complex software development projects. Key enhancements include improved autonomous codebase navigation, reduced error rates in agent-driven workflows, and increased reliability in following intricate instructions. Sonnet 4 is optimized for practical everyday use, providing advanced reasoning capabilities while maintaining efficiency and responsiveness in diverse internal and external scenarios.
Created May 22, 2025
200,000 context
$3/M input tokens
$15/M output tokens
$4.80/K input imgs

qwen/qwen3-coder
Qwen3-Coder-480B-A35B-Instruct is a Mixture-of-Experts (MoE) code generation model developed by the Qwen team. It is optimized for agentic coding tasks such as function calling, tool use, and long-context reasoning over repositories. The model features 480 billion total parameters, with 35 billion active per forward pass (8 out of 160 experts).

Pricing for the Alibaba endpoints varies by context length. Once a request is greater than 128k input tokens, the higher pricing is used.
Created Jul 23, 2025
262,144 context
$0.20/M input tokens
$0.80/M output tokens

x-ai/grok-4
eated Jul 9, 2025
256,000 context
Starting at $3/M input tokens
Starting at $15/M output tokens
Grok 4 is xAI's latest reasoning model with a 256k context window. It supports parallel tool calling, structured outputs, and both image and text inputs. Note that reasoning is not exposed, reasoning cannot be disabled, and the reasoning effort cannot be specified. Pricing increases once the total tokens in a given request is greater than 128k tokens
