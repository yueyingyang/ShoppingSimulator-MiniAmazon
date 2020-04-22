#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import socket

AMAZON_HOST, AMAZON_PORT = "vcm-12347.vm.duke.edu", 23456

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Amazon.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def connect_amazon():
    amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        try:
            amazon_socket.connect((AMAZON_HOST, AMAZON_PORT))
            print('Connected to Amazon backend')
            return amazon_socket
        except:
            print('Failed to connect to Amazon backend')
            continue

if __name__ == '__main__':
    amazon_socket = connect_amazon()
    # if amazon_socket:
    #     main()
    main()

