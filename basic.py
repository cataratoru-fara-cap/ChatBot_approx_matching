import json
from difflib import get_close_matches

import gradio


def load_base(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data: dict = json.load(file)
    return data


def save_base(file_path: str, data: dict):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)  # noqa

    return matches[0] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]


def add_answer_from_user(
    path_to_knowledge: str, knowledge_base: dict, user_input: str
) -> None:  # noqa
    print("Bot: I don't know the answer, Can you teach me?\n")
    new_answer: str = input('Type the answer or "skip" to skip:\n')  # noqa

    if new_answer.lower() != "skip":
        knowledge_base["questions"].append(
            {"question": user_input, "answer": new_answer}
        )  # noqa
        save_base(path_to_knowledge, knowledge_base)
        print("Bot: Thank you! I learned a new response!")


def add_question_to_unanswered(
    path_to_unanswered: str, user_input: str
) -> None:  # noqa
    print(
        """Bot: I don't know the answer, I will check, please try again later.
        For more information you can contactthe secretary office at
        999-999-99 between now and forever """
    )
    unanswered_base: dict = load_base(path_to_unanswered)
    unanswered_base["questions"].append({"question": user_input})
    save_base(path_to_unanswered, unanswered_base)


def chat_bot(path_to_knowledge: str, path_to_unanswered: str):
    knowledge_base: dict = load_base(path_to_knowledge)

    while True:
        user_input: str = input("You: ")

        if user_input.lower() == "quit" or user_input.lower() == "exit":
            break

        questions = [q["question"] for q in knowledge_base["questions"]]
        best_match: str | None = find_best_match(user_input, questions)

        if best_match:
            answer: str = get_answer_for_question(best_match, knowledge_base)
            print(f"Bot: {answer}")
        else:
            # add_answer_from_user(path_to_knowledge, knowledge_base, user_input) # noqa
            add_question_to_unanswered(path_to_unanswered, user_input)


def custom_bot(user_input: str) -> str:
    knowledge_base: dict = load_base("knowledge_base.json")
    unanswered_base: dict = load_base("unanswered_base.json")

    questions = [q["question"] for q in knowledge_base["questions"]]
    best_match: str | None = find_best_match(user_input, questions)

    if best_match:
        answer: str = get_answer_for_question(best_match, knowledge_base)
        return answer
    else:
        # add_answer_from_user(path_to_knowledge, knowledge_base, user_input) # noqa
        # The print statement inside add_question_to_unanswered thankfully gets  ignored by gradio
        add_question_to_unanswered(
            user_input=user_input, path_to_unanswered="unanswered_base.json"
        )
        return """ I don't know the answer, I will check, please try again later.
        For more information you can contact the secretary office at
        999-999-99 between now and forever """


def main() -> None:
    # chat_bot("knowledge_base.json", "unanswered_base.json")

    demo = gradio.Interface(
        fn=custom_bot, inputs="text", outputs="text", title="ChatBot"
    )
    demo.launch(share=True)


if __name__ == "__main__":
    main()
