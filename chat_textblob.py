"""
Endless Conversation & Fable Generator
Updated to use TextBlob instead of NLTK for part-of-speech tagging.
Compatible with Python 3.8+.
"""

import random
import re
import wikipedia
from collections import deque
import time
from textblob import TextBlob
from textblob import Word

# ============================================
# TEXTBLOB INITIALIZATION
# ============================================
# TextBlob requires a corpus download on first use
# This will automatically download required data
try:
    # Test TextBlob to trigger any automatic downloads
    test_blob = TextBlob("test")
    print("✓ TextBlob is ready.")
except Exception as e:
    print(f"Note: TextBlob may need to download data on first use: {e}")

class IntelligentDialogueEngine:
    def __init__(self):
        # Initialize conversation memory
        self.conversation_history = deque(maxlen=10)
        self.current_topic = None
        self.speaker_toggle = "A"

        # Common stop words (simplified list)
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 
            'will', 'would', 'shall', 'should', 'may', 'might', 'must', 
            'can', 'could', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its'
        }

        # 5 Ws patterns for conversation
        self.w_patterns = {
            "who": ["Who is involved with {topic}?", "Who created or discovered {topic}?"],
            "what": ["What exactly is {topic}?", "What is the significance of {topic}?"],
            "where": ["Where is {topic} most relevant or located?", "Where did the concept of {topic} begin?"],
            "when": ["When did {topic} become important?", "When is {topic} typically observed?"],
            "why": ["Why is {topic} important to understand?", "Why does {topic} matter in this context?"]
        }

        # Transition phrases for smooth topic flow
        self.transitions = [
            "Speaking of {old}, that reminds me of {new}...",
            "On a related note to {old}, I was thinking about {new}...",
            "That discussion about {old} connects to the idea of {new}...",
            "By the way, from {old} we can explore {new}...",
            "Which reminds me, {old} naturally leads us to consider {new}..."
        ]

        # Basic synonyms database (fallback when WordNet isn't available)
        self.basic_synonyms = {
            "love": ["affection", "passion", "devotion", "fondness", "adoration"],
            "time": ["duration", "period", "era", "moment", "interval"],
            "art": ["creativity", "expression", "craft", "work", "design"],
            "science": ["knowledge", "study", "research", "discipline", "field"],
            "space": ["universe", "cosmos", "void", "expanse", "galaxy"],
            "exploration": ["discovery", "investigation", "search", "journey", "adventure"],
            "technology": ["innovation", "engineering", "machinery", "tools", "devices"],
            "knowledge": ["understanding", "wisdom", "information", "learning", "education"]
        }

    def fetch_wikipedia_context(self, topic):
        """Fetch relevant information from Wikipedia for a given topic."""
        try:
            # Get a short summary (2-3 sentences)
            summary = wikipedia.summary(topic, sentences=2, auto_suggest=True, redirect=True)
            return summary, True
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle ambiguous topics
            return f"Multiple topics found for '{topic}'. Perhaps you meant: {', '.join(e.options[:3])}.", False
        except wikipedia.exceptions.PageError:
            return f"No specific Wikipedia page found for '{topic}'.", False
        except Exception as e:
            return f"Could not fetch details on '{topic}' due to: {str(e)[:50]}...", False

    def get_semantic_links(self, word):
        """Get synonyms using TextBlob's Word.synsets or fallback to basic dictionary."""
        synonyms = []
        
        # Try TextBlob first
        try:
            word_obj = Word(word)
            for synset in word_obj.synsets[:3]:  # Limit to first 3 synsets
                for lemma in synset.lemmas()[:3]:  # Limit to first 3 lemmas per synset
                    syn = lemma.name()
                    if syn != word and syn not in synonyms:
                        synonyms.append(syn.replace('_', ' '))
        except:
            # Fallback to basic synonyms dictionary
            if word in self.basic_synonyms:
                synonyms = self.basic_synonyms[word]
        
        # If still no synonyms, use related concepts
        if not synonyms:
            related_concepts = ["understanding", "concept", "idea", "notion", "subject"]
            synonyms = [f"{word} {concept}" for concept in related_concepts[:2]]
        
        return synonyms[:5]

    def parse_and_extract_keywords(self, text):
        """Extract main keywords from text using TextBlob."""
        try:
            blob = TextBlob(text.lower())
            keywords = []
            
            # Extract nouns and adjectives
            # TextBlob tags: NN (noun), NNS (plural noun), NNP (proper noun), 
            # JJ (adjective), JJR (comparative adj), JJS (superlative adj)
            for word, tag in blob.tags:
                # Filter out stop words and short words
                if (word not in self.stop_words and len(word) > 2 and 
                    tag in ['NN', 'NNS', 'NNP', 'JJ', 'JJR', 'JJS']):
                    keywords.append(word)
            
            return keywords[:3] if keywords else ["discussion"]
        except Exception as e:
            # Fallback: simple word extraction
            words = text.lower().split()
            filtered = [w for w in words if w not in self.stop_words and len(w) > 3]
            return filtered[:3] if filtered else ["conversation"]

    def generate_response_with_5ws(self, topic, context):
        """Generate a conversational question/response using the 5 Ws."""
        w_type = random.choice(list(self.w_patterns.keys()))
        question_template = random.choice(self.w_patterns[w_type])
        question = question_template.format(topic=topic)
        
        response = f"{question} "
        
        if context and "found for" not in context and "could not fetch" not in context:
            # Use the Wikipedia context
            sentences = context.split('. ')
            fact = sentences[0] if sentences else context
            response += f"I know that {fact.lower()} "
        else:
            response += "It's a fascinating subject. "
        
        # Add a conversational follow-up
        follow_ups = [
            "What's your take on this?",
            "Does that align with your understanding?",
            "I'd be curious to explore this further."
        ]
        response += random.choice(follow_ups)
        
        return response

    def transition_to_new_topic(self, old_topic):
        """Create a smooth transition to a semantically related new topic."""
        related = self.get_semantic_links(old_topic)
        
        if related:
            new_topic = random.choice(related)
        else:
            # Fallback topics
            fallback_topics = ["innovation", "culture", "nature", "progress", 
                              "discovery", "history", "science", "art", "philosophy"]
            new_topic = random.choice(fallback_topics)
        
        transition = random.choice(self.transitions)
        return transition.format(old=old_topic, new=new_topic), new_topic

    def simulate_dialogue_exchange(self, user_input):
        """Simulate a conversation between two speakers (A and B)."""
        # Extract main topic from input
        keywords = self.parse_and_extract_keywords(user_input)
        main_topic = keywords[0] if keywords else "dialogue"
        
        # Get Wikipedia context
        context, valid_context = self.fetch_wikipedia_context(main_topic)
        
        # Speaker A's turn
        speaker_a_response = self.generate_response_with_5ws(main_topic, context)
        
        # Speaker B's turn
        speaker_b_response = f"That's an interesting point about {main_topic}. "
        
        if valid_context and "found for" not in context:
            # Add a different fact or perspective
            sentences = context.split('. ')
            if len(sentences) > 1:
                fact = sentences[1] if len(sentences) > 1 else sentences[0]
                speaker_b_response += f"From what I've read, {fact.lower()} "
            else:
                speaker_b_response += "There's certainly more to explore here. "
        else:
            speaker_b_response += "It makes me think about related concepts. "
        
        # Add a reflective question
        reflections = [
            "How do you think this concept has evolved?",
            "This seems to connect to broader themes in interesting ways.",
            "What future developments might come from this?"
        ]
        speaker_b_response += random.choice(reflections)
        
        # Store conversation
        self.conversation_history.append({
            'topic': main_topic,
            'speaker_a': speaker_a_response,
            'speaker_b': speaker_b_response,
            'context': context if valid_context else "No context"
        })
        
        # Transition to next topic
        transition_text, next_topic = self.transition_to_new_topic(main_topic)
        self.current_topic = next_topic
        
        # Format dialogue output
        dialogue = f"""
        {'='*60}
        Topic: {main_topic.upper()}
        {'-'*60}
        
        Speaker A: {speaker_a_response}
        
        Speaker B: {speaker_b_response}
        
        {transition_text}
        
        Next potential topic: {next_topic.upper()}
        {'='*60}
        """
        
        return dialogue, next_topic

    def run_endless_conversation(self, initial_prompt=None):
        """Main loop for endless conversation."""
        print("\n" + "="*60)
        print("ENDLESS CONVERSATION GENERATOR (TextBlob Edition)")
        print("="*60)
        print("This system simulates dialogue between two speakers.")
        print("It uses Wikipedia for facts and semantic links for transitions.")
        print("="*60)
        print("Commands: 'quit' to exit, 'history' for recent topics, 'auto' for auto-run.")
        print("="*60)
        
        if initial_prompt:
            current_topic = initial_prompt
        else:
            current_topic = random.choice([
                "artificial intelligence", "space exploration", "renaissance art", 
                "climate change", "ancient philosophy", "modern technology"
            ])
            print(f"\nStarting with topic: {current_topic}\n")
        
        while True:
            user_input = input(f"\n[Current: {current_topic}] Your input (Enter for auto): ").strip()
            
            if user_input.lower() == 'quit':
                print("\nEnding conversation. Final topic was:", current_topic)
                if self.conversation_history:
                    print(f"Total exchanges: {len(self.conversation_history)}")
                break
            elif user_input.lower() == 'history':
                print("\nRecent Conversation History:")
                for i, entry in enumerate(list(self.conversation_history)[-5:], 1):
                    print(f"{i}. {entry['topic']} - A: {entry['speaker_a'][:50]}...")
                continue
            elif user_input.lower() == 'auto':
                steps = input("How many auto-exchanges? (1-10, default 3): ").strip()
                try:
                    steps = min(max(int(steps), 1), 10)
                except ValueError:
                    steps = 3
                
                for i in range(steps):
                    print(f"\n[Auto-exchange {i+1}/{steps}]")
                    dialogue, current_topic = self.simulate_dialogue_exchange(current_topic)
                    print(dialogue)
                    time.sleep(1)
                continue
            elif not user_input:
                # Auto-generate based on current topic
                user_input = f"Let's discuss {current_topic}"
            
            # Generate and display dialogue
            dialogue, current_topic = self.simulate_dialogue_exchange(user_input)
            print(dialogue)

# ============================================
# Main execution block
# ============================================

if __name__ == "__main__":
    print("Initializing Intelligent Dialogue Engine (TextBlob Edition)...")
    
    # Test TextBlob
    try:
        test_blob = TextBlob("Testing TextBlob installation")
        print("✓ TextBlob initialized successfully.")
    except Exception as e:
        print(f"✗ TextBlob error: {e}")
        print("Please install with: pip install textblob")
        print("Also download corpora: python -m textblob.download_corpora")
        exit(1)
    
    # Test Wikipedia
    try:
        test_summary = wikipedia.summary("Python", sentences=1)
        print("✓ Wikipedia library is working.")
    except Exception as e:
        print(f"✗ Wikipedia test failed: {e}")
        print("Please install with: pip install wikipedia")
        exit(1)
    
    # Create and run the engine
    engine = IntelligentDialogueEngine()
    
    # Ask for initial topic
    initial = input("\nEnter a starting topic (or press Enter for random): ").strip()
    
    print("\nStarting conversation engine...\n")
    time.sleep(1)
    
    # Start the endless conversation
    engine.run_endless_conversation(initial if initial else None)