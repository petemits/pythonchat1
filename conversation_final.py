"""
COMPLETE ENDLESS CONVERSATION GENERATOR
Fixed version with all corrections applied
Compatible with Python 3.8+
"""

import random
import re
import wikipedia
from collections import deque
import time
from textblob import TextBlob
from textblob import Word

print("Initializing Intelligent Dialogue Engine...")

try:
    test_blob = TextBlob("test")
    print("✓ TextBlob is ready.")
except Exception as e:
    print(f"Note: TextBlob may need to download data: {e}")
    print("Run: python -m textblob.download_corpora")

class IntelligentDialogueEngine:
    def __init__(self):
        self.conversation_history = deque(maxlen=10)
        self.current_topic = None
        
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 
            'will', 'would', 'shall', 'should', 'may', 'might', 'must', 
            'can', 'could', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its',
            'let', 'lets', "let's"
        }
        
        self.excluded_words = {
            "let's", "lets", "let", "dont", "cant", "wont", "im", "youre", 
            "its", "thats", "theres", "theyre", "weve", "ive", "youve"
        }

        self.w_patterns = {
            "who": ["Who is involved with {topic}?", "Who created or discovered {topic}?"],
            "what": ["What exactly is {topic}?", "What is the significance of {topic}?"],
            "where": ["Where is {topic} most relevant or located?", "Where did the concept of {topic} begin?"],
            "when": ["When did {topic} become important?", "When is {topic} typically observed?"],
            "why": ["Why is {topic} important to understand?", "Why does {topic} matter in this context?"]
        }

        self.transitions = [
            "Speaking of {old}, that reminds me of {new}...",
            "On a related note to {old}, I was thinking about {new}...",
            "That discussion about {old} connects to the idea of {new}...",
            "By the way, from {old} we can explore {new}...",
            "Which reminds me, {old} naturally leads us to consider {new}..."
        ]

        self.basic_synonyms = {
            "love": ["affection", "passion", "emotion", "relationship"],
            "time": ["duration", "period", "moment", "history"],
            "art": ["creativity", "expression", "painting", "music"],
            "science": ["knowledge", "research", "discovery", "technology"],
            "space": ["universe", "cosmos", "astronomy", "galaxy"],
            "exploration": ["discovery", "journey", "adventure", "research"],
            "technology": ["innovation", "computers", "digital", "engineering"],
            "knowledge": ["understanding", "wisdom", "learning", "education"],
            "climate": ["weather", "environment", "atmosphere", "earth"],
            "change": ["transformation", "evolution", "shift", "development"],
            "discussion": ["conversation", "dialogue", "debate", "talk"],
            "conversation": ["dialogue", "discussion", "chat", "talk"]
        }
        
        self.fallback_topics = [
            "artificial intelligence", "space exploration", "climate change", 
            "ancient philosophy", "modern technology", "renaissance art",
            "human psychology", "scientific discovery", "cultural evolution"
        ]

    def fetch_wikipedia_context(self, topic):
        """Fetch relevant information from Wikipedia."""
        try:
            clean_topic = topic
            for suffix in [" concept", " understanding", " discussion"]:
                if topic.endswith(suffix):
                    clean_topic = topic[:-len(suffix)].strip()
                    break
            
            summary = wikipedia.summary(clean_topic, sentences=2, auto_suggest=True, redirect=True)
            return summary, True
        except wikipedia.exceptions.DisambiguationError as e:
            if e.options:
                try:
                    summary = wikipedia.summary(e.options[0], sentences=2)
                    return f"Regarding {e.options[0]}: {summary}", True
                except:
                    pass
            return f"Multiple topics found for '{clean_topic}'.", False
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{clean_topic}'.", False
        except Exception as e:
            return f"Could not fetch details: {str(e)[:50]}...", False

    def get_semantic_links(self, word):
        """Get synonyms using TextBlob or fallback."""
        clean_word = word.lower().strip()
        
        if clean_word in ["lets", "let", "concept", "understanding", "discussion"]:
            return random.sample(self.fallback_topics, 2)
        
        synonyms = []
        
        try:
            word_obj = Word(clean_word)
            for synset in word_obj.synsets[:3]:
                for lemma in synset.lemmas()[:3]:
                    syn = lemma.name()
                    if syn != clean_word and syn not in synonyms:
                        synonyms.append(syn.replace('_', ' '))
        except:
            pass
        
        if clean_word in self.basic_synonyms:
            synonyms.extend(self.basic_synonyms[clean_word])
        
        if not synonyms:
            synonyms = random.sample(self.fallback_topics, 2)
        
        clean_synonyms = []
        for syn in synonyms:
            clean_syn = syn.lower().strip()
            if (clean_syn != clean_word and 
                clean_syn not in clean_synonyms and 
                len(clean_syn) > 2):
                clean_synonyms.append(clean_syn)
        
        return clean_synonyms[:3]

    def parse_and_extract_keywords(self, text):
        """Extract main keywords from text with improved filtering."""
        try:
            lower_text = text.lower().strip()
            
            auto_patterns = [
                r"let's discuss (.+)",
                r"what about (.+)\?",
                r"consider (.+)",
                r"thoughts on (.+)\?",
                r"exploring (.+) further",
                r"(.+) is interesting"
            ]
            
            for pattern in auto_patterns:
                match = re.match(pattern, lower_text)
                if match:
                    topic = match.group(1).strip()
                    if topic.endswith("."):
                        topic = topic[:-1]
                    return [topic] if topic else ["discussion"]
            
            blob = TextBlob(lower_text)
            keywords = []
            
            for word, tag in blob.tags:
                clean_word = word.lower().strip()
                
                if (clean_word not in self.stop_words and 
                    clean_word not in self.excluded_words and
                    len(clean_word) > 3 and
                    tag in ['NN', 'NNS', 'NNP', 'JJ'] and
                    not clean_word.endswith("'s") and
                    not clean_word.endswith("'t")):
                    
                    if (clean_word.isalpha() and 
                        not clean_word.isnumeric()):
                        keywords.append(clean_word)
            
            if keywords:
                scored_keywords = []
                for kw in keywords:
                    score = len(kw)
                    scored_keywords.append((score, kw))
                
                scored_keywords.sort(reverse=True)
                return [kw for _, kw in scored_keywords[:2]]
            
            words = lower_text.split()
            meaningful_words = []
            for w in words:
                clean_w = w.strip('.,!?;:"\'()[]{}')
                if (len(clean_w) > 4 and
                    clean_w not in self.stop_words and
                    clean_w not in self.excluded_words and
                    clean_w.isalpha()):
                    meaningful_words.append(clean_w)
            
            return meaningful_words[:2] if meaningful_words else ["knowledge"]
            
        except Exception as e:
            return ["conversation"]

    def generate_response_with_5ws(self, topic, context):
        """Generate a conversational question/response."""
        display_topic = topic.replace('_', ' ').title()
        
        w_type = random.choice(list(self.w_patterns.keys()))
        question_template = random.choice(self.w_patterns[w_type])
        question = question_template.format(topic=display_topic)
        
        response = f"{question} "
        
        if context and "Wikipedia page found" not in context and "Multiple topics" not in context:
            sentences = re.split(r'[.!?]+', context)
            if sentences and len(sentences[0].split()) > 3:
                fact = sentences[0].strip()
                response += f"I understand that {fact.lower()} "
            else:
                response += "This is quite fascinating. "
        else:
            response += "This seems like an intriguing subject. "
        
        follow_ups = [
            "What are your thoughts on this?",
            "How does this resonate with you?",
            "I find this perspective quite engaging.",
            "There's much to explore here, isn't there?"
        ]
        response += random.choice(follow_ups)
        
        return response

    def transition_to_new_topic(self, old_topic):
        """Create a smooth transition to a related new topic."""
        clean_old = old_topic.lower().strip()
        for suffix in [" concept", " understanding", " discussion"]:
            if clean_old.endswith(suffix):
                clean_old = clean_old[:-len(suffix)].strip()
                break
        
        related = self.get_semantic_links(clean_old)
        
        if related:
            new_topic = random.choice(related)
        else:
            new_topic = random.choice(self.fallback_topics)
        
        if (new_topic.lower() == clean_old or 
            new_topic.lower().startswith(clean_old) or
            clean_old.startswith(new_topic.lower())):
            new_topic = random.choice([t for t in self.fallback_topics if t != clean_old])
        
        transition = random.choice(self.transitions)
        return transition.format(old=clean_old.title(), new=new_topic.title()), new_topic

    def simulate_dialogue_exchange(self, user_input):
        """Simulate a conversation between two speakers."""
        keywords = self.parse_and_extract_keywords(user_input)
        
        if not keywords:
            main_topic = "knowledge"
        else:
            main_topic = keywords[0]
            if main_topic in self.excluded_words or main_topic in self.stop_words:
                main_topic = "understanding" if len(keywords) < 2 else keywords[1]
        
        if len(main_topic) < 3 or main_topic in self.excluded_words:
            main_topic = random.choice(self.fallback_topics)
        
        context, valid_context = self.fetch_wikipedia_context(main_topic)
        
        speaker_a_response = self.generate_response_with_5ws(main_topic, context)
        
        display_topic = main_topic.replace('_', ' ').title()
        speaker_b_response = f"I appreciate your insight about {display_topic}. "
        
        if valid_context and "Wikipedia page found" not in context and "Multiple topics" not in context:
            sentences = re.split(r'[.!?]+', context)
            if len(sentences) > 1 and len(sentences[1].split()) > 2:
                fact = sentences[1].strip()
                speaker_b_response += f"It's also noteworthy that {fact.lower()} "
            else:
                speaker_b_response += "This brings up several interesting implications. "
        else:
            speaker_b_response += "This raises some profound questions. "
        
        reflections = [
            "How might this influence our broader understanding?",
            "What future developments could emerge from this?",
            "How does this connect to other areas of thought?",
            "What are the deeper implications here?"
        ]
        speaker_b_response += random.choice(reflections)
        
        self.conversation_history.append({
            'topic': main_topic,
            'speaker_a': speaker_a_response,
            'speaker_b': speaker_b_response
        })
        
        transition_text, next_topic = self.transition_to_new_topic(main_topic)
        self.current_topic = next_topic
        
        dialogue = f"""
        {'='*60}
        Topic: {display_topic.upper()}
        {'-'*60}
        
        Speaker A: {speaker_a_response}
        
        Speaker B: {speaker_b_response}
        
        {transition_text}
        
        Next potential topic: {next_topic.title()}
        {'='*60}
        """
        
        return dialogue, next_topic

    def run_endless_conversation(self, initial_prompt=None):
        """Main loop for endless conversation."""
        print("\n" + "="*60)
        print("ENDLESS CONVERSATION GENERATOR")
        print("="*60)
        print("This system simulates dialogue between two speakers.")
        print("It uses Wikipedia for facts and semantic links for transitions.")
        print("="*60)
        print("Commands: 'quit' to exit, 'history' for recent topics, 'auto' for auto-run.")
        print("="*60)
        
        if initial_prompt:
            current_topic = initial_prompt
        else:
            current_topic = random.choice(self.fallback_topics)
            print(f"\nStarting with topic: {current_topic}\n")
        
        auto_prompts = [
            "What are the key aspects of {topic}?",
            "How would you describe {topic}?",
            "What comes to mind when you think of {topic}?",
            "Let's explore {topic} further.",
            "Consider the implications of {topic}."
        ]
        
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
                    short_topic = entry['topic'][:20] + "..." if len(entry['topic']) > 20 else entry['topic']
                    print(f"{i}. {short_topic} - A: {entry['speaker_a'][:40]}...")
                continue
            elif user_input.lower() == 'auto':
                steps = input("How many auto-exchanges? (1-10, default 3): ").strip()
                try:
                    steps = min(max(int(steps), 1), 10)
                except:
                    steps = 3
                
                for i in range(steps):
                    print(f"\n[Auto-exchange {i+1}/{steps}]")
                    prompt_template = random.choice(auto_prompts)
                    auto_input = prompt_template.format(topic=current_topic)
                    dialogue, current_topic = self.simulate_dialogue_exchange(auto_input)
                    print(dialogue)
                    time.sleep(0.5)
                continue
            elif not user_input:
                prompt_template = random.choice(auto_prompts)
                user_input = prompt_template.format(topic=current_topic)
            
            dialogue, current_topic = self.simulate_dialogue_exchange(user_input)
            print(dialogue)

# ============================================
# Main execution
# ============================================

if __name__ == "__main__":
    try:
        test_blob = TextBlob("Testing the system")
        print("✓ TextBlob initialized successfully.")
    except Exception as e:
        print(f"✗ TextBlob error: {e}")
        print("Please install: pip install textblob")
        print("Then run: python -m textblob.download_corpora")
        exit(1)
    
    try:
        test_summary = wikipedia.summary("Python", sentences=1)
        print("✓ Wikipedia library is working.")
    except Exception as e:
        print(f"✗ Wikipedia test failed: {e}")
        print("Please install: pip install wikipedia")
        exit(1)
    
    engine = IntelligentDialogueEngine()
    initial = input("\nEnter a starting topic (or press Enter for random): ").strip()
    print("\nStarting conversation engine...")
    time.sleep(1)
    engine.run_endless_conversation(initial if initial else None)