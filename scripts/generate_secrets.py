#!/usr/bin/env python3
"""
Generate secure secrets for deployment
"""
import secrets
import string
import sys


def generate_secret_key(length: int = 32) -> str:
    """Generate a secure secret key."""
    return secrets.token_hex(length)


def generate_password(length: int = 16) -> str:
    """Generate a secure password with mixed characters."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    print("🔐 Secure Secrets Generator for Note Taking API\n")
    
    print("1. SECRET_KEY (for JWT signing):")
    print(f"   {generate_secret_key()}\n")
    
    print("2. Database Password (PostgreSQL):")
    print(f"   {generate_password(20)}\n")
    
    print("3. Redis Password:")
    print(f"   {generate_password(20)}\n")
    
    print("4. Admin Password:")
    print(f"   {generate_password(16)}\n")
    
    print("5. Grafana Admin Password:")
    print(f"   {generate_password(16)}\n")
    
    print("\n📋 Copy these values to your environment configuration.")
    print("⚠️  Keep these values secure and never commit them to version control!")


if __name__ == "__main__":
    main() 