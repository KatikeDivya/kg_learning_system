# Knowledge Graph-Driven Framework for Personalized Learning Path Recommendation

## Project Overview

The Knowledge Graph-Driven Framework for Personalized Learning Path Recommendation is an AI-powered application designed to generate personalized learning paths based on users' existing knowledge, learning goals, and career interests.

The system uses **Knowledge Graphs, Artificial Intelligence, and graph algorithms** to identify learning topics, establish prerequisite relationships, and recommend the next topics users should learn.

Users can interact with the application through its web interface, explore learning recommendations, and receive career suggestions. The framework also provides a visual representation of topic relationships through a knowledge graph.

The main objective of this project is to make learning more organized, efficient, and personalized by considering the user's current knowledge and the dependencies between learning topics.

## Features

- Accept user input for personalized learning recommendations.
- Extract relevant information from PDF documents.
- Generate learning topics using AI.
- Identify prerequisite relationships between topics.
- Construct dynamic knowledge graphs.
- Represent topics as nodes and prerequisites as directed edges.
- Recommend learning topics based on the user's existing knowledge.
- Generate personalized learning paths.
- Provide career recommendations based on user interests and skills.
- Visualize knowledge graphs through an interactive interface.
- Store application data and learning-related information in JSON format.
- Provide a web-based dashboard for accessing learning features.
- Support dynamic graph generation and visualization.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Web application and routing, if used in `app.py` |
| HTML | Structure of the web interface |
| CSS | Styling and responsive page design |
| JavaScript | Frontend interactions |
| NetworkX | Knowledge graph construction and graph algorithms, if used |
| Cohere API | AI-based text processing and topic generation, if configured |
| PyPDF | Extracting text from PDF documents, if used |
| JSON | Storing application data |
| Graph Visualization | Displaying topic relationships and learning dependencies |

**Note:** Confirm the specific libraries and API integrations against `requirements.txt` and your source code.

## How It Works

The system follows a knowledge graph-based recommendation workflow.

1. **User Input:** The user provides learning requirements, uploads a PDF document, or enters information through the available interface.

2. **Input Processing:** The application processes the input and identifies the relevant learning domain and topics.

3. **Topic Generation:** AI-based processing generates relevant learning topics and identifies prerequisite relationships.

4. **Knowledge Graph Construction:** The system creates a graph in which nodes represent learning topics and directed edges represent prerequisite relationships.

5. **User Knowledge Identification:** The application considers topics the user already knows to determine which topics are suitable for further learning.

6. **Recommendation Generation:** The recommendation engine analyzes the knowledge graph and identifies topics that can be learned next.

7. **Learning Path Generation:** The system organizes recommended topics into a logical sequence based on prerequisite dependencies.

8. **Career Recommendation:** The career recommendation module analyzes available user information and generates relevant career suggestions.

9. **Data Management:** The application stores and manages relevant application data using its data management components and JSON storage.

10. **Visualization and Output:** The application displays personalized learning recommendations, career suggestions, and knowledge graph visualizations through the web interface.

## Project Structure

```text
Knowledge-Graph-Driven-Learning-Path/
│
├── data/
│   └── data_store.json
│
├── static/
│   ├── Background.jpg
│   ├── graph.js
│   ├── script.js
│   └── style.css
│
├── templates/
│   ├── career.html
│   ├── dashboard.html
│   ├── graph.html
│   └── index.html
│
├── .gitignore
├── LICENSE
├── app.py
├── career_recommender.py
├── cohere_utils.py
├── data_manager.py
├── dynamic_graph.py
├── graph_loader.py
├── main.py
├── pdf_extractor.py
├── recommender.py
├── requirements.txt
└── README.md
```

### Description of Important Files

| File or Folder | Description |
|---|---|
| `app.py` | Main web application entry point, if configured that way |
| `main.py` | Main execution or processing module |
| `career_recommender.py` | Handles career recommendation functionality |
| `cohere_utils.py` | Provides utilities for interacting with Cohere, if configured |
| `data_manager.py` | Manages application data and storage operations |
| `dynamic_graph.py` | Handles dynamic knowledge graph generation |
| `graph_loader.py` | Loads graph data for further processing or visualization |
| `pdf_extractor.py` | Extracts text from PDF documents |
| `recommender.py` | Generates learning topic or learning path recommendations |
| `data/data_store.json` | Stores application data in JSON format |
| `static/graph.js` | Handles graph-related frontend functionality |
| `static/script.js` | Handles frontend interactions |
| `static/style.css` | Contains website styling |
| `static/Background.jpg` | Provides the application's background image |
| `templates/index.html` | Main page of the web application |
| `templates/dashboard.html` | Dashboard interface |
| `templates/career.html` | Career recommendation interface |
| `templates/graph.html` | Knowledge graph visualization page |
| `requirements.txt` | Lists Python dependencies |
| `.gitignore` | Specifies files Git should ignore |
| `LICENSE` | Defines the project's license |

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Navigate to the Project Folder

```bash
cd Knowledge-Graph-Driven-Learning-Path
```

Use your actual repository folder name if it is different.

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the API Key

If your project uses the Cohere API, configure the API key required by your implementation.

For example, if the application reads the key from an environment variable named `COHERE_API_KEY`, create a `.env` file in the project directory and add:

```ini
COHERE_API_KEY=your_cohere_api_key
```

Obtain an API key from the [Cohere Dashboard](https://dashboard.cohere.com/).

Install and configure `python-dotenv` if your application requires it and it is not already included in your dependencies.

**Important:** Use the exact environment variable name expected by your code. Never upload your actual API key to GitHub. Add `.env` to `.gitignore`.

If your application obtains its API key through another configuration method, follow that implementation instead.

### 7. Run the Application

If `app.py` is the Flask entry point, execute:

```bash
python app.py
```

Alternatively, if `main.py` is the intended entry point, use the command specified by your project configuration.

### 8. Open the Application

If Flask runs locally on its default development port, open:

```text
http://127.0.0.1:5000
```

Use the actual address and port displayed in your terminal if they differ.

## System Architecture

The project processes user input, generates a learning knowledge graph, and produces personalized recommendations.

```text
          User Input
      (Text / PDF / Quiz)
               |
               v
       Input Processing
               |
               v
    AI-Based Topic Generation
               |
               v
   Prerequisite Identification
               |
               v
      Dynamic Graph Creation
               |
               v
       User Knowledge Mapping
               |
               v
     Learning Recommendation
               |
               v
    Personalized Learning Path
               |
               v
       Data Management
               |
               v
             Output
       /        |        \
      v         v         v
  Learning    Career    Knowledge
    Path   Recommendations  Graph
```

## Knowledge Graph Representation

The knowledge graph represents relationships and dependencies between learning topics.

- **Nodes:** Represent individual learning topics.
- **Directed Edges:** Represent prerequisite relationships between topics.
- **User Knowledge:** Represents the topics the user already knows.
- **Graph Analysis:** Helps determine the order in which topics can be learned.
- **Learning Recommendations:** Identify appropriate next topics based on prerequisite completion and existing knowledge.

For example, a user who wants to learn Machine Learning may first need to understand Python programming, basic mathematics, and relevant statistics before studying advanced algorithms.

The framework can use these prerequisite relationships to suggest a suitable learning sequence.

## Advantages

- Provides personalized learning paths.
- Organizes topics according to prerequisite relationships.
- Helps users identify topics they need to learn.
- Supports AI-based topic generation.
- Provides career-oriented recommendations.

