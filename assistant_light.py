#!/usr/bin/env python3
"""
LIGHTWEIGHT TEXT-TO-CODE ASSISTANT - NO DEPENDENCIES
Pure Python standard library - NO installation needed!
Run: python assistant_light.py
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime

# ========== SIMPLE COLOR OUTPUT ==========
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def cprint(text, color):
    print(f"{color}{text}{Colors.RESET}")

# ========== SIMPLE PARSER ==========
class SimpleParser:
    def parse(self, text):
        text_lower = text.lower()
        result = {'intent': 'unknown', 'language': 'python', 'target': 'Generated'}
        
        # Dictionary commands
        dict_patterns = [
            (r'(define|what is|meaning of)\s+["\']?([a-z]+)["\']?', 'dictionary'),
            (r'synonyms?(?: for| of)?\s+["\']?([a-z]+)["\']?', 'synonyms'),
            (r'antonyms?(?: for| of)?\s+["\']?([a-z]+)["\']?', 'antonyms')
        ]
        
        for pattern, intent in dict_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['intent'] = 'dictionary'
                result['word'] = match.group(1) if intent != 'dictionary' else match.group(2)
                result['lookup_type'] = intent
                return result
        
        # Code commands
        if any(word in text_lower for word in ['create', 'make', 'generate', 'class', 'function']):
            result['intent'] = 'code'
            
            # Extract language
            if 'java' in text_lower:
                result['language'] = 'java'
            elif 'javascript' in text_lower or 'js' in text_lower:
                result['language'] = 'javascript'
            elif 'python' in text_lower or 'py' in text_lower:
                result['language'] = 'python'
            
            # Extract name (capitalized word)
            words = re.findall(r'[A-Z][a-z]+', text)
            if words:
                result['target'] = words[0]
            
            # Extract fields
            fields = re.findall(r'(\w+)\s+(\w+)', text)
            if fields:
                result['fields'] = [{'name': f[0], 'type': f[1]} for f in fields]
        
        return result

# ========== SIMPLE DICTIONARY ==========
class SimpleDictionary:
    def __init__(self):
        self.local_db = {
            'resilience': {
                'definitions': ['The capacity to recover quickly from difficulties; toughness.'],
                'synonyms': ['durability', 'strength', 'fortitude', 'toughness'],
                'antonyms': ['fragility', 'weakness', 'vulnerability']
            },
            'perseverance': {
                'definitions': ['Persistence in doing something despite difficulty or delay.'],
                'synonyms': ['persistence', 'determination', 'tenacity', 'diligence'],
                'antonyms': ['laziness', 'indifference', 'apathy']
            },
            'intelligent': {
                'definitions': ['Having or showing intelligence.'],
                'synonyms': ['smart', 'bright', 'clever', 'brilliant'],
                'antonyms': ['stupid', 'foolish', 'unintelligent']
            }
        }
    
    def lookup(self, word, lookup_type="definition"):
        word_lower = word.lower()
        
        if word_lower in self.local_db:
            return self.local_db[word_lower]
        
        # Simple fallback
        return {
            'definitions': [f'Definition of {word}'],
            'synonyms': ['similar', 'equivalent', 'counterpart'],
            'antonyms': ['opposite', 'contrary', 'reverse']
        }

# ========== SIMPLE CODE GENERATOR ==========
class SimpleCodeGen:
    def generate_java(self, name, fields=None):
        if not fields:
            fields = [{'name': 'id', 'type': 'int'}, {'name': 'name', 'type': 'String'}]
        
        code = f"public class {name} {{\n"
        for f in fields:
            code += f"    private {f['type']} {f['name']};\n"
        
        code += f"\n    public {name}() {{\n"
        for f in fields:
            if f['type'] == 'String':
                code += f"        this.{f['name']} = \"\";\n"
            elif f['type'] == 'int':
                code += f"        this.{f['name']} = 0;\n"
            else:
                code += f"        this.{f['name']} = null;\n"
        code += "    }\n"
        
        # Getters
        for f in fields:
            cap = f['name'][0].upper() + f['name'][1:]
            code += f"\n    public {f['type']} get{cap}() {{\n"
            code += f"        return this.{f['name']};\n    }}\n"
        
        code += "}"
        return code
    
    def generate_python(self, name, fields=None):
        if not fields:
            fields = [{'name': 'name'}, {'name': 'value'}]
        
        attrs = [f['name'] for f in fields]
        code = f"class {name}:\n"
        code += f"    def __init__(self, {', '.join(attrs)}):\n"
        for attr in attrs:
            code += f"        self.{attr} = {attr}\n"
        
        code += f"\n    def __str__(self):\n"
        code += f'        return f"{name}('
        for i, attr in enumerate(attrs):
            if i > 0:
                code += ", "
            code += f"{attr}={{self.{attr}}}"
        code += f')"\n'
        
        return code

# ========== MAIN ASSISTANT ==========
class LightweightAssistant:
    def __init__(self):
        self.parser = SimpleParser()
        self.dict = SimpleDictionary()
        self.codegen = SimpleCodeGen()
        
        print(f"{Colors.CYAN}╔══════════════════════════════════════════╗")
        print(f"{Colors.YELLOW}║   LIGHTWEIGHT ASSISTANT - READY!       ║")
        print(f"{Colors.CYAN}║   (No Installation Needed)              ║")
        print(f"╚══════════════════════════════════════════╝")
        print(f"\n{Colors.GREEN}Try: 'Create a Java class User'")
        print(f"{Colors.GREEN}Or:  'Define resilience'")
        print(f"{Colors.GREEN}Or:  'Synonyms for intelligent'")
        print(f"{Colors.CYAN}Type 'quit' to exit")
        print("-" * 40)
    
    def run(self):
        while True:
            try:
                cmd = input(f"\n{Colors.YELLOW}💬 > {Colors.RESET}").strip()
                
                if cmd.lower() in ['quit', 'exit']:
                    print(f"{Colors.CYAN}Goodbye! 👋")
                    break
                
                if not cmd:
                    continue
                
                # Parse command
                parsed = self.parser.parse(cmd)
                
                # Handle dictionary
                if parsed['intent'] == 'dictionary':
                    word = parsed.get('word', 'example')
                    lookup_type = parsed.get('lookup_type', 'definition')
                    info = self.dict.lookup(word, lookup_type)
                    
                    print(f"\n{Colors.CYAN}📚 {word.upper()}:")
                    print(f"{Colors.GREEN}Definitions:")
                    for i, d in enumerate(info['definitions'], 1):
                        print(f"  {i}. {d}")
                    print(f"{Colors.BLUE}Synonyms: {', '.join(info['synonyms'][:5])}")
                    print(f"{Colors.MAGENTA}Antonyms: {', '.join(info['antonyms'][:3])}")
                
                # Handle code generation
                elif parsed['intent'] == 'code':
                    lang = parsed['language']
                    name = parsed['target']
                    fields = parsed.get('fields', [])
                    
                    print(f"\n{Colors.GREEN}Generating {lang} code...")
                    
                    if lang == 'java':
                        code = self.codegen.generate_java(name, fields)
                    else:  # python default
                        code = self.codegen.generate_python(name, fields)
                    
                    print(f"\n{Colors.CYAN}📄 {name}.{'java' if lang == 'java' else 'py'}:")
                    print(f"{Colors.WHITE}{code}")
                
                else:
                    print(f"{Colors.YELLOW}Try: 'Create a class' or 'Define [word]'")
            
            except KeyboardInterrupt:
                print(f"\n{Colors.CYAN}Goodbye! 👋")
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}")

# ========== START ==========
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    assistant = LightweightAssistant()
    assistant.run()