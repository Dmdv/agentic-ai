import chromadb
import os

class HiveMemory:
    """
    Tier 2 Procedural Memory (The Hive Mind).
    Stores heuristics, lessons learned, and context dynamically using a local Vector DB.
    """
    def __init__(self, db_path=".hive_memory"):
        # Use a persistent local ChromaDB instance
        self.client = chromadb.PersistentClient(path=os.path.abspath(db_path))
        self.collection = self.client.get_or_create_collection(name="agent_skills")

    def add_lesson(self, task: str, lesson: str):
        """Saves a learned lesson to the procedural memory."""
        doc_id = str(hash(task + lesson))
        self.collection.upsert(
            documents=[lesson],
            metadatas=[{"task": task}],
            ids=[doc_id]
        )

    def get_relevant_lessons(self, prompt: str, n_results=3) -> str:
        """Retrieves past lessons relevant to the current prompt."""
        if self.collection.count() == 0:
            return ""
            
        results = self.collection.query(
            query_texts=[prompt],
            n_results=min(n_results, self.collection.count())
        )
        
        if not results['documents'] or not results['documents'][0]:
            return ""
            
        lessons = [f"- {doc}" for doc in results['documents'][0]]
        return "\n".join(lessons)

if __name__ == "__main__":
    # Quick test
    memory = HiveMemory()
    memory.add_lesson("Fix Docker", "Always use python:3.11-slim instead of alpine for ML workloads.")
    print("Test retrieval:")
    print(memory.get_relevant_lessons("Write a dockerfile for an AI app"))
