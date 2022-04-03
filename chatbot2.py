from datetime import date
from random import randint


class ChatBot(object):
    def __init__(self, form_read, form_write):
        self.form_read = form_read
        self.form_write = form_write
        self.questions_and_answers = {}

    def run(self):
        print("Hello! You have " + self.get_questionnaire_name() + "left to fill out.")
        val = input("Would you like to get started? ")
        if val.strip().lower() == "yes":
            self.read_questions()
        else:
            print("Okay, see you later!")

    def get_questionnaire_name(self):
        form = open(self.form_read, "r")
        name = form.readline()
        form.close()
        return name

    def read_questions(self):
        form = open(self.form_read, "r")
        answer_file = open(self.form_write, "w")
        form.readline()
        while True:
            line = form.readline()
            if not line:
                break
            parts = line.split(":")
            ask_question = True
            if parts[0] in list(self.questions_and_answers):
                self.questions_and_answers[parts[0] + str(randint(100, 999))] = parts[1]
                self.identify_type(answer_file, True)
                ask_question = False
            else:
                self.questions_and_answers[parts[0]] = parts[1]
            if not self.dependent_questions(answer_file) and ask_question:
                self.identify_type(answer_file, False)
        form.close()
        answer_file.close()

    def identify_type(self, answer_file, is_repeat_question):
        orig_question = list(self.questions_and_answers)[-1]
        question = orig_question
        if is_repeat_question:
            question = orig_question[:len(orig_question) - 3]
        ask_question = True
        answers = self.questions_and_answers[orig_question]
        if "if yes" in question.lower():
            previous = list(self.questions_and_answers)[-2]
            if self.questions_and_answers[previous] == "No":
                question_to_delete = list(self.questions_and_answers)[-1]
                ask_question = False
                del self.questions_and_answers[question_to_delete]
                return
        if ask_question:
            # if "?" in question or "list" in question.lower() or "if yes" in question.lower():
            if answers.strip() == "blank":
                self.blank_question(question, answer_file)
            elif "multi select" in answers:
                self.question_with_options_multiple_answers(question, answer_file)
            elif "yes" and "no" in answers.strip().lower():
                self.yes_or_no_questions(question, answer_file)
            elif "Y/P" in answers:
                self.y_or_p(question, answer_file)
            elif "," in answers:
                self.question_with_options_1_answer(question,
                                                    answer_file)

    def blank_question(self, question_to_ask, file_to_write):
        answer = input(question_to_ask + ": ")
        while answer == "":
            answer = input(question_to_ask + ": ")
        orig_question = list(self.questions_and_answers)[-1]
        file_to_write.write(question_to_ask + ": " + answer + "\n")
        self.questions_and_answers[orig_question] = answer

    def question_with_options_1_answer(self, question_to_ask, file_to_write):
        orig_question = list(self.questions_and_answers)[-1]
        options = self.questions_and_answers[orig_question].split(",")
        print(question_to_ask + "\nPlease enter the number which best applies.")
        counter = 1
        for option in options:
            print(str(counter) + ": " + option)
            counter += 1
        answer = input("")
        while int(answer) < 1 or int(answer) > len(options):
            answer = input("Please enter the number which best applies.")
        file_to_write.write(question_to_ask + ": " + options[int(answer) - 1] + "\n")
        self.questions_and_answers[orig_question] = answer

    def dependent_questions(self, file_to_write):
        orig_question = list(self.questions_and_answers)[-1]
        if orig_question.lower().strip() == "date":
            file_to_write.write(orig_question + ": " + str(date.today()))
            return True
        return False

    def question_with_options_multiple_answers(self, question_to_ask, file_to_write):
        orig_question = list(self.questions_and_answers)[-1]
        options = self.questions_and_answers[orig_question].split(",")
        options.remove(options[0])
        print(question_to_ask + "\nPlease enter the numbers which best apply. Separate each number by a comma.")
        counter = 1
        for option in options:
            print(str(counter) + ": " + option)
            counter += 1
        answer = input("")
        answers = answer.strip().split(",")

        file_to_write.write(question_to_ask + ": ")
        valid_answer = True
        for num in answers:
            num = int(num.strip())
            if num < 1 or num > len(options):
                self.reask_question_multi_select(question_to_ask, options)

        for num in answers:
            file_to_write.write(options[int(num) - 1])

        file_to_write.write("\n")
        self.questions_and_answers[orig_question] = answers

    def reask_question_multi_select(self, question_to_ask, options):
        print("Please enter the numbers which best apply. Separate each number by a comma.")
        answer = input("")
        answers = answer.strip().split(",")
        self.check_answer_multi_select(question_to_ask, options, answers)
        return answers

    def check_answer_multi_select(self, question_to_ask, options, answers):
        for num in answers:
            num = int(num.strip())
            if num < 1 or num > len(options):
                self.reask_question_multi_select(question_to_ask, options)
        return answers

    def yes_or_no_questions(self, question_to_ask, file_to_write):
        print(question_to_ask + "\nPlease enter 1 for \"Yes\" and 2 for \"No\".")
        orig_question = list(self.questions_and_answers)[-1]
        answer = input("")
        while answer.strip() != "1" and answer.strip() != "2":
            answer = input("Please enter the number which best applies.")
        if int(answer.strip()) == 1:
            file_to_write.write(question_to_ask + ": " + "Yes" + "\n")
            self.questions_and_answers[orig_question] = "Yes"
        else:
            file_to_write.write(question_to_ask + ": " + "No" + "\n")
            self.questions_and_answers[orig_question] = "No"

    def y_or_p(self, question_to_ask, file_to_write):
        print(question_to_ask + "\nPlease enter Y for symptoms you currently have, P for past symptoms (not a "
                                "problem now but was in the past), and N for never a symptom.")
        orig_question = list(self.questions_and_answers)[-1]
        answer = input("")
        while answer.strip().lower() != "y" and answer.strip().lower() != "p" and answer.strip().lower() != "n":
            answer = input("Please enter the letter which best applies.")
        if answer.strip().lower() == "y":
            file_to_write.write(question_to_ask + ": " + "Currently has" + "\n")
            self.questions_and_answers[orig_question] = "Y"
        elif answer.strip().lower() == "p":
            file_to_write.write(question_to_ask + ": " + "Past symptom" + "\n")
            self.questions_and_answers[orig_question] = "P"
        elif answer.strip().lower() == "n":
            file_to_write.write(question_to_ask + ": " + "Never a symptom" + "\n")
            self.questions_and_answers[orig_question] = "n"





chat1 = ChatBot("AdultNewPatientIntake.txt", "AdultNewPatientIntakeFilled.txt")
chat1.run()
