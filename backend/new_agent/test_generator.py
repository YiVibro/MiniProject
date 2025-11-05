from typing import List, Dict, Any

def generate_test_from_topics(topics: List[Dict[str, Any]], num_mcq_per_topic: int = 2, num_short_per_topic: int = 1) -> List[Dict[str, Any]]:
    """Build a flat list of test questions from topics with embedded questions.

    Each topic may contain a `questions` array with objects that include fields:
    - question (str)
    - type ("multiple_choice" | "short_answer")
    - options (list[str]) for MCQ
    - answer (str)
    """
    questions: List[Dict[str, Any]] = []
    for topic in topics:
        qlist = topic.get("questions", [])
        mcqs = [q for q in qlist if q.get("type") == "multiple_choice"][:num_mcq_per_topic]
        shorts = [q for q in qlist if q.get("type") == "short_answer"][:num_short_per_topic]
        for q in mcqs + shorts:
            # Ensure a stable id
            qid = f"{topic.get('id','topic')}-{len(questions)+1}"
            questions.append({
                "id": qid,
                "question": q.get("question", ""),
                "type": q.get("type", "short_answer"),
                "options": q.get("options", []),
                "answer": q.get("answer", "")
            })
    return questions










