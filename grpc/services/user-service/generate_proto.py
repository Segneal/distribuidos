#!/usr/bin/env python3
"""
Script to generate Python gRPC code from proto files
"""
import os
import subprocess
import sys

def generate_grpc_code():
    """Generate Python gRPC code from proto files"""
    
    # Paths
    proto_dir = os.path.join(os.path.dirname(__file__), '../../proto')
    output_dir = os.path.join(os.path.dirname(__file__), 'src/grpc')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Proto files to generate
    proto_files = ['user.proto']
    
    for proto_file in proto_files:
        proto_path = os.path.join(proto_dir, proto_file)
        
        if not os.path.exists(proto_path):
            print(f"Proto file not found: {proto_path}")
            continue
        
        # Generate Python code
        cmd = [
            sys.executable, '-m', 'grpc_tools.protoc',
            f'--proto_path={proto_dir}',
            f'--python_out={output_dir}',
            f'--grpc_python_out={output_dir}',
            proto_path
        ]
        
        print(f"Generating code for {proto_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error generating code for {proto_file}:")
            print(result.stderr)
        else:
            print(f"Successfully generated code for {proto_file}")
    
    print("gRPC code generation completed!")

if __name__ == '__main__':
    generate_grpc_code()