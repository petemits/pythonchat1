"""
COMPLETE ENDLESS CONVERSATION GENERATOR - FIXED VERSION
Properly connects to Wikipedia with robust keyword extraction
"""

import random
import re
import wikipedia
from collections import deque
import time
import sys

print("Initializing Intelligent Dialogue Engine...")

# Test Wikipedia first
try:
    test_summary = wikipedia.summary("Python", sentences=1)
    print("✓ Wikipedia library is working.")
except Exception as e:
    print(f"✗ Wikipedia error: {e}")
    print("Please install: pip install wikipedia")
    sys.exit(1)

class IntelligentDialogueEngine:
    def __init__(self):
        self.conversation_history = deque(maxlen=10)
        self.current_topic = None
        self.used_topics = set()  # Track used topics to avoid repetition
        
        # Enhanced stop words
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 
            'will', 'would', 'shall', 'should', 'may', 'might', 'must', 
            'can', 'could', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its',
            'let', 'lets', "let's", "that's", "what's", "there's", "here's",
            'about', 'very', 'just', 'more', 'some', 'any', 'all', 'also'
        }
        
        # Common topics for fallback (actual Wikipedia-friendly topics)
        self.common_topics = [
            "artificial intelligence", "climate change", "space exploration",
            "quantum computing", "renewable energy", "ancient history",
            "modern art", "world literature", "marine biology",
            "astrophysics", "neuroscience", "sustainable agriculture",
            "digital currency", "virtual reality", "genetic engineering",
            "robotics", "nanotechnology", "renewable energy", "cybersecurity",
            "urban planning", "economic development", "public health"
        ]

        self.w_patterns = {
            "who": ["Who is involved with {topic}?", "Who studies {topic}?"],
            "what": ["What is {topic}?", "What does {topic} involve?"],
            "where": ["Where is {topic} relevant?", "Where does {topic} occur?"],
            "when": ["When did {topic} become important?", "When do we see {topic}?"],
            "why": ["Why is {topic} significant?", "Why does {topic} matter?"]
        }

        self.transitions = [
            "Speaking of {old}, that makes me think about {new}...",
            "This connects to the broader topic of {new}...",
            "Related to this is the subject of {new}...",
            "This brings up questions about {new}...",
            "We could also consider {new} in this context..."
        ]

    def clean_topic_for_wikipedia(self, topic):
        """Clean and prepare a topic for Wikipedia search."""
        # Remove problematic phrases
        topic = re.sub(r'\b(lets|let\'s|discuss|talk about|think about)\b', '', topic, flags=re.IGNORECASE)
        
        # Remove trailing punctuation and common suffixes
        topic = re.sub(r'[\?\.\!,;:]$', '', topic)
        topic = re.sub(r'\s+(concept|idea|topic|subject|discussion|understanding)$', '', topic, flags=re.IGNORECASE)
        
        # Get the most meaningful part (usually last few words)
        words = topic.split()
        if len(words) > 3:
            # Take the most recent words which are usually the main topic
            topic = ' '.join(words[-3:])
        
        # Capitalize properly for Wikipedia
        if topic:
            topic = ' '.join(word.capitalize() if len(word) > 2 else word for word in topic.split())
        
        return topic.strip()

    def get_wikipedia_content(self, topic):
        """Get meaningful content from Wikipedia with multiple fallbacks."""
        original_topic = topic
        
        # Clean the topic first
        clean_topic = self.clean_topic_for_wikipedia(topic)
        
        if not clean_topic or len(clean_topic) < 3:
            # Topic is too short, use a random common topic
            clean_topic = random.choice([t for t in self.common_topics if t not in self.used_topics])
        
        # Try multiple approaches to get Wikipedia content
        attempts = [
            clean_topic,  # Try the cleaned topic
            clean_topic.split()[-1] if ' ' in clean_topic else clean_topic,  # Try last word
            original_topic.split()[-1] if ' ' in original_topic else original_topic  # Try original last word
        ]
        
        for attempt in attempts:
            if not attempt or len(attempt) < 3:
                continue
                
            try:
                print(f"  [Debug] Searching Wikipedia for: '{attempt}'")
                page = wikipedia.page(attempt, auto_suggest=True)
                
                if page and hasattr(page, 'content') and page.content:
                    # Get first paragraph or summary
                    content = page.content.split('\n')[0]
                    if len(content) > 100:
                        sentences = content.split('. ')
                        summary = '. '.join(sentences[:2]) + '.'
                        return summary, True, attempt
            except wikipedia.exceptions.DisambiguationError as e:
                # Try first suggestion
                if e.options:
                    try:
                        print(f"  [Debug] Disambiguation, trying: '{e.options[0]}'")
                        page = wikipedia.page(e.options[0], auto_suggest=False)
                        if page.content:
                            content = page.content.split('\n')[0]
                            if len(content) > 50:
                                sentences = content.split('. ')
                                summary = '. '.join(sentences[:2]) + '.'
                                return summary, True, e.options[0]
                    except:
                        continue
            except wikipedia.exceptions.PageError:
                continue
            except Exception as e:
                print(f"  [Debug] Wikipedia error: {e}")
                continue
        
        # If all attempts fail, use a fallback topic
        fallback = random.choice([t for t in self.common_topics if t not in self.used_topics])
        try:
            page = wikipedia.page(fallback, auto_suggest=True)
            content = page.content.split('\n')[0]
            sentences = content.split('. ')
            summary = '. '.join(sentences[:2]) + '.'
            return summary, True, fallback
        except:
            return f"Exploring the concept of {fallback}.", False, fallback

    def extract_meaningful_keywords(self, text):
        """Extract the most meaningful keywords from text."""
        if not text or not isinstance(text, str):
            return ["knowledge"]
        
        text = text.lower().strip()
        
        # Check for auto-generated patterns first
        auto_patterns = [
            r"what are the key aspects of (.+?)(?:\?|$)",
            r"how would you describe (.+?)(?:\?|$)",
            r"what comes to mind when you think of (.+?)(?:\?|$)",
            r"let's explore (.+?) further",
            r"consider the implications of (.+?)(?:\?|$)",
            r"thoughts on (.+?)(?:\?|$)",
            r"what about (.+?)(?:\?|$)"
        ]
        
        for pattern in auto_patterns:
            match = re.search(pattern, text)
            if match:
                extracted = match.group(1).strip()
                if extracted and len(extracted) > 3:
                    return [extracted]
        
        # Split into words and filter
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Remove stop words
        filtered = [w for w in words if w not in self.stop_words]
        
        # Prioritize longer words (usually more meaningful)
        if filtered:
            filtered.sort(key=len, reverse=True)
            return filtered[:2]
        
        # Last resort: use the longest word in the text
        all_words = text.split()
        if all_words:
            meaningful = [w for w in all_words if len(w) > 4]
            if meaningful:
                meaningful.sort(key=len, reverse=True)
                return [meaningful[0]]
        
        return ["discussion"]

    def get_next_topic(self, current_topic):
        """Get a related but different topic."""
        # Mark current topic as used
        if current_topic:
            self.used_topics.add(current_topic.lower())
        
        # Get a new topic that hasn't been used recently
        available_topics = [t for t in self.common_topics if t.lower() not in self.used_topics]
        
        if available_topics:
            # Prefer topics that share words with current topic
            if current_topic:
                current_words = set(current_topic.lower().split())
                scored_topics = []
                for topic in available_topics:
                    topic_words = set(topic.lower().split())
                    common_words = current_words.intersection(topic_words)
                    score = len(common_words)
                    scored_topics.append((score, topic))
                
                scored_topics.sort(reverse=True)
                # Pick from top 3 related topics
                top_topics = [t for _, t in scored_topics[:3]]
                return random.choice(top_topics)
            else:
                return random.choice(available_topics)
        else:
            # Reset used topics if we've used them all
            self.used_topics.clear()
            return random.choice(self.common_topics)

    def generate_conversation(self, topic, wiki_content):
        """Generate a natural conversation about the topic."""
        # Clean the topic for display
        display_topic = topic.title()
        
        # Speaker A asks a question
        w_type = random.choice(list(self.w_patterns.keys()))
        question_template = random.choice(self.w_patterns[w_type])
        question = question_template.format(topic=display_topic)
        
        # Speaker A adds context from Wikipedia
        if wiki_content and "Exploring the concept" not in wiki_content:
            # Extract an interesting fact
            sentences = wiki_content.split('. ')
            if sentences:
                fact = sentences[0]
                speaker_a = f"{question} {fact}"
            else:
                speaker_a = f"{question} This is an interesting area of study."
        else:
            speaker_a = f"{question} This seems like a fascinating subject."
        
        # Speaker B responds
        reflections = [
            "That's an interesting perspective.",
            "I see what you mean.",
            "That raises some important questions.",
            "That's a good point to consider."
        ]
        
        if wiki_content and len(wiki_content.split('. ')) > 1:
            # Add another fact
            sentences = wiki_content.split('. ')
            if len(sentences) > 1:
                second_fact = sentences[1]
                speaker_b = f"{random.choice(reflections)} {second_fact}"
            else:
                speaker_b = f"{random.choice(reflections)} There's certainly more to explore here."
        else:
            speaker_b = f"{random.choice(reflections)} What other aspects should we consider?"
        
        return speaker_a, speaker_b, display_topic

    def simulate_dialogue_exchange(self, user_input):
        """Simulate a conversation exchange."""
        # Extract topic from input
        keywords = self.extract_meaningful_keywords(user_input)
        main_keyword = keywords[0] if keywords else "knowledge"
        
        # Get Wikipedia content
        wiki_content, success, actual_topic = self.get_wikipedia_content(main_keyword)
        
        # Generate conversation
        speaker_a, speaker_b, display_topic = self.generate_conversation(actual_topic, wiki_content)
        
        # Get next topic
        next_topic = self.get_next_topic(actual_topic)
        self.current_topic = next_topic
        
        # Add transition
        transition = random.choice(self.transitions)
        transition_text = transition.format(old=display_topic, new=next_topic.title())
        
        # Store in history
        self.conversation_history.append({
            'topic': display_topic,
            'speaker_a': speaker_a,
            'speaker_b': speaker_b,
            'wiki_success': success
        })
        
        # Format output
        dialogue = f"""
        {'='*60}
        Topic: {display_topic.upper()}
        {'-'*60}
        
        Speaker A: {speaker_a}
        
        Speaker B: {speaker_b}
        
        {transition_text}
        
        Next topic: {next_topic.title()}
        {'='*60}
        """
        
        return dialogue, next_topic

    def run_endless_conversation(self):
        """Main conversation loop."""
        print("\n" + "="*60)
        print("ENDLESS CONVERSATION GENERATOR")
        print("="*60)
        print("This bot uses Wikipedia for real information.")
        print("Commands: 'quit', 'history', 'auto X' (X = number of exchanges)")
        print("="*60)
        
        # Start with a random topic
        current_topic = random.choice(self.common_topics)
        print(f"\nStarting with: {current_topic.title()}\n")
        
        while True:
            user_input = input(f"\n[Current: {current_topic.title()}] Your input (Enter for auto): ").strip()
            
            if user_input.lower() == 'quit':
                print(f"\nConversation ended. Topics discussed: {len(self.conversation_history)}")
                break
                
            elif user_input.lower() == 'history':
                print("\nRecent History:")
                for i, entry in enumerate(list(self.conversation_history)[-5:], 1):
                    status = "✓" if entry['wiki_success'] else "✗"
                    print(f"{i}. {status} {entry['topic']} - {entry['speaker_a'][:50]}...")
                continue
                
            elif user_input.lower().startswith('auto'):
                parts = user_input.split()
                steps = 3 if len(parts) < 2 else min(int(parts[1]), 10)
                
                for i in range(steps):
                    print(f"\n[Auto-exchange {i+1}/{steps}]")
                    auto_input = f"What about {current_topic}?"
                    dialogue, current_topic = self.simulate_dialogue_exchange(auto_input)
                    print(dialogue)
                    time.sleep(1)
                continue
                
            elif not user_input:
                # Auto-generate
                prompts = [
                    f"What about {current_topic}?",
                    f"Tell me about {current_topic}.",
                    f"Discuss {current_topic}.",
                    f"Thoughts on {current_topic}?"
                ]
                user_input = random.choice(prompts)
            
            # Process input
            dialogue, current_topic = self.simulate_dialogue_exchange(user_input)
            print(dialogue)

# ============================================
# Main execution
# ============================================

if __name__ == "__main__":
    # Set Wikipedia settings
    wikipedia.set_lang("en")
    
    # Create and run engine
    engine = IntelligentDialogueEngine()
    
    print("\n" + "="*60)
    print("READY TO START CONVERSATION")
    print("="*60)
    print("The bot will now fetch real information from Wikipedia.")
    print("This may take a moment for the first few searches...")
    print("="*60)
    
    time.sleep(2)
    
    # Start conversation
    try:
        engine.run_endless_conversation()
    except KeyboardInterrupt:
        print("\n\nConversation interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Restarting might help.")