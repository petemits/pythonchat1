#!/usr/bin/env python3
"""
LIGHTWEIGHT TEXT-TO-CODE ASSISTANT
No external dependencies - pure Python standard library
Run: python assistant_light.py
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Any, Optional

# ========== SIMPLE COLOR OUTPUT ==========
class Colors:
    """Simple color codes for terminal."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def cprint(text, color):
    """Print colored text."""
    print(f"{color}{text}{Colors.RESET}")

# ========== LIGHTWEIGHT NLP PARSER ==========
class LightweightNLP:
    """Simple NLP parser using regex patterns only."""
    
    def __init__(self):
        self.code_patterns = [
            (r'(create|make|generate|write)\s+(?:a\s+)?(java|python|javascript|c\+\+|c#)\s+(?:class|function)\s+(?:called|named|)\s*["\']?([A-Za-z_][A-Za-z0-9_]*)["\']?', 'class'),
            (r'(create|make|generate)\s+(?:a\s+)?(java|python|javascript)\s+function\s+(?:called|named|)\s*["\']?([A-Za-z_][A-Za-z0-9_]*)["\']?', 'function'),
            (r'(?:class|function)\s+["\']?([A-Za-z_][A-Za-z0-9_]*)["\']?\s+with\s+(?:fields|attributes)\s+(.+)', 'with_fields')
        ]
        
        self.dict_patterns = [
            (r'(define|what is|meaning of|definition of)\s+["\']?([A-Za-z]+)["\']?', 'definition'),
            (r'synonyms?(?: for| of)?\s+["\']?([A-Za-z]+)["\']?', 'synonyms'),
            (r'antonyms?(?: for| of)?\s+["\']?([A-Za-z]+)["\']?', 'antonyms')
        ]
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse user input using regex patterns."""
        text_lower = text.lower()
        result = {
            'intent': 'unknown',
            'language': None,
            'action': None,
            'target': None,
            'parameters': {},
            'words': re.findall(r'\b[a-zA-Z]+\b', text_lower)
        }
        
        # Check for dictionary intent first
        for pattern, intent_type in self.dict_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                result['intent'] = 'dictionary'
                result['parameters']['word'] = match.group(1) if intent_type != 'definition' else match.group(2)
                result['parameters']['lookup_type'] = intent_type
                return result
        
        # Check for code generation intent
        for pattern, action in self.code_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                result['intent'] = 'code'
                
                if action == 'with_fields':
                    result['target'] = match.group(1)
                    # Parse fields like "name String, age int"
                    fields_text = match.group(2)
                    fields = []
                    for field_match in re.finditer(r'(\w+)\s+(\w+)', fields_text):
                        fields.append({'name': field_match.group(1), 'type': field_match.group(2)})
                    if fields:
                        result['parameters']['fields'] = fields
                else:
                    # Extract language and target name
                    groups = match.groups()
                    if len(groups) >= 3:
                        result['language'] = groups[1]
                        result['target'] = groups[2]
                    elif len(groups) >= 2:
                        result['language'] = 'python'  # Default
                        result['target'] = groups[1]
                
                result['action'] = action
                
                # Determine language if not specified
                if not result.get('language'):
                    if 'java' in text_lower:
                        result['language'] = 'java'
                    elif 'javascript' in text_lower or 'js' in text_lower:
                        result['language'] = 'javascript'
                    elif 'c++' in text_lower or 'cpp' in text_lower:
                        result['language'] = 'cpp'
                    elif 'c#' in text_lower or 'csharp' in text_lower:
                        result['language'] = 'csharp'
                    else:
                        result['language'] = 'python'  # Default
                
                return result
        
        # Fallback: If no pattern matches but has code keywords
        code_keywords = {'create', 'make', 'generate', 'class', 'function', 'code'}
        if any(keyword in text_lower for keyword in code_keywords):
            result['intent'] = 'code'
            result['language'] = 'python'
            result['action'] = 'class'
            # Extract a capitalized word as target
            words = re.findall(r'[A-Z][a-z]+', text)
            if words:
                result['target'] = words[0]
            else:
                result['target'] = 'GeneratedCode'
        
        return result

# ========== LIGHTWEIGHT DICTIONARY ==========
class LightweightDictionary:
    """Dictionary using simple local database and online fallback."""
    
    def __init__(self):
        # Local word database (expanded)
        self.local_db = {
            'resilience': {
                'definitions': ['The capacity to recover quickly from difficulties; toughness.'],
                'synonyms': ['durability', 'strength', 'fortitude', 'toughness', 'hardiness'],
                'antonyms': ['fragility', 'weakness', 'vulnerability', 'frailty'],
                'examples': ['Her resilience in the face of adversity was inspiring.', 'The material showed great resilience under pressure.']
            },
            'ephemeral': {
                'definitions': ['Lasting for a very short time.', 'Transient or fleeting in nature.'],
                'synonyms': ['transient', 'fleeting', 'short-lived', 'temporary', 'momentary'],
                'antonyms': ['permanent', 'enduring', 'everlasting', 'perpetual', 'eternal'],
                'examples': ['The beauty of cherry blossoms is ephemeral.', 'Fame can be an ephemeral thing.']
            },
            'perseverance': {
                'definitions': ['Persistence in doing something despite difficulty or delay.', 'Steady persistence in a course of action.'],
                'synonyms': ['persistence', 'determination', 'tenacity', 'diligence', 'steadfastness'],
                'antonyms': ['laziness', 'indifference', 'apathy', 'neglect'],
                'examples': ['Success comes to those who show perseverance.', 'Through perseverance, he mastered the skill.']
            },
            'intelligent': {
                'definitions': ['Having or showing intelligence, especially of a high level.', 'Able to acquire and apply knowledge.'],
                'synonyms': ['smart', 'bright', 'clever', 'brilliant', 'knowledgeable'],
                'antonyms': ['stupid', 'foolish', 'unintelligent', 'ignorant', 'dumb'],
                'examples': ['She asked intelligent questions during the lecture.', 'An intelligent approach to problem-solving.']
            },
            'beautiful': {
                'definitions': ['Pleasing the senses or mind aesthetically.', 'Having qualities that delight the senses.'],
                'synonyms': ['attractive', 'lovely', 'gorgeous', 'stunning', 'exquisite'],
                'antonyms': ['ugly', 'unattractive', 'hideous', 'plain', 'unpleasant'],
                'examples': ['The sunset was incredibly beautiful.', 'She has a beautiful singing voice.']
            },
            'courage': {
                'definitions': ['The ability to do something that frightens one.', 'Strength in the face of pain or grief.'],
                'synonyms': ['bravery', 'valor', 'fearlessness', 'heroism', 'boldness'],
                'antonyms': ['cowardice', 'fear', 'timidity', 'weakness', 'spinelessness'],
                'examples': ['It took great courage to stand up to the bully.', 'He showed courage in difficult times.']
            },
            'knowledge': {
                'definitions': ['Facts, information, and skills acquired through experience.', 'Awareness or familiarity gained by experience.'],
                'synonyms': ['understanding', 'wisdom', 'expertise', 'comprehension', 'awareness'],
                'antonyms': ['ignorance', 'unawareness', 'inexperience', 'naivety'],
                'examples': ['He has extensive knowledge of ancient history.', 'Sharing knowledge helps everyone grow.']
            },
            'innovation': {
                'definitions': ['The action or process of innovating.', 'A new method, idea, or product.'],
                'synonyms': ['invention', 'creativity', 'novelty', 'originality', 'breakthrough'],
                'antonyms': ['stagnation', 'tradition', 'conformity', 'imitation'],
                'examples': ['Technological innovation drives progress.', 'The company is known for its innovation.']
            }
        }
        cprint("✓ Lightweight dictionary initialized", Colors.GREEN)
    
    def lookup(self, word: str, lookup_type: str = "definition") -> Dict[str, Any]:
        """Look up word in local database with online fallback."""
        word_lower = word.lower()
        
        result = {
            'word': word,
            'definitions': [],
            'synonyms': [],
            'antonyms': [],
            'examples': [],
            'source': 'Local Database'
        }
        
        # Check local database first
        if word_lower in self.local_db:
            result.update(self.local_db[word_lower])
            return result
        
        # Try online lookup as fallback
        online_data = self._online_lookup(word)
        if online_data:
            result.update(online_data)
            result['source'] = 'Online API'
        else:
            # Generate generic response
            self._generate_generic(word, result, lookup_type)
        
        return result
    
    def _online_lookup(self, word: str) -> Optional[Dict]:
        """Simple online lookup using urllib (no requests library needed)."""
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            request = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(request, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data:
                        entry = data[0]
                        result = {
                            'definitions': [],
                            'synonyms': [],
                            'antonyms': [],
                            'examples': []
                        }
                        
                        # Extract meanings (first 2 only)
                        for meaning in entry.get('meanings', [])[:2]:
                            for definition in meaning.get('definitions', [])[:2]:
                                if 'definition' in definition:
                                    result['definitions'].append(definition['definition'])
                                if 'example' in definition:
                                    result['examples'].append(definition['example'])
                            
                            result['synonyms'].extend(meaning.get('synonyms', [])[:5])
                            result['antonyms'].extend(meaning.get('antonyms', [])[:5])
                        
                        return result
        
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def _generate_generic(self, word: str, result: Dict, lookup_type: str):
        """Generate generic word information."""
        if lookup_type == 'definition':
            result['definitions'] = [f'The word "{word}" - look it up in a comprehensive dictionary.']
        elif lookup_type == 'synonyms':
            result['definitions'] = [f'Word: {word}']
            result['synonyms'] = ['similar', 'equivalent', 'counterpart', 'match', 'parallel']
        elif lookup_type == 'antonyms':
            result['definitions'] = [f'Word: {word}']
            result['antonyms'] = ['opposite', 'contrary', 'reverse', 'inverse', 'contrast']
        
        result['examples'] = [f'Try using "{word}" in your own sentence.']
        result['synonyms'] = result.get('synonyms', ['example', 'sample', 'instance'])
        result['antonyms'] = result.get('antonyms', ['opposite', 'contrary', 'reverse'])
    
    def format_output(self, word_info: Dict) -> str:
        """Format word information nicely."""
        output = []
        output.append(f"{Colors.CYAN}📚 {word_info['word'].upper()}")
        output.append(f"{Colors.CYAN}────────────────────────────────────────")
        
        if word_info['definitions']:
            output.append(f"{Colors.GREEN}📖 Definitions:")
            for i, definition in enumerate(word_info['definitions'][:3], 1):
                output.append(f"{Colors.WHITE}  {i}. {definition}")
        
        if word_info['synonyms']:
            output.append(f"{Colors.BLUE}🔄 Synonyms:")
            synonyms_text = ", ".join(word_info['synonyms'][:8])
            # Wrap long lines
            if len(synonyms_text) > 60:
                parts = [synonyms_text[i:i+60] for i in range(0, len(synonyms_text), 60)]
                output.append(f"{Colors.WHITE}  " + ("\n  ".join(parts)))
            else:
                output.append(f"{Colors.WHITE}  {synonyms_text}")
        
        if word_info['antonyms']:
            output.append(f"{Colors.MAGENTA}⚡ Antonyms:")
            antonyms_text = ", ".join(word_info['antonyms'][:8])
            if len(antonyms_text) > 60:
                parts = [antonyms_text[i:i+60] for i in range(0, len(antonyms_text), 60)]
                output.append(f"{Colors.WHITE}  " + ("\n  ".join(parts)))
            else:
                output.append(f"{Colors.WHITE}  {antonyms_text}")
        
        if word_info['examples']:
            output.append(f"{Colors.YELLOW}💡 Examples:")
            for i, example in enumerate(word_info['examples'][:2], 1):
                output.append(f"{Colors.WHITE}  {i}. {example}")
        
        output.append(f"{Colors.CYAN}\nSource: {word_info.get('source', 'Unknown')}")
        return "\n".join(output)

# ========== LIGHTWEIGHT CODE GENERATOR ==========
class LightweightCodeGenerator:
    """Code generator using string templates (no Jinja2 needed)."""
    
    def __init__(self):
        cprint("✓ Lightweight code generator initialized", Colors.GREEN)
    
    def generate(self, parsed: Dict) -> Dict[str, Any]:
        """Generate code using string templates."""
        language = parsed.get('language', 'python')
        action = parsed.get('action', 'class')
        target = parsed.get('target', 'GeneratedCode')
        params = parsed.get('parameters', {})
        
        result = {
            'language': language,
            'type': action,
            'name': target,
            'code': '',
            'success': True,
            'message': f'Generated {action} "{target}" in {language}'
        }
        
        try:
            if language == 'java':
                result['code'] = self._generate_java(target, action, params)
            elif language == 'python':
                result['code'] = self._generate_python(target, action, params)
            elif language == 'javascript':
                result['code'] = self._generate_javascript(target, action, params)
            elif language == 'cpp':
                result['code'] = self._generate_cpp(target, action, params)
            elif language == 'csharp':
                result['code'] = self._generate_csharp(target, action, params)
            else:
                result['code'] = self._generate_generic(target, language, action)
        except Exception as e:
            result['success'] = False
            result['message'] = f'Error: {str(e)}'
            result['code'] = f'// Error generating code: {str(e)}'
        
        return result
    
    def _generate_java(self, name: str, action: str, params: Dict) -> str:
        """Generate Java code."""
        fields = params.get('fields', [{'name': 'id', 'type': 'int'}, {'name': 'name', 'type': 'String'}])
        
        code = f"public class {name} {{\n"
        
        # Fields
        for field in fields:
            code += f"    private {field['type']} {field['name']};\n"
        
        code += "\n    // Constructors\n"
        code += f"    public {name}() {{\n"
        for field in fields:
            if field['type'] == 'String':
                code += f"        this.{field['name']} = \"\";\n"
            elif field['type'] == 'int':
                code += f"        this.{field['name']} = 0;\n"
            else:
                code += f"        this.{field['name']} = null;\n"
        code += "    }\n\n"
        
        # Parameterized constructor
        param_list = ", ".join([f"{f['type']} {f['name']}" for f in fields])
        code += f"    public {name}({param_list}) {{\n"
        for field in fields:
            code += f"        this.{field['name']} = {field['name']};\n"
        code += "    }\n\n"
        
        # Getters and setters
        code += "    // Getters and setters\n"
        for field in fields:
            cap_name = field['name'][0].upper() + field['name'][1:]
            code += f"    public {field['type']} get{cap_name}() {{\n"
            code += f"        return this.{field['name']};\n    }}\n\n"
            code += f"    public void set{cap_name}({field['type']} {field['name']}) {{\n"
            code += f"        this.{field['name']} = {field['name']};\n    }}\n\n"
        
        # toString method
        code += "    @Override\n    public String toString() {\n"
        code += f'        return "{name}{" + \n'
        for i, field in enumerate(fields):
            if i == 0:
                code += f'               "{field["name"]}=" + {field["name"]}'
            else:
                code += f' + ", {field["name"]}=" + {field["name"]}'
        code += " + \"}\";\n    }\n}\n"
        
        return code
    
    def _generate_python(self, name: str, action: str, params: Dict) -> str:
        """Generate Python code."""
        if action == 'class':
            attributes = [f['name'] for f in params.get('fields', [{'name': 'name'}, {'name': 'value'}])]
            
            code = f"class {name}:\n"
            code += f'    """{name} class - auto-generated"""\n\n'
            code += f"    def __init__(self"
            if attributes:
                code += f", {', '.join(attributes)}"
            code += "):\n"
            code += f'        """Initialize {name}"""\n'
            for attr in attributes:
                code += f"        self.{attr} = {attr}\n"
            
            code += f"\n    def display(self):\n"
            code += f'        """Display object info"""\n'
            code += f'        print(f"{name}: ")\n'
            for attr in attributes:
                code += f'        print(f"  {attr}: {{self.{attr}}}")\n'
            
            code += f"\n    def __str__(self):\n"
            code += f'        """String representation"""\n'
            code += f'        return f"{name}('
            for i, attr in enumerate(attributes):
                if i > 0:
                    code += ", "
                code += f"{attr}={{self.{attr}}}"
            code += f')"\n\n'
            
            code += f"# Example usage\n"
            code += f"if __name__ == '__main__':\n"
            code += f"    obj = {name}("
            for i, attr in enumerate(attributes):
                if i > 0:
                    code += ", "
                code += f'{attr}="test_{attr}"'
            code += f")\n"
            code += f"    print(obj)\n"
            code += f"    obj.display()\n"
            
            return code
        
        else:  # Function
            return f'''def {name}(data):
    """Process data - auto-generated function"""
    print(f"Processing: {{data}}")
    return data.upper()

# Example usage
if __name__ == "__main__":
    result = {name}("test input")
    print(f"Result: {{result}}")'''
    
    def _generate_javascript(self, name: str, action: str, params: Dict) -> str:
        """Generate JavaScript code."""
        if action == 'class':
            return f"""class {name} {{
    constructor(name, value) {{
        this.name = name;
        this.value = value;
    }}
    
    display() {{
        console.log(`${{this.name}}: ${{this.value}}`);
    }}
    
    toJSON() {{
        return {{
            name: this.name,
            value: this.value
        }};
    }}
}}

