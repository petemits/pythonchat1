import random
import re
import wikipedia
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import wordnet, stopwords
from nltk import pos_tag
from collections import deque

# Download necessary NLTK data (run once)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

class IntelligentDialogueEngine:
    def __init__(self):
        # Initialize Wikipedia API with a proper user agent[citation:5]
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='IntelligentDialogueBot/1.0 (your_email@example.com)',
            language='en'
        )
        
        # Conversation memory to track topics and history[citation:6]
        self.conversation_history = deque(maxlen=10)
        self.current_topic = None
        self.speaker_toggle = "A"  # Tracks current speaker
        
        # NLP building blocks setup[citation:1]
        self.stop_words = set(stopwords.words('english'))
        
        # 5 Ws patterns for generating conversational questions/responses
        self.w_patterns = {
            "who": ["Who is involved with {topic}?", "Who created {topic}?"],
            "what": ["What exactly is {topic}?", "What are the main aspects of {topic}?"],
            "where": ["Where did {topic} originate?", "Where is {topic} most relevant?"],
            "when": ["When did {topic} become significant?", "When was {topic} first recognized?"],
            "why": ["Why is {topic} important?", "Why does {topic} matter?"]
        }
        
        # Transition phrases for topic shifting
        self.transitions = [
            "Speaking of {old}, that reminds me of {new}...",
            "On a related note to {old}, I was thinking about {new}...",
            "That discussion about {old} connects to {new} in an interesting way...",
            "By the way, considering {old} leads me to {new}...",
            "Which reminds me, from {old} we can explore {new}..."
        ]

    def fetch_wikipedia_context(self, topic):
        """Fetch relevant information from Wikipedia for a given topic[citation:2][citation:5][citation:9]"""
        try:
            page = self.wiki.page(topic)
            if page.exists():
                # Get the summary/short introduction of the page[citation:5]
                summary = page.summary
                # Extract first 3 sentences for concise context
                sentences = sent_tokenize(summary)[:3]
                return " ".join(sentences), True
            return f"Information about {topic}", False
        except Exception as e:
            return f"Could not fetch details on {topic}.", False

    def get_semantic_links(self, word):
        """Use WordNet to find semantically related words and synonyms[citation:3]"""
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name() != word:
                    synonyms.append(lemma.name().replace('_', ' '))
        return list(set(synonyms))[:5]  # Return top 5 unique synonyms

    def parse_and_extract_keywords(self, text):
        """Parse input text and extract meaningful keywords using NLP[citation:1]"""
        # Tokenize and remove stop words
        words = word_tokenize(text.lower())
        filtered_words = [w for w in words if w not in self.stop_words and w.isalpha()]
        
        # Use part-of-speech tagging to focus on nouns and adjectives[citation:8]
        tagged = pos_tag(filtered_words)
        keywords = [word for word, pos in tagged if pos.startswith('NN') or pos.startswith('JJ')]
        
        return keywords[:3] if keywords else [random.choice(["technology", "history", "science", "art"])]

    def generate_response_with_5ws(self, topic, context):
        """Generate a conversational response using the 5 Ws framework"""
        # Select a random W to focus on
        w_type = random.choice(list(self.w_patterns.keys()))
        question_template = random.choice(self.w_patterns[w_type])
        question = question_template.format(topic=topic)
        
        # Create a knowledge-based response using Wikipedia context
        response = f"{question} "
        
        # Add context from Wikipedia
        if "Information about" not in context:
            response += f"From what I understand, {context.lower()} "
        else:
            response += "That's an interesting topic. "
        
        # Add a conversational follow-up
        follow_ups = [
            "What's your perspective on this?",
            "Does that align with what you know?",
            "I find that connection quite fascinating."
        ]
        response += random.choice(follow_ups)
        
        return response

    def transition_to_new_topic(self, old_topic):
        """Generate a smooth transition to a new topic using semantic links"""
        # Get related words from WordNet
        related = self.get_semantic_links(old_topic)
        if related:
            new_topic = random.choice(related)
            transition = random.choice(self.transitions)
            return transition.format(old=old_topic, new=new_topic), new_topic
        # Fallback to random topic from a predefined list
        fallback_topics = ["innovation", "culture", "nature", "progress", "discovery"]
        new_topic = random.choice(fallback_topics)
        transition = random.choice(self.transitions)
        return transition.format(old=old_topic, new=new_topic), new_topic

    def simulate_dialogue_exchange(self, user_input):
        """Simulate a conversation between two speakers about a topic"""
        # Extract keywords from input
        keywords = self.parse_and_extract_keywords(user_input)
        main_topic = keywords[0] if keywords else "dialogue"
        
        # Get Wikipedia context for the topic[citation:9]
        context, valid_context = self.fetch_wikipedia_context(main_topic)
        
        # Generate Speaker A's response
        speaker_a_response = self.generate_response_with_5ws(main_topic, context)
        
        # Generate Speaker B's follow-up
        speaker_b_response = f"Speaker B: That's a good point about {main_topic}. "
        if valid_context:
            # Extract an interesting fact from context
            sentences = sent_tokenize(context)
            if len(sentences) > 1:
                fact = sentences[1] if len(sentences) > 1 else sentences[0]
                speaker_b_response += f"I also read that {fact.lower()} "
        
        # Add a question or reflection from Speaker B
        reflections = [
            "It makes me wonder how this applies in different contexts.",
            "This seems to connect with broader themes we've discussed.",
            "How do you think this has evolved over time?"
        ]
        speaker_b_response += random.choice(reflections)
        
        # Store in conversation history
        self.conversation_history.append({
            'topic': main_topic,
            'speaker_a': speaker_a_response,
            'speaker_b': speaker_b_response
        })
        
        # Create transition to next topic
        transition_text, next_topic = self.transition_to_new_topic(main_topic)
        self.current_topic = next_topic
        
        # Format the full dialogue
        dialogue = f"""
        Topic: {main_topic.upper()}
        
        Speaker A: {speaker_a_response}
        
        Speaker B: {speaker_b_response}
        
        {transition_text}
        
        Next potential topic: {next_topic.upper()}
        {'-'*60}
        """
        
        return dialogue, next_topic

    def run_endless_conversation(self, initial_prompt=None):
        """Run the endless conversation engine"""
        print("="*60)
        print("INTELLIGENT DIALOGUE ENGINE")
        print("="*60)
        print("This system simulates endless conversations between two speakers.")
        print("It uses Wikipedia for facts, NLP for understanding, and semantic links for transitions.")
        print("Type 'quit' to exit, 'history' to see recent topics, or just press Enter for auto-generation.")
        print("="*60)
        
        if initial_prompt:
            current_topic = initial_prompt
        else:
            current_topic = random.choice(["artificial intelligence", "space exploration", "renaissance art", "climate change"])
        
        while True:
            user_input = input(f"\nCurrent focus: {current_topic}\nYour input (or press Enter for auto): ").strip()
            
            if user_input.lower() == 'quit':
                print("\nEnding dialogue. Final topic was:", current_topic)
                break
            elif user_input.lower() == 'history':
                print("\nRecent Topics:")
                for i, item in enumerate(list(self.conversation_history)[-5:], 1):
                    print(f"{i}. {item['topic']}")
                continue
            elif not user_input:
                # Auto-generate based on current topic
                user_input = f"Let's discuss {current_topic}"
            
            # Generate dialogue exchange
            dialogue, next_topic = self.simulate_dialogue_exchange(user_input)
            print(dialogue)
            
            # Update current topic
            current_topic = next_topic
            
            # Optional: auto-continue
            auto_continue = input("Press Enter to continue, or type your own prompt: ").strip()
            if auto_continue:
                user_input = auto_continue

# ============================================
# Run the Engine
# ============================================

if __name__ == "__main__":
    # Initialize the engine
    engine = IntelligentDialogueEngine()
    
    # Example of a single exchange
    print("Example Dialogue Exchange:")
    print("-"*60)
    
    sample_dialogue, next_topic = engine.simulate_dialogue_exchange(
        "Let's talk about artificial intelligence and its impact on society"
    )
    print(sample_dialogue)
    
    # Ask user if they want to start endless conversation
    start_convo = input("\nStart endless conversation? (yes/no): ").strip().lower()
    if start_convo in ['yes', 'y']:
        initial = input("Initial topic (or press Enter for random): ").strip()
        if not initial:
            initial = None
        engine.run_endless_conversation(initial)
    else:
        print("\nSample dialogue complete. You can modify the code to explore different topics.")