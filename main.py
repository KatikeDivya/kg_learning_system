from dynamic_graph import generate_learning_graph
from graph_loader import build_graph
from recommender import create_user_knowledge, recommend_next_topics, generate_learning_path
from cohere_utils import detect_domain, extract_topics, generate_roadmap
from data_manager import add_query
from dotenv import load_dotenv

load_dotenv()


def main():
    print("\n===== Personalized Learning System =====\n")

    user_input = input("Enter what you know: ")

    # Step 1: Detect domain
    domain = detect_domain(user_input)
    print(f"\nDetected Domain: {domain}")

    # Step 2: Extract topics
    topics = extract_topics(user_input)
    print(f"Extracted Topics: {topics}")

    # Step 3: Get graph data
    domain_data = generate_learning_graph(domain)

    # Step 4: Build graph
    G = build_graph(domain_data)

    # Step 5: Create user knowledge
    user_knowledge = create_user_knowledge(G, topics)

    # Step 6: Recommend next topics
    recommendations = recommend_next_topics(G, user_knowledge)

    # Step 7: Full learning path
    learning_path = generate_learning_path(G, user_knowledge)

    print("\n----------------------------------")
    print("Known Topics:")
    for t in topics:
        print(f"✔ {t}")

    print("\nRecommended Next Topics:")
    for r in recommendations:
        print(f"➡ {r}")

    print("\nFull Learning Path:")
    print("➡ " + " → ".join(learning_path))

    print("\n----------------------------------")

    # Optional roadmap display
    print("\n📚 Full Roadmap:\n")
    print(generate_roadmap(domain))

    #  SAVE TO DATA STORE
    add_query(
        user_input=user_input,
        domain=domain,
        learning_path=learning_path,
        recommendations=recommendations,
        graph_data=domain_data
    )
    
    print("\n Data saved to data_store.json")


if __name__ == "__main__":
    main()