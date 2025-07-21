#!/usr/bin/env python3
"""
HandyWriterz Environment Configuration Validator
Validates all environment variables for YC Demo Day readiness
"""

import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse
import logging
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnvValidator:
    """Comprehensive environment configuration validator"""
    
    def __init__(self):
        self.backend_env_path = Path("backend/.env")
        self.frontend_env_path = Path("frontend/.env")
        self.validation_results = []
        self.critical_errors = []
        self.warnings = []
        
    def load_env_file(self, file_path: Path) -> Dict[str, str]:
        """Load environment variables from file"""
        env_vars = {}
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            return env_vars
        except FileNotFoundError:
            logger.error(f"Environment file not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {}
    
    def validate_required_keys(self, env_vars: Dict[str, str], required_keys: List[str], context: str) -> bool:
        """Validate that all required keys are present and not empty"""
        missing_keys = []
        empty_keys = []
        
        for key in required_keys:
            if key not in env_vars:
                missing_keys.append(key)
            elif not env_vars[key] or env_vars[key] in ['your_api_key_here', 'your_actual_key_here', '']:
                empty_keys.append(key)
        
        if missing_keys:
            self.critical_errors.append(f"{context}: Missing required keys: {', '.join(missing_keys)}")
            return False
            
        if empty_keys:
            self.warnings.append(f"{context}: Empty or placeholder values: {', '.join(empty_keys)}")
            return False
            
        return True
    
    def validate_url_format(self, url: str, description: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                return True
            else:
                self.warnings.append(f"Invalid URL format for {description}: {url}")
                return False
        except Exception:
            self.warnings.append(f"Invalid URL format for {description}: {url}")
            return False
    
    def validate_supabase_config(self, env_vars: Dict[str, str]) -> bool:
        """Validate Supabase configuration"""
        logger.info("🔍 Validating Supabase configuration...")
        
        supabase_keys = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'DATABASE_URL'
        ]
        
        valid = True
        
        # Check required keys exist
        if not self.validate_required_keys(env_vars, supabase_keys, "Supabase"):
            valid = False
        
        # Validate Supabase URL format
        if 'SUPABASE_URL' in env_vars:
            supabase_url = env_vars['SUPABASE_URL']
            if not self.validate_url_format(supabase_url, "Supabase URL"):
                valid = False
            elif not supabase_url.endswith('.supabase.co'):
                self.warnings.append("Supabase URL should end with .supabase.co")
        
        # Validate JWT format
        if 'SUPABASE_ANON_KEY' in env_vars:
            anon_key = env_vars['SUPABASE_ANON_KEY']
            if not anon_key.startswith('eyJ'):
                self.warnings.append("Supabase anon key doesn't appear to be a valid JWT")
        
        # Validate database URL format
        if 'DATABASE_URL' in env_vars:
            db_url = env_vars['DATABASE_URL']
            if not db_url.startswith('postgresql://'):
                self.critical_errors.append("DATABASE_URL must be a PostgreSQL connection string")
                valid = False
            elif 'supabase.co' not in db_url and 'localhost' not in db_url:
                self.warnings.append("Database URL doesn't appear to be Supabase or local")
        
        return valid
    
    def validate_llm_keys(self, env_vars: Dict[str, str]) -> bool:
        """Validate LLM API keys"""
        logger.info("🤖 Validating LLM API keys...")
        
        # Primary LLM keys (at least one required)
        primary_keys = ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
        secondary_keys = ['PERPLEXITY_API_KEY', 'QWEN_API_KEY', 'DEEPSEEK_API_KEY']
        
        # Check if at least one primary key is valid
        valid_primary = False
        for key in primary_keys:
            if key in env_vars and env_vars[key] and env_vars[key] not in ['your_api_key_here', 'your_actual_key_here']:
                valid_primary = True
                logger.info(f"✅ {key} configured")
        
        if not valid_primary:
            self.critical_errors.append("At least one primary LLM API key must be configured (Gemini, OpenAI, or Anthropic)")
            return False
        
        # Check secondary keys
        for key in secondary_keys:
            if key in env_vars and env_vars[key] and env_vars[key] not in ['your_api_key_here', 'your_actual_key_here']:
                logger.info(f"✅ {key} configured")
            else:
                logger.info(f"⚠️ {key} not configured (optional)")
        
        return True
    
    def validate_demo_config(self, env_vars: Dict[str, str]) -> bool:
        """Validate YC Demo Day specific configuration"""
        logger.info("🎪 Validating YC Demo Day configuration...")
        
        demo_keys = [
            'TARGET_PROCESSING_TIME_SECONDS',
            'TARGET_QUALITY_SCORE', 
            'TARGET_ORIGINALITY_PERCENTAGE',
            'TARGET_MAX_COST_USD',
            'AGENT_COUNT'
        ]
        
        valid = True
        
        # Check demo mode settings
        if 'DEMO_MODE' in env_vars and env_vars['DEMO_MODE'].lower() == 'true':
            logger.info("✅ Demo mode enabled")
        else:
            self.warnings.append("DEMO_MODE not enabled - may affect YC Demo Day presentation")
        
        # Validate performance targets
        try:
            if 'TARGET_PROCESSING_TIME_SECONDS' in env_vars:
                time_target = int(env_vars['TARGET_PROCESSING_TIME_SECONDS'])
                if time_target != 807:
                    self.warnings.append(f"Processing time target is {time_target}s, demo expects 807s")
            
            if 'TARGET_QUALITY_SCORE' in env_vars:
                quality_target = float(env_vars['TARGET_QUALITY_SCORE'])
                if quality_target != 9.1:
                    self.warnings.append(f"Quality score target is {quality_target}, demo expects 9.1")
            
            if 'TARGET_ORIGINALITY_PERCENTAGE' in env_vars:
                originality_target = float(env_vars['TARGET_ORIGINALITY_PERCENTAGE'])
                if originality_target != 88.7:
                    self.warnings.append(f"Originality target is {originality_target}%, demo expects 88.7%")
            
            if 'AGENT_COUNT' in env_vars:
                agent_count = int(env_vars['AGENT_COUNT'])
                if agent_count != 32:
                    self.warnings.append(f"Agent count is {agent_count}, demo expects 32 agents")
                    
        except ValueError as e:
            self.critical_errors.append(f"Invalid numeric values in demo configuration: {e}")
            valid = False
        
        return valid
    
    def validate_security_config(self, env_vars: Dict[str, str]) -> bool:
        """Validate security configuration"""
        logger.info("🛡️ Validating security configuration...")
        
        valid = True
        
        # Check JWT secret
        if 'JWT_SECRET_KEY' in env_vars:
            jwt_secret = env_vars['JWT_SECRET_KEY']
            if len(jwt_secret) < 32:
                self.critical_errors.append("JWT_SECRET_KEY must be at least 32 characters long")
                valid = False
            elif jwt_secret in ['your_jwt_secret_here', 'default_secret']:
                self.critical_errors.append("JWT_SECRET_KEY must be changed from default value")
                valid = False
        else:
            self.critical_errors.append("JWT_SECRET_KEY is required for security")
            valid = False
        
        # Check production settings
        if 'NODE_ENV' in env_vars:
            if env_vars['NODE_ENV'] != 'production':
                self.warnings.append("NODE_ENV should be 'production' for YC Demo Day")
        
        if 'DEBUG' in env_vars and env_vars['DEBUG'].lower() == 'true':
            self.warnings.append("DEBUG mode is enabled - should be disabled for production")
        
        return valid
    
    def validate_frontend_config(self) -> bool:
        """Validate frontend environment configuration"""
        logger.info("🎨 Validating frontend configuration...")
        
        if not self.frontend_env_path.exists():
            self.critical_errors.append("Frontend .env file does not exist")
            return False
        
        frontend_vars = self.load_env_file(self.frontend_env_path)
        
        required_frontend_keys = [
            'NEXT_PUBLIC_API_URL',
            'NEXT_PUBLIC_SUPABASE_URL',
            'NEXT_PUBLIC_SUPABASE_ANON_KEY',
            'NEXT_PUBLIC_DYNAMIC_ENV_ID'
        ]
        
        valid = self.validate_required_keys(frontend_vars, required_frontend_keys, "Frontend")
        
        # Validate API URLs
        for key in ['NEXT_PUBLIC_API_URL', 'NEXT_PUBLIC_WS_URL', 'NEXT_PUBLIC_AGENTIC_DOC_URL']:
            if key in frontend_vars:
                if not self.validate_url_format(frontend_vars[key], key):
                    valid = False
        
        # Check demo day specific frontend config
        demo_frontend_keys = [
            'NEXT_PUBLIC_DEMO_MODE',
            'NEXT_PUBLIC_AGENT_COUNT',
            'NEXT_PUBLIC_TARGET_QUALITY_SCORE'
        ]
        
        for key in demo_frontend_keys:
            if key not in frontend_vars:
                self.warnings.append(f"Frontend demo configuration missing: {key}")
        
        # Check feature flags
        if 'NEXT_PUBLIC_ENABLE_MULTIMODAL_UPLOAD' not in frontend_vars or frontend_vars['NEXT_PUBLIC_ENABLE_MULTIMODAL_UPLOAD'].lower() != 'true':
            self.warnings.append("Multimodal upload not enabled in frontend")
        
        return valid
    
    def validate_backend_config(self) -> bool:
        """Validate backend environment configuration"""
        logger.info("⚙️ Validating backend configuration...")
        
        if not self.backend_env_path.exists():
            self.critical_errors.append("Backend .env file does not exist")
            return False
        
        backend_vars = self.load_env_file(self.backend_env_path)
        
        valid = True
        
        # Validate core configurations
        valid &= self.validate_supabase_config(backend_vars)
        valid &= self.validate_llm_keys(backend_vars)
        valid &= self.validate_demo_config(backend_vars)
        valid &= self.validate_security_config(backend_vars)
        
        # Check Redis configuration
        if 'REDIS_URL' not in backend_vars:
            self.critical_errors.append("REDIS_URL is required for caching and pub/sub")
            valid = False
        
        # Check file upload configuration
        if 'UPLOAD_MAX_SIZE' in backend_vars:
            try:
                max_size = int(backend_vars['UPLOAD_MAX_SIZE'])
                if max_size < 104857600:  # 100MB
                    self.warnings.append("Upload max size is less than 100MB - may limit multimodal file uploads")
            except ValueError:
                self.warnings.append("Invalid UPLOAD_MAX_SIZE value")
        
        return valid
    
    def run_validation(self) -> bool:
        """Run complete environment validation"""
        logger.info("🔍 Starting HandyWriterz Environment Validation")
        logger.info("=" * 60)
        
        # Validate backend configuration
        backend_valid = self.validate_backend_config()
        
        # Validate frontend configuration  
        frontend_valid = self.validate_frontend_config()
        
        # Generate report
        self.generate_validation_report(backend_valid and frontend_valid)
        
        return backend_valid and frontend_valid
    
    def generate_validation_report(self, overall_valid: bool):
        """Generate comprehensive validation report"""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 ENVIRONMENT VALIDATION REPORT")
        logger.info("=" * 60)
        
        # Summary
        status = "✅ READY" if overall_valid and not self.critical_errors else "❌ NEEDS ATTENTION"
        logger.info(f"📊 Overall Status: {status}")
        
        # Critical errors
        if self.critical_errors:
            logger.info(f"\n🚨 CRITICAL ERRORS ({len(self.critical_errors)}):")
            for error in self.critical_errors:
                logger.error(f"   ❌ {error}")
        
        # Warnings
        if self.warnings:
            logger.info(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"   ⚠️ {warning}")
        
        # Configuration summary
        logger.info(f"\n📋 CONFIGURATION SUMMARY:")
        logger.info(f"   Backend .env: {'✅' if self.backend_env_path.exists() else '❌'}")
        logger.info(f"   Frontend .env: {'✅' if self.frontend_env_path.exists() else '❌'}")
        logger.info(f"   Critical errors: {len(self.critical_errors)}")
        logger.info(f"   Warnings: {len(self.warnings)}")
        
        # YC Demo Day readiness
        logger.info(f"\n🎪 YC DEMO DAY READINESS:")
        if overall_valid and not self.critical_errors:
            logger.info("   🏆 Environment fully configured for YC Demo Day")
            logger.info("   🚀 All systems ready for live demonstration")
            logger.info("   💡 No critical issues blocking demo")
        else:
            logger.info("   🔧 Environment needs attention before demo")
            logger.info("   ⚠️ Address critical errors to ensure smooth demo")
        
        # Next steps
        logger.info(f"\n📝 NEXT STEPS:")
        if self.critical_errors:
            logger.info("   1. Fix all critical errors listed above")
            logger.info("   2. Re-run validation: python validate-env-config.py")
            logger.info("   3. Test deployment: ./deploy-production.sh")
        else:
            logger.info("   1. Review and address warnings if needed")
            logger.info("   2. Run deployment: ./deploy-production.sh") 
            logger.info("   3. Validate deployment: ./validate-deployment.sh")
            logger.info("   4. Run demo test: python test_yc_demo_ready.py")
        
        logger.info("=" * 60)

def main():
    """Main validation execution"""
    print("🎯 HandyWriterz Environment Configuration Validator")
    print("=" * 50)
    
    validator = EnvValidator()
    
    try:
        is_valid = validator.run_validation()
        
        # Exit codes
        if is_valid and not validator.critical_errors:
            print("\n✨ Environment validation completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ Environment validation found issues")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()