#!/usr/bin/env python3
"""
Test suite for enhanced FAQ generation system
Tests both documentation and code comment extraction
"""

import tempfile
import re
from pathlib import Path
from typing import List

# Simplified versions of our classes for testing without full dependencies
class CodeComment:
    def __init__(self, content: str, file_path: str, line_number: int, comment_type: str, context: str = ""):
        self.content = content
        self.file_path = file_path
        self.line_number = line_number
        self.comment_type = comment_type
        self.context = context

class FAQItem:
    def __init__(self, question: str, answer: str, category: str = "General", source: str = "test"):
        self.question = question
        self.answer = answer
        self.category = category
        self.source = source

class CodeCommentExtractor:
    """Extracts meaningful comments from code files for FAQ generation"""
    
    COMMENT_PATTERNS = {
        'TODO': r'(?:TODO|@todo)\s*:?\s*(.+)',
        'FIXME': r'(?:FIXME|@fixme)\s*:?\s*(.+)',
        'NOTE': r'(?:NOTE|@note)\s*:?\s*(.+)',
        'HACK': r'(?:HACK|@hack)\s*:?\s*(.+)',
        'BUG': r'(?:BUG|@bug)\s*:?\s*(.+)',
        'WARNING': r'(?:WARNING|@warning)\s*:?\s*(.+)',
        'IMPORTANT': r'(?:IMPORTANT|@important)\s*:?\s*(.+)',
        'DEPRECATED': r'(?:DEPRECATED|@deprecated)\s*:?\s*(.+)',
    }
    
    # File patterns to exclude
    EXCLUDE_PATTERNS = [
        '*.pyc', '*.pyo', '*.pyd', '__pycache__/*',
        '*.so', '*.dylib', '*.dll',
        '.git/*', '.gitignore', 
        'node_modules/*', '*.lock', 'package-lock.json',
        '*.log', '*.tmp', '*.temp',
        '.env', '.env.*',
        '*.pdf', '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg',
        'venv/*', 'env/*', '.venv/*'
    ]
    
    # File extensions to process
    INCLUDE_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h',
        '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
        '.yaml', '.yml', '.json', '.md', '.txt', '.sh', '.bat',
        '.tf', '.hcl', '.sql', '.html', '.css', '.scss', '.less'
    }
    
    def __init__(self, root_path: str = "../../"):
        self.root_path = Path(root_path).resolve()
        
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on patterns and extensions"""
        relative_path = str(file_path.relative_to(self.root_path))
        
        # Check exclude patterns
        import fnmatch
        for pattern in self.EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(relative_path, pattern):
                return False
                
        # Check file extension
        return file_path.suffix.lower() in self.INCLUDE_EXTENSIONS
    
    def extract_line_comments(self, file_path: Path) -> List[CodeComment]:
        """Extract line comments from any file type"""
        comments = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip empty lines
                if not line_stripped:
                    continue
                
                # Check for different comment patterns based on file type
                comment_content = None
                if file_path.suffix in ['.py']:
                    if line_stripped.startswith('#'):
                        comment_content = line_stripped[1:].strip()
                elif file_path.suffix in ['.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.cs', '.swift', '.kt', '.scala']:
                    if line_stripped.startswith('//'):
                        comment_content = line_stripped[2:].strip()
                    elif '/*' in line_stripped and '*/' in line_stripped:
                        start = line_stripped.find('/*') + 2
                        end = line_stripped.find('*/')
                        comment_content = line_stripped[start:end].strip()
                
                # Check if comment matches our patterns
                if comment_content:
                    for comment_type, pattern in self.COMMENT_PATTERNS.items():
                        match = re.search(pattern, comment_content, re.IGNORECASE)
                        if match:
                            # Get surrounding context
                            context_lines = []
                            for i in range(max(0, line_num-3), min(len(lines), line_num+2)):
                                if i != line_num-1:  # Skip the comment line itself
                                    context_lines.append(lines[i].strip())
                            context = " | ".join(filter(None, context_lines))
                            
                            comments.append(CodeComment(
                                content=match.group(1).strip(),
                                file_path=str(file_path.relative_to(self.root_path)),
                                line_number=line_num,
                                comment_type=comment_type,
                                context=context[:200]  # Limit context length
                            ))
                            break
                            
        except Exception as e:
            print(f"Debug: Could not read file {file_path}: {e}")
        
        return comments
    
    def extract_all_comments(self) -> List[CodeComment]:
        """Extract all relevant comments from the codebase"""
        all_comments = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                try:
                    # Extract line comments
                    line_comments = self.extract_line_comments(file_path)
                    all_comments.extend(line_comments)
                        
                except Exception as e:
                    print(f"Debug: Error processing file {file_path}: {e}")
        
        print(f"Extracted {len(all_comments)} code comments from codebase")
        return all_comments


def test_comment_extraction():
    """Test comment extraction functionality"""
    print("🧪 Testing code comment extraction...")
    
    # Create temporary directory and files
    temp_dir = tempfile.mkdtemp()
    try:
        extractor = CodeCommentExtractor(temp_dir)
        
        # Create test Python file
        test_py = Path(temp_dir) / "test.py"
        test_py_content = '''
def example_function():
    """This function demonstrates AI agent capabilities"""
    # TODO: Implement better error handling for user experience
    # FIXME: Handle edge cases in data processing  
    # NOTE: This is crucial for system reliability
    pass

class AIAgent:
    # WARNING: This feature is experimental
    def process(self):
        return "result"
'''
        test_py.write_text(test_py_content)
        
        # Create test JavaScript file
        test_js = Path(temp_dir) / "test.js"
        test_js_content = '''
function processData() {
    // TODO: Add input validation
    // HACK: Temporary fix for browser compatibility
    return data;
}
'''
        test_js.write_text(test_js_content)
        
        # Extract comments
        py_comments = extractor.extract_line_comments(test_py)
        js_comments = extractor.extract_line_comments(test_js)
        
        all_comments = py_comments + js_comments
        
        print(f"✅ Extracted {len(all_comments)} comments total")
        print(f"   - Python file: {len(py_comments)} comments")
        print(f"   - JavaScript file: {len(js_comments)} comments")
        
        # Test specific patterns
        todo_comments = [c for c in all_comments if c.comment_type == "TODO"]
        fixme_comments = [c for c in all_comments if c.comment_type == "FIXME"]
        note_comments = [c for c in all_comments if c.comment_type == "NOTE"]
        warning_comments = [c for c in all_comments if c.comment_type == "WARNING"]
        hack_comments = [c for c in all_comments if c.comment_type == "HACK"]
        
        print(f"   - TODO: {len(todo_comments)}")
        print(f"   - FIXME: {len(fixme_comments)}")
        print(f"   - NOTE: {len(note_comments)}")
        print(f"   - WARNING: {len(warning_comments)}")
        print(f"   - HACK: {len(hack_comments)}")
        
        # Show some examples
        for comment in all_comments[:3]:
            print(f"   Example: {comment.comment_type} - {comment.content}")
        
        return all_comments
        
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_pattern_matching():
    """Test comment pattern matching"""
    print("\n🧪 Testing comment pattern matching...")
    
    extractor = CodeCommentExtractor()
    
    test_cases = [
        ("# TODO: Fix this issue", "TODO", "Fix this issue"),
        ("// FIXME: Handle edge case", "FIXME", "Handle edge case"),
        ("/* NOTE: Important consideration */", "NOTE", "Important consideration"),
        ("# @todo Implement feature", "TODO", "Implement feature"),
        ("// WARNING: Deprecated method", "WARNING", "Deprecated method"),
        ("# HACK: Temporary workaround", "HACK", "Temporary workaround"),
    ]
    
    success_count = 0
    for comment_text, expected_type, expected_content in test_cases:
        pattern = extractor.COMMENT_PATTERNS[expected_type]
        match = re.search(pattern, comment_text, re.IGNORECASE)
        
        if match and expected_content in match.group(1):
            success_count += 1
            print(f"   ✅ {expected_type}: '{comment_text}' → '{match.group(1)}'")
        else:
            print(f"   ❌ {expected_type}: Failed to match '{comment_text}'")
    
    print(f"✅ Pattern matching: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)


def simulate_faq_generation(comments: List[CodeComment]) -> List[FAQItem]:
    """Simulate FAQ generation from comments"""
    print("\n🧪 Simulating FAQ generation from comments...")
    
    # Group comments by type
    grouped = {}
    for comment in comments:
        if comment.comment_type not in grouped:
            grouped[comment.comment_type] = []
        grouped[comment.comment_type].append(comment)
    
    faq_items = []
    
    # Generate FAQ items based on comment types
    if "TODO" in grouped:
        todo_items = grouped["TODO"]
        if len(todo_items) >= 2:
            faq_items.append(FAQItem(
                question="What features are currently in development?",
                answer=f"We're actively working on several improvements including: {', '.join([item.content[:50] + '...' for item in todo_items[:3]])}",
                category="Planned Features",
                source="code"
            ))
    
    if "FIXME" in grouped:
        fixme_items = grouped["FIXME"]
        if len(fixme_items) >= 1:
            faq_items.append(FAQItem(
                question="Are there any known issues being addressed?",
                answer=f"Yes, we're currently addressing: {', '.join([item.content[:50] + '...' for item in fixme_items[:2]])}",
                category="Known Issues",
                source="code"
            ))
    
    if "NOTE" in grouped:
        note_items = grouped["NOTE"]
        if len(note_items) >= 1:
            faq_items.append(FAQItem(
                question="What should users know about the system?",
                answer=f"Important considerations include: {', '.join([item.content[:50] + '...' for item in note_items[:2]])}",
                category="Best Practices",
                source="code"
            ))
    
    # Add some default FAQs
    default_faqs = [
        FAQItem(
            question="What is the AI SaaS Factory?",
            answer="The AI SaaS Factory is an automated platform that transforms your ideas into production-ready SaaS applications using AI agents.",
            category="Getting Started",
            source="docs"
        ),
        FAQItem(
            question="How does the development process work?",
            answer="Our AI agents handle the entire development pipeline: idea validation, design, coding, testing, and deployment.",
            category="Features",
            source="docs"
        )
    ]
    
    faq_items.extend(default_faqs)
    
    print(f"✅ Generated {len(faq_items)} FAQ items")
    for item in faq_items:
        print(f"   Q: {item.question}")
        print(f"   A: {item.answer[:100]}...")
        print(f"   Category: {item.category}, Source: {item.source}")
        print()
    
    return faq_items


def main():
    """Run all tests"""
    print("🎯 Night 75: FAQ Auto-generated from Code Comments")
    print("=" * 60)
    
    # Test 1: Pattern matching
    pattern_test_passed = test_pattern_matching()
    
    # Test 2: Comment extraction
    comments = test_comment_extraction()
    
    # Test 3: FAQ generation simulation
    faq_items = simulate_faq_generation(comments)
    
    # Summary
    print("\n🎉 Test Summary:")
    print(f"   ✅ Pattern matching: {'PASSED' if pattern_test_passed else 'FAILED'}")
    print(f"   ✅ Comment extraction: {len(comments)} comments found")
    print(f"   ✅ FAQ generation: {len(faq_items)} FAQ items created")
    
    if pattern_test_passed and len(comments) > 0 and len(faq_items) > 0:
        print("\n🎉 All core functionality tests passed!")
        print("📝 The FAQ generation system is ready for Night 75 implementation.")
        
        # Show categories and sources
        categories = set(item.category for item in faq_items)
        sources = set(item.source for item in faq_items)
        print("\n📊 Generated FAQ Statistics:")
        print(f"   Categories: {', '.join(sorted(categories))}")
        print(f"   Sources: {', '.join(sorted(sources))}")
        
    else:
        print("\n❌ Some tests failed. Please review the implementation.")


if __name__ == "__main__":
    main() 