// Example usage
const instance = new {name}('Test', 42);
instance.display();
console.log(instance.toJSON());"""
        else:
            return f"""function {name}(input) {{
    console.log(`Processing: ${{input}}`);
    return input.toUpperCase();
}}

// Example usage
const result = {name}('example');
console.log(`Result: ${{result}}`);"""
    
    def _generate_cpp(self, name: str, action: str, params: Dict) -> str:
        """Generate C++ code."""
        return f"""// {name}.cpp - Auto-generated C++ code
#include <iostream>
#include <string>

using namespace std;

class {name} {{
private:
    string name;
    int value;
    
public:
    // Constructor
    {name}(string n, int v) : name(n), value(v) {{}}
    
    // Display method
    void display() {{
        cout << name << ": " << value << endl;
    }}
    
    // Getter methods
    string getName() {{ return name; }}
    int getValue() {{ return value; }}
}};

int main() {{
    {name} obj("Test", 42);
    obj.display();
    return 0;
}}"""
    
    def _generate_csharp(self, name: str, action: str, params: Dict) -> str:
        """Generate C# code."""
        return f"""using System;

namespace AutoGenerated
{{
    public class {name}
    {{
        public string Name {{ get; set; }}
        public int Value {{ get; set; }}
        
        public {name}(string name, int value)
        {{
            Name = name;
            Value = value;
        }}
        
        public void Display()
        {{
            Console.WriteLine($"{{Name}}: {{Value}}");
        }}
    }}
    
    class Program
    {{
        static void Main(string[] args)
        {{
            {name} obj = new {name}("Test", 42);
            obj.Display();
        }}
    }}
}}"""
    
    def _generate_generic(self, name: str, language: str, action: str) -> str:
        """Generate generic code template."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""// Auto-generated {action} in {language}
// Name: {name}
// Generated: {timestamp}
// Language: {language}

{action} {name} {{
    // TODO: Implement your {action} logic here
    
    // Example structure for {language}
    public void exampleMethod() {{
        // Your code here
    }}
}}

// Usage example:
// {name} instance = new {name}();
// instance.exampleMethod();"""
    
    def format_output(self, result: Dict) -> str:
        """Format code output."""
        if not result['success']:
            return f"{Colors.RED}❌ {result['message']}\n\n{result['code']}"
        
        extensions = {
            'java': 'java',
            'python': 'py',
            'javascript': 'js',
            'cpp': 'cpp',
            'csharp': 'cs',
            'csharp': 'cs'
        }
        
        ext = extensions.get(result['language'], 'txt')
        
        output = []
        output.append(f"{Colors.GREEN}✅ {result['message']}")
        output.append(f"{Colors.CYAN}════════════════════════════════════════════════════")
        output.append(f"{Colors.YELLOW}📁 File: {result['name']}.{ext}")
        output.append(f"{Colors.YELLOW}📝 Type: {result['type']}")
        output.append(f"{Colors.YELLOW}💻 Language: {result['language']}")
        output.append(f"{Colors.CYAN}────────────────────────────────────────────────────────")
        output.append(f"{Colors.WHITE}{result['code']}")
        output.append(f"{Colors.CYAN}════════════════════════════════════════════════════")
        
        return "\n".join(output)

