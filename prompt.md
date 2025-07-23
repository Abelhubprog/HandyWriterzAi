# Pluggable-Model Control Panel: Environment Issue

## Goal

The goal is to create a "Pluggable-Model" control panel that allows an administrator to swap the AI models used for different stages of the HandyWriterz workflow without redeploying the application. This involves:

1.  Storing the model mapping in a database table.
2.  Creating an admin UI to edit the mapping.
3.  Refactoring the agent nodes to dynamically load the models from the database.

## Problem

I am currently blocked from implementing this feature due to a persistent issue with the Python environment. I am unable to install the required dependencies, which prevents me from setting up the database table and proceeding with the rest of the implementation.

### Root Cause

The root cause of the issue is an incompatibility between the project's dependencies and the Python 3.14 environment. Specifically:

1.  **Missing C++ Compiler**: Several key packages, including `numpy` and `onnxruntime` (a dependency of `chromadb`), require a C++ compiler to be built from source. The current environment does not have a C++ compiler configured, causing the build process to fail.
2.  **Lack of Pre-builta Wheels**: For many of the required packages, pre-built binary wheels are not yet available for Python 3.14. This forces `pip` to attempt to build them from source, which fails without a C++ compiler.

### Impact

This issue prevents me from:

*   Installing the required Python dependencies.
*   Running the database migrations to create the `model_map` table.
*   Proceeding with the development of the admin UI and the refactoring of the agent nodes.

### Proposed Solutions

I have identified several potential solutions to this problem:

1.  **Use a JSON file for model configuration**: Instead of a database table, we could use a JSON file to store the model configuration. This would bypass the need for database migrations and allow me to proceed with the rest of the implementation.
2.  **Fix the Python build environment**: This would involve installing a C++ compiler and other necessary build tools in the environment.
3.  **Switch to an older Python version**: We could switch the project to use a more stable version of Python, such as 3.12, for which pre-built wheels are more likely to be available for all dependencies.
4.  **Find compatible package versions**: I could continue to try and find versions of the conflicting packages that have pre-built wheels for Python 3.14, although this has been unsuccessful so far.

I am currently awaiting guidance on how to proceed.