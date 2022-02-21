#!/usr/bin/env python3

"""
Inputs:
    - Participant category
        - OA
        - Healthy
    - Food category
        - Pudding
        - Jello
        - Both

Processing:
You have categories of questions
    - Intensity (12)
    - Like/dislike (16)
    - Sweetness (9)
    - Oily (5)
    - Fatty (2)
    - Creamy (1)
    - Familiar (0)
    - Wanting (8)
Some overarching categories (first 3 and last 3 questions)
    - Hungry (3)
    - Full (4)
    - Thirsty (7)

You have questions. Let's treat a question as an item. What makes up a "Question"?
    - Category
    - Score
What makes up a category (for questions)?
    - One word description (or even the full question phrase)
    - Code number

You have 3 general question categories. After going through the data, you collect frequencies and accumulated scores for each category:
Category
    - Metadata about category (code number and description)
    - Frequency
    - Accumulated score

You have 8 food-specific question categories. After going through the data, you collect frequencies and accumulated scores for each category:
Category
    - Metadata about category (code number and description)
    - Food
    - Frequency
    - Accumulated score

Outputs:
    - Average scores for each category of question
    - Stored as an xlsx file
"""

import csv
from enum import Enum

import toml
import xlsxwriter

# participant categories
# when you want to refer to these enumerations, use Paricipant.X
class Participant(Enum):
    OA = 'Osteoarthritis knee'
    HEALTHY = 'Healthy control'

# food categories
# when you want to refer to these enumerations, use Food.X
class Food(Enum):
    PUDDING = 'Pudding'
    JELLO = 'Jello'
    BOTH = 'Both (pudding, jello)'

# to create a subject, use Subject(id, profile)
class Subject:
    def __init__(self, id, pudding_profile, jello_profile):
        self.id = id
        self.pudding_profile = pudding_profile
        self.jello_profile = jello_profile
    
    def __repr__(self):
        return f'{self.id} - {self.pudding_profile + self.jello_profile}'

    def get_profile(self, food_type):
        if food_type is Food.PUDDING:
            return self.pudding_profile
        elif food_type is Food.JELLO:
            return self.jello_profile

class Question():
    def __init__(self, id, description):
        self.id = id
        self.description = description

class StateQuestion(Question):
    def __init__(self, id, description):
        super().__init__(id, description)
        self.begin_score = None
        self.end_score = None
    
    def __repr__(self):
        return f'{self.id} - {self.description} - {self.get_scores()}'

    def __eq__(self, id):
        return self.id == id

    def add_score(self, score):
        if self.begin_score is None:
            self.begin_score = score
        else:
            self.end_score = score

    def get_scores(self):
        return [self.begin_score, self.end_score]

# concentration can mean % fat (pudding) or sucrose concentration (jello)
class FoodQuestion(Question):
    def __init__(self, id, description, food, concentration):
        super().__init__(id, description)
        self.food = food
        self.frequency = 0
        self.score = 0.0
        self.concentration = concentration
    
    def __repr__(self):
        return f'{self.id} - {self.food} - {self.concentration} - {self.description} - {self.average_score()}'

    def __eq__(self, identifier):
        id, food, concentration = identifier
        return self.id == id and self.food == food and self.concentration == concentration

    def add_score(self, score):
        self.score += score
        self.frequency += 1

    def average_score(self):
        return self.score / self.frequency

state_questions = \
[
    StateQuestion(id=3, description='How hungry are you right now?'),
    StateQuestion(id=4, description='How full are you right now?'),
    StateQuestion(id=7, description='How thirsty are you right now?'),
]
food_questions = []

def process_food_questions(questions, food_type):
    profile = subject.get_profile(food_type=food_type)
    # concentration can mean both % fat (pudding) and sucrose concentration (jello)
    for index, concentration in enumerate(profile):
        questions_for_conc = questions[8*index:8*(index + 1)]
        for question in questions_for_conc:
            id = int(question[0])
            score = float(question[-1])
            if (id, food_type, concentration) not in food_questions:
                food_questions.append(FoodQuestion(id=id, description=question[1], food=food_type, concentration=concentration))
            question_index = food_questions.index([id, food_type, concentration])
            food_questions[question_index].add_score(score)

# -----------------------------------------------------------------------

def process_configurable_data():
    data = toml.load('config.toml')
    # set participant type
    if data['participant_type'].lower() == 'healthy':
        participant_type = Participant.HEALTHY
    elif data['participant_type'].lower() == 'oa':
        participant_type = Participant.OA
    else:
        raise ValueError('Wrong participant type provided')
    
    # set food type
    if data['food_type'].lower() == 'pudding':
        food_type = Food.PUDDING
    elif data['food_type'].lower() == 'jello':
        food_type = Food.JELLO
    elif data['food_type'].lower() == 'both':
        food_type = Food.BOTH
    else:
        raise ValueError('Wrong food type provided')

    # set subject
    subject = Subject(id=data['subject_id'], pudding_profile=data['pudding_profile'], jello_profile=data['jello_profile'])

    return participant_type, food_type, subject

participant_type, food_type, subject = process_configurable_data()

# -----------------------------------------------------------------------

# Diagnostic information
print(f'Participant type: {participant_type}')
print(f'Food type: {food_type}')
print(f'Subject: {subject}')
print('---\tReading data file\t---')

input_file_name = 'data.txt'
input_file_handle = open(input_file_name)
input_file = csv.reader(input_file_handle, delimiter='\t')

"""
iterate through each line:
    note that line's question category
    for that category, add the score
"""

# processes the input to exclude empty lines
lines = []
for line in input_file:
    if line[0] == '':
        continue
    lines.append(line)

# the first and last 3 questions are state questions
state_question_lines = lines[:3] + lines[-3:]
# everything in between are food questions
food_question_lines = lines[3:-3]

print(f'---\tFound {len(lines)} questions\t---')

print(f'---\tProcessing state questions\t---')
# process the state questions
for question in state_question_lines:
    id = int(question[0])
    question_index = state_questions.index(id)
    score = float(question[-1])
    state_questions[question_index].add_score(score)

print(f'---\tProcessing food questions\t---')
# process the food questions
if food_type is Food.BOTH:
    # do something
    pudding_question_lines = food_question_lines[:len(food_question_lines)//2]
    process_food_questions(questions=pudding_question_lines, food_type=Food.PUDDING)
    jello_question_lines = food_question_lines[len(food_question_lines)//2:]
    process_food_questions(questions=jello_question_lines, food_type=Food.JELLO)
else:
    process_food_questions(questions=food_question_lines, food_type=food_type)

input_file_handle.close()

# -----------------------------------------------------------------------

def food_type_descr(food_type):
    if food_type is Food.BOTH:
        return 'PuddingJello'
    else:
        return food_type.value

def get_keyword(description):
    keyword_map = {
        'How hungry are you right now?': 'Hunger',
        'How full are you right now?': 'Fullness',
        'How thirsty are you right now?': 'Thirst',
        'How familiar is this flavor?': 'Familiarity',
        'How creamy is this food?': 'Creaminess',
        'How fatty is this food?': 'Fattiness',
        'How oily is this food?': 'Oiliness',
        'How much do you want to eat this at the end of the experiment?': 'Wanting',
        'Rate Sweetness': 'Sweetness',
        'Rate Intensity': 'Intensity',
        'How much do you like or dislike the item?': 'Liking',
    }
    return keyword_map[description]

def get_sorted_output(food):
    if food not in (Food.PUDDING, Food.JELLO):
        return None
    elif food is not food_type and food_type is not Food.BOTH:
        return None
    profile = sorted(set(subject.get_profile(food_type=food)))
    output = {}
    for concentration in profile:
        descr_score_pairs = []
        for question in food_questions:
            if question.food == food and question.concentration == concentration:
                keyword = get_keyword(question.description)
                descr_score_pairs.append([keyword, question.average_score()])
        output[concentration] = descr_score_pairs
    return output
    
if food_type is Food.BOTH:
    pudding_data = get_sorted_output(food=Food.PUDDING)
    jello_data = get_sorted_output(food=Food.JELLO)
else:
    pudding_data = get_sorted_output(food=food_type)
    jello_data = get_sorted_output(food=food_type)

out_book = xlsxwriter.Workbook(f'{subject.id}_{food_type_descr(food_type)}.xlsx')
out_sheet = out_book.add_worksheet()

pudding_row = 0
pudding_col = 0
jello_row = 11
jello_col = 0
general_row = 23
general_col = 0

def write_data(sheet, data, start_row, start_col, label):
    if data is None:
        return False
    
    row, col = start_row, start_col
    
    # write the label at the pivot cell
    sheet.write(row, col, label)

    # write the question categories in the first column
    row += 1
    for q, _ in data[0]:
        sheet.write(row, col, q)
        row += 1
    
    # write the scores for each category, concentration pair
    col += 1
    for c, qa_list in data.items():
        row = start_row
        sheet.write(row, col, c)
        row += 1
        for _, a in qa_list:
            sheet.write(row, col, a)
            row += 1
        col += 1
    
    return True

merge_format = out_book.add_format({'align': 'center', 'valign': 'vcenter',})

# write pudding data
if write_data(sheet=out_sheet, data=pudding_data, start_row=pudding_row, start_col=pudding_col, label='% Fat'):
    out_sheet.merge_range('F1:F9', Food.PUDDING.value, merge_format)

# write jello data
if write_data(sheet=out_sheet, data=jello_data, start_row=jello_row, start_col=jello_col, label='Sucrose Concentration'):
    out_sheet.merge_range('F12:F20', Food.JELLO.value, merge_format)

# write general data
out_sheet.write(general_row - 1, general_col + 1, 'Beginning')
out_sheet.write(general_row - 1, general_col + 2, 'End')
for q in state_questions:
    out_sheet.write(general_row, general_col, get_keyword(q.description))
    out_sheet.write(general_row, general_col + 1, q.begin_score)
    out_sheet.write(general_row, general_col + 2, q.end_score)
    general_row += 1

out_book.close()