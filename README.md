# Conversational Context Builder (CCB)

A Python framework for analyzing and structuring conversations. The CCB extracts **intent**, **emotion**, **subtext**, tracks **conversation state**, generates **rolling summaries**, and provides structured context for downstream AI agents or dialog systems.

---

## 🚀 Features

- **Intent Detection:** Classifies user messages into intents (greeting, request, instruction, etc.).
- **Emotion Analysis:** Detects emotional tone in messages (neutral, happy, frustrated, etc.).
- **Subtext Extraction:** Infers hidden meaning, meta-intentions, and implied requests.
- **Conversation State Tracking:** Identifies the current stage of the conversation (GREETING, REQUEST, CLARIFICATION, etc.).
- **Memory Management:** Stores short-term and session memory for context continuity.
- **Summarization:** Produces rolling summaries and insights of the conversation.
- **Structured Output:** Provides a JSON schema for consistent internal context representation.
- **Modular Architecture:** Clean separation of modules for maintainability and extensibility.

---

## 📂 Repository Structure
CCB/
├─ main.py # Main execution script
├─ run_ccb.bat # CLI entry point (Windows)
├─ context_manager.py # Context handling logic
├─ memory_store.py # Short-term & session memory
├─ intent_analyzer.py # Intent classification
├─ emotion_classifier.py # Emotion detection
├─ subtext_inferencer.py # Subtext extraction
├─ state_manager.py # Conversation state machine
├─ summarizer.py # Rolling summary generator
├─ model_interface.py # Wrapper for ML/LLM models
├─ schema.py # Structured output schema
├─ utils.py # Helper functions
├─ logger.py # Logging utilities
├─ error_handler.py # Error handling
├─ config.py # Configuration
├─ requirements.txt # Python dependencies
└─ conversation.json # Example conversation history


---

## ⚡ Installation

1. Clone the repository:

```bash
git clone https://github.com/Hanae8B/CCB.git
cd CCB'''

2. Create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

3. Install dependencies:
pip install -r requirements.txt

---
## 🏃 Running the CCB

python main.py
# or, on Windows
run_ccb.bat

The system will process your messages and output structured context including intent, emotion, subtext, state, and conversation summaries.

---
## 🛠 Usage Example

You: Hello, how are you?
CCB: Intent: greeting | Emotion: neutral | Subtext: none | Summary: Conversation summary:
- Turn 1: Hello, how are you? (intent: greeting) (emotion: neutral)

Key insights:
- Dominant intent appears to be 'greeting'.
- Prevailing emotion is 'neutral'.

---
## 📄 License

This project is licensed under the GNU General Public License (GPL). See the LICENSE file for details.

---
## 📫 Author

Anna Baniakina
