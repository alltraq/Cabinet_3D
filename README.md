# Smart Shelf LED Controller App

This Python application monitors shelf light switch events and active RFID device locations to control LED indicators on a cabinet. It determines which LED to activate and what color to display based on sensor input and spatial proximity.

---

## 🧠 Project Overview

- **Trigger Input 1:** Light switch message (shelf activity)
- **Trigger Input 2:** RFID tag location message (x, y, z)
- **Action:** Send command to LED controller to display RED, BLUE, or WHITE based on logic
- **Timeout:** LED automatically turns OFF after a configured delay

---

## 🚀 Features

- Receives and parses messages from switches and RFID systems
- Determines shelf proximity using configurable thresholds
- Sends LED control messages over a network (UDP/TCP)
- Configurable color rules and behavior
- Modular, testable Python architecture

---

## 📁 Project Structure
smart_shelf_led_controller/
├── config/ # YAML configuration
├── docs/ # Design docs (PRD, architecture, diagrams)
├── src/ # Source code
├── tests/ # Unit tests
├── scripts/ # Helper setup or deploy scripts
├── requirements.txt
└── README.md


---

## ⚙️ Configuration

All behavior is driven by the YAML file located in `config/config.yaml`.

```yaml
proximity_threshold: 1.5
led_colors:
  initial: "red"
  rfid_match: "blue"
  rfid_miss: "white"
  off: "off"
led_timeout: 5

Update the shelf coordinates and network settings to match your deployment.

## 📦 Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/yourusername/smart-shelf-led-controller.git
cd smart-shelf-led-controller
Create a virtual environment:

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
🧪 Running the App
bash
Copy
Edit
python src/main.py
Make sure your hardware is connected and your config.yaml is correct before running.

🧪 Testing
Run unit tests using pytest:

bash
Copy
Edit
pytest tests/
📄 Documentation
Product Requirements (PRD)

Architecture Overview

Communication Protocols

Shelf Diagrams

🛠️ Tech Stack
Python 3.9+

Socket (UDP/TCP)

YAML for configuration

Pytest for testing

📬 Contact
For questions, contact [yourname@example.com] or open an issue on the repo.