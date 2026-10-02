# 🚨 AEGIS – Emergency Evacuation Route Planner

AEGIS is an emergency evacuation route planning system that finds the shortest available route when a path becomes blocked.

## 💡 How It Works

- Building is represented as a weighted graph.
- Rooms, corridors, staircases and exits are represented as nodes.
- Connections are represented as edges.
- Blocked connections are avoided.
- Dijkstra's algorithm finds the shortest available route.
- The system displays the recommended route and exit.

## 🛠️ Technologies

- Python
- Streamlit
- NetworkX
- Dijkstra's Algorithm
- JSON

## 📁 Project Structure

```text
app.py
graph.py
dijkstra.py
requirements.txt
data/
└── building_map.json
```

## ▶️ Run the Project

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🚀 Future Scope

- Real-time fire and smoke detection
- Sensor and IoT integration
- Indoor positioning
- Multi-floor buildings
- Risk-aware route planning

## 👨‍💻 Project

**AEGIS – Emergency Evacuation Route Planner**

Built with Python and Graph Algorithms.
