"""Shared fixtures for local-search tests"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file"""
    file_path = temp_dir / "sample.py"
    content = '''def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return "Hello"

class Calculator:
    """A simple calculator class"""

    def add(self, a, b):
        """Add two numbers"""
        return a + b

    def subtract(self, a, b):
        """Subtract two numbers"""
        return a - b
'''
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def sample_javascript_file(temp_dir):
    """Create a sample JavaScript file"""
    file_path = temp_dir / "sample.js"
    content = """function greet(name) {
    return `Hello, ${name}!`;
}

class Person {
    constructor(name) {
        this.name = name;
    }

    sayHello() {
        console.log(`Hello, I'm ${this.name}`);
    }
}
"""
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def sample_codebase(temp_dir):
    """Create a sample codebase with multiple files"""
    # Create Python files
    (temp_dir / "main.py").write_text('print("Main file")')
    (temp_dir / "utils.py").write_text("def utility(): pass")

    # Create subdirectory
    subdir = temp_dir / "module"
    subdir.mkdir()
    (subdir / "helper.py").write_text("def helper(): pass")

    # Create JavaScript files
    (temp_dir / "app.js").write_text('console.log("App")')

    # Create excluded directory
    node_modules = temp_dir / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.js").write_text("// Should be excluded")

    return str(temp_dir)