# ========== MAIN ASSISTANT ==========
class LightweightAssistant:
    """Main lightweight assistant."""
    
    def __init__(self):
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════╗")
        print(f"{Colors.YELLOW}║   LIGHTWEIGHT TEXT-TO-CODE ASSISTANT               ║")
        print(f"{Colors.CYAN}║   (No Dependencies - Pure Python)                    ║")
        print(f"╚══════════════════════════════════════════════════════╝{Colors.RESET}")
        
        self.nlp = LightweightNLP()
        self.dictionary = LightweightDictionary()
        self.code_gen = LightweightCodeGenerator()
        self.history = []
        self.running = True
        
        self._show_help()
    
    def _show_help(self):
        """Show help information."""
        help_text = f"""
{Colors.GREEN}🎯 READY TO USE! No installation needed.{Colors.WHITE}

{Colors.YELLOW}📚 AVAILABLE COMMANDS:{Colors.WHITE}

🔧 {Colors.CYAN}CODE GENERATION:{Colors.WHITE}
  • "Create a Java class called User"
  • "Make a Python function named calculate"
  • "Generate a JavaScript class named Car"
  • "Create class Student with fields id int, name String"
  • "Make a Python class Person with name, age, email"

📖 {Colors.CYAN}DICTIONARY:{Colors.WHITE}
  • "Define resilience"
  • "What is ephemeral?"
  • "Synonyms for intelligent"
  • "Antonyms of generous"
  • "Meaning of perseverance"

🎮 {Colors.CYAN}SYSTEM:{Colors.WHITE}
  • {Colors.YELLOW}help{Colors.WHITE}    - Show this message
  • {Colors.YELLOW}history{Colors.WHITE} - Show conversation history
  • {Colors.YELLOW}clear{Colors.WHITE}   - Clear screen
  • {Colors.YELLOW}quit{Colors.WHITE}    - Exit program

{Colors.GREEN}📝 EXAMPLES:{Colors.WHITE}
  > create a Python class named Student
  > define perseverance
  > make a Java class called Product
  > synonyms for beautiful
  > create class User with fields id int, name String

{Colors.CYAN}────────────────────────────────────────────────────────
"""
        print(help_text)
    
    def process_input(self, user_input: str) -> Optional[str]:
        """Process user input."""
        user_input_lower = user_input.lower().strip()
        
        # System commands
        if user_input_lower in ['quit', 'exit', 'bye']:
            self.running = False
            return f"{Colors.CYAN}👋 Goodbye! Thanks for using the assistant."
        
        if user_input_lower in ['help', '?']:
            self._show_help()
            return None
        
        if user_input_lower in ['history', 'hist']:
            return self._show_history()
        
        if user_input_lower in ['clear', 'cls']:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Colors.CYAN}Screen cleared. Type 'help' for commands.{Colors.RESET}")
            return None
        
        # Parse input
        parsed = self.nlp.parse(user_input)
        
        # Route based on intent
        if parsed['intent'] == 'dictionary':
            return self._handle_dictionary(parsed)
        elif parsed['intent'] == 'code':
            return self._handle_code(parsed)
        else:
            return self._handle_unknown(user_input)
    
    def _handle_dictionary(self, parsed: Dict) -> str:
        """Handle dictionary lookup."""
        word = parsed['parameters'].get('word')
        
        if not word and parsed['words']:
            # Use the longest word that's not a common word
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were'}
            for w in parsed['words']:
                if w not in common_words and len(w) > 2:
                    word = w
                    break
        
        if not word:
            return f"{Colors.RED}❌ Please specify a word.{Colors.WHITE}\nExample: 'Define resilience'"
        
        print(f"{Colors.MAGENTA}🔍 Looking up '{word}'...")
        
        # Perform lookup
        lookup_type = parsed['parameters'].get('lookup_type', 'definition')
        word_info = self.dictionary.lookup(word, lookup_type)
        
        # Add to history
        self.history.append({
            'type': 'dictionary',
            'word': word,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        return self.dictionary.format_output(word_info)
    
    def _handle_code(self, parsed: Dict) -> str:
        """Handle code generation."""
        if not parsed.get('target'):
            # Extract a capitalized word
            for word in parsed['words']:
                if word[0].isupper():
                    parsed['target'] = word
                    break
            
            if not parsed.get('target'):
                parsed['target'] = 'GeneratedCode'
        
        print(f"{Colors.GREEN}⚡ Generating {parsed.get('language', 'Python')} code...")
        
        # Generate code
        result = self.code_gen.generate(parsed)
        
        # Add to history
        self.history.append({
            'type': 'code',
            'language': parsed.get('language'),
            'target': parsed.get('target'),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        return self.code_gen.format_output(result)
    
    def _handle_unknown(self, user_input: str) -> str:
        """Handle unknown commands."""
        suggestions = []
        
        if any(word in user_input.lower() for word in ['what', 'how', 'when', 'where', 'why']):
            suggestions.append(f"{Colors.WHITE}• For definitions, try: 'Define [word]'")
        
        if any(word in user_input.lower() for word in ['make', 'create', 'build', 'write']):
            suggestions.append(f"{Colors.WHITE}• For code, try: 'Create a Java class named Test'")
        
        if not suggestions:
            suggestions.append(f"{Colors.WHITE}• Try: 'Create a Python class' or 'Define resilience'")
            suggestions.append(f"{Colors.WHITE}• Type 'help' for all commands")
        
        response = f"{Colors.YELLOW}🤔 Not sure what you want.\n"
        response += f"{Colors.CYAN}💡 Suggestions:{Colors.RESET}\n"
        response += "\n".join(suggestions)
        
        return response
    
    def _show_history(self) -> str:
        """Show conversation history."""
        if not self.history:
            return f"{Colors.YELLOW}No history yet. Try some commands!"
        
        output = [f"{Colors.CYAN}📜 HISTORY (last 5):"]
        output.append(f"{Colors.CYAN}────────────────────────────────────────")
        
        for i, entry in enumerate(self.history[-5:], 1):
            if entry['type'] == 'dictionary':
                output.append(f"{Colors.BLUE}[{i}] 🔍 {entry['word']} ({entry['timestamp']})")
            elif entry['type'] == 'code':
                output.append(f"{Colors.GREEN}[{i}] 💻 {entry['language']} {entry['target']} ({entry['timestamp']})")
        
        output.append(f"{Colors.CYAN}────────────────────────────────────────")
        return "\n".join(output)
    
    def ask_feedback(self):
        """Ask for feedback."""
        feedback = input(f"\n{Colors.CYAN}💡 How can I improve? (Enter to skip): {Colors.RESET}").strip()
        if feedback and feedback.lower() not in ['skip', 'no', '']:
            print(f"{Colors.GREEN}✓ Thanks! Feedback noted.")
            return True
        return False
    
    def run(self):
        """Main run loop."""
        while self.running:
            try:
                # Get input
                user_input = input(f"\n{Colors.YELLOW}💬 You > {Colors.RESET}").strip()
                
                if not user_input:
                    continue
                
                # Process
                response = self.process_input(user_input)
                
                # Show response
                if response:
                    print(f"\n{Colors.CYAN}🤖 Assistant:{Colors.RESET}")
                    print(response)
                    
                    # Ask for feedback
                    if user_input.lower() not in ['help', 'history', 'clear']:
                        self.ask_feedback()
            
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}⚠️  Use 'quit' to exit.{Colors.RESET}")
                continue
            except Exception as e:
                print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")

# ========== MAIN ==========
def main():
    """Entry point."""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{Colors.GREEN}🚀 Starting Lightweight Assistant...")
    print(f"{Colors.YELLOW}📦 No dependencies required - pure Python!{Colors.RESET}")
    
    try:
        assistant = LightweightAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Assistant stopped.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}💥 Error: {e}{Colors.RESET}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())