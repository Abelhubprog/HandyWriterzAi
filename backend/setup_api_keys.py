#!/usr/bin/env python3
"""
Setup script to add API keys for real AI responses
Run this script to configure your AI providers
"""
import os

def setup_api_keys():
    print("🔑 HandyWriterz API Key Setup")
    print("=" * 50)
    print("Add your AI provider API keys to enable real responses:")
    print("(Leave blank to skip a provider)")
    print()
    
    # OpenAI
    openai_key = input("OpenAI API Key: ").strip()
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        print("✅ OpenAI key configured")
    
    # Anthropic
    anthropic_key = input("Anthropic API Key: ").strip()
    if anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        print("✅ Anthropic key configured")
    
    # Google Gemini
    gemini_key = input("Google Gemini API Key: ").strip()
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        print("✅ Gemini key configured")
    
    print()
    if not any([openai_key, anthropic_key, gemini_key]):
        print("⚠️  No API keys provided. Chat will use fallback responses.")
    else:
        print("🎉 API keys configured! Real AI responses enabled.")
    
    print("\nNow run: python start_server.py")

if __name__ == "__main__":
    setup_api_keys()