#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import json


ROOT = pathlib.Path(__file__).resolve().parents[1]
TRANSLATION_CACHE_PATH = ROOT / "scripts" / "example_translations.json"
TABLE_HEADER = "| 序号 | 单词 | 英式音标 | 美式音标 | 中文翻译 |"
TABLE_HEADER_WITH_EXAMPLES = "| 序号 | 单词 | 英式音标 | 美式音标 | 中文翻译 | 例句 | 例句翻译 |"
TABLE_DIVIDER_WITH_EXAMPLES = "| --- | --- | --- | --- | --- | --- | --- |"
MORE_EXAMPLES_HEADING = "## 更多例句"
MORE_EXAMPLE_COUNT = 3
_TRANSLATION_CACHE: dict[str, str] | None = None

WHITESPACE_RE = re.compile(r"\s+")
ELLIPSIS_RE = re.compile(r"\s*(?:\.\.\.|…)\s*")
HEADER_CELLS = ["序号", "单词", "英式音标", "美式音标", "中文翻译"]
HEADER_CELLS_WITH_EXAMPLES = HEADER_CELLS + ["例句", "例句翻译"]

PROTECTED_DOT_TERMS = {
    "a.m.",
    "p.m.",
    "A.M.",
    "P.M.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "Ms",
    "P.E.",
}

VOWEL_SOUND_PREFIXES = (
    "a",
    "e",
    "i",
    "o",
    "u",
    "honest",
    "hour",
    "x-",
)

PLURAL_OR_MASS_NOUNS = {
    "clothes",
    "pants",
    "shorts",
    "trousers",
    "jeans",
    "glasses",
    "scissors",
    "chopsticks",
    "goods",
    "works",
    "woods",
    "thanks",
    "congratulations",
    "earnings",
    "surroundings",
    "stairs",
    "outdoors",
    "rapids",
    "news",
    "maths",
    "physics",
    "politics",
    "phonetics",
    "athletics",
}

UNCOUNTABLE_TERMS = {
    "water",
    "milk",
    "rice",
    "bread",
    "juice",
    "tea",
    "coffee",
    "food",
    "homework",
    "housework",
    "information",
    "advice",
    "news",
    "weather",
    "music",
    "work",
    "money",
    "time",
    "progress",
    "knowledge",
    "furniture",
    "equipment",
    "luggage",
    "baggage",
    "traffic",
    "pollution",
    "air",
    "energy",
    "power",
    "electricity",
    "research",
    "evidence",
    "experience",
    "luck",
    "fun",
    "health",
    "peace",
    "silence",
    "freedom",
    "education",
    "culture",
    "transport",
    "vocabulary",
    "pronunciation",
    "grammar",
}

FUNCTION_WORD_EXAMPLES = {
    "a": "I saw a bird in the tree.",
    "an": "An apple is on the table.",
    "the": "The book is on my desk.",
    "i": "I like learning English.",
    "me": "Please help me with this word.",
    "my": "My bag is blue.",
    "mine": "This pencil is mine.",
    "you": "You can read this sentence aloud.",
    "your": "Your answer is clear.",
    "yours": "This book is yours.",
    "he": "He plays basketball after school.",
    "him": "I met him at the gate.",
    "his": "His notebook is on the desk.",
    "she": "She reads English every morning.",
    "her": "Her schoolbag is red.",
    "hers": "The blue pen is hers.",
    "it": "It is a sunny day.",
    "its": "The dog wagged its tail.",
    "we": "We study together after class.",
    "us": "The teacher asked us a question.",
    "our": "Our classroom is clean.",
    "ours": "This classroom is ours.",
    "they": "They are playing in the park.",
    "them": "I can see them from here.",
    "their": "Their team won the game.",
    "theirs": "The new bikes are theirs.",
    "this": "This is my English book.",
    "that": "That is a red apple.",
    "these": "These are my friends.",
    "those": "Those flowers are beautiful.",
    "here": "Please sit here.",
    "there": "There is a map on the wall.",
    "what": "What is your name?",
    "who": "Who is your English teacher?",
    "whose": "Whose coat is this?",
    "where": "Where do you live?",
    "when": "When do you get up?",
    "why": "Why are you late?",
    "how": "How do you spell this word?",
    "and": "Tom and Mary are classmates.",
    "or": "Would you like tea or water?",
    "but": "I am tired, but I will finish my homework.",
    "so": "It was raining, so we stayed inside.",
    "because": "I stayed home because I was sick.",
    "if": "If it rains, we will read at home.",
    "than": "This bag is heavier than that one.",
    "as": "Please do as I say.",
    "of": "This is a photo of my family.",
    "to": "I go to school by bus.",
    "in": "The keys are in the box.",
    "on": "The cup is on the table.",
    "at": "I get up at seven.",
    "for": "This gift is for you.",
    "from": "I come from China.",
    "with": "I play chess with my brother.",
    "about": "We talked about our weekend.",
    "into": "She walked into the classroom.",
    "over": "The plane flew over the city.",
    "under": "The cat is under the chair.",
    "up": "Please stand up.",
    "down": "Please sit down.",
    "out": "The children ran out to play.",
    "by": "I go to school by bike.",
    "off": "Please turn off the light.",
    "again": "Please read the sentence again.",
    "also": "I also like English.",
    "too": "I like apples too.",
    "very": "This story is very interesting.",
    "not": "I am not afraid.",
    "no": "No, I do not need help.",
    "yes": "Yes, I can help you.",
    "ok": "OK, let's start now.",
    "am": "I am ready for class.",
    "is": "She is my friend.",
    "are": "They are in the classroom.",
    "was": "It was cold yesterday.",
    "were": "We were happy at the party.",
    "be": "Try to be kind to others.",
    "been": "I have been to that city once.",
    "being": "Being honest is important.",
    "have": "I have a new dictionary.",
    "has": "She has a beautiful voice.",
    "had": "We had a good time yesterday.",
    "do": "Do your homework carefully.",
    "does": "He does his homework after dinner.",
    "did": "She did well in the test.",
    "can": "I can speak a little English.",
    "could": "Could you open the window?",
    "may": "May I come in?",
    "might": "It might rain this afternoon.",
    "must": "You must finish your homework first.",
    "should": "You should drink more water.",
    "will": "I will call you tonight.",
    "would": "Would you like some tea?",
    "shall": "Shall we go now?",
    "both": "Both answers are correct.",
    "all": "All students are here.",
    "each": "Each student has a book.",
    "every": "Every child needs time to read.",
    "either": "Either answer is acceptable.",
    "neither": "Neither plan is perfect.",
    "some": "Some students are reading.",
    "any": "Do you have any questions?",
    "many": "Many people learn English.",
    "much": "There is much work to do.",
    "few": "Few students were absent.",
    "little": "I have a little time before class.",
    "other": "The other book is on the desk.",
    "another": "May I have another apple?",
    "nobody": "Nobody was late for class.",
    "whom": "Whom did you meet yesterday?",
    "anyone": "Anyone can join the activity.",
    "anybody": "Anybody can ask for help.",
    "everyone": "Everyone is ready for class.",
    "everybody": "Everybody listened carefully.",
    "someone": "Someone left a book on the desk.",
    "somebody": "Somebody knocked at the door.",
    "none": "None of the answers is correct.",
    "himself": "He finished the work by himself.",
    "herself": "She made the card by herself.",
    "itself": "The machine can stop itself.",
    "yourself": "You should believe in yourself.",
    "ourselves": "We made lunch ourselves.",
    "themselves": "They solved the problem themselves.",
}

NUMBER_EXAMPLES = {
    "zero": "Zero means nothing.",
    "one": "I have one pencil.",
    "two": "Two birds are in the tree.",
    "three": "There are three books on the desk.",
    "four": "Four students are reading.",
    "five": "Five apples are in the basket.",
    "six": "Six children are playing outside.",
    "seven": "Seven days make a week.",
    "eight": "Eight chairs are in the room.",
    "nine": "Nine is my lucky number.",
    "ten": "I can count to ten.",
    "eleven": "Eleven players are on a soccer team.",
    "twelve": "There are twelve months in a year.",
    "thirteen": "Thirteen students joined the club.",
    "fourteen": "The bus leaves at fourteen minutes past eight.",
    "fifteen": "I waited fifteen minutes.",
    "sixteen": "She is sixteen years old.",
    "seventeen": "There are seventeen desks in the room.",
    "eighteen": "He turned eighteen last week.",
    "nineteen": "Nineteen people came to the meeting.",
    "twenty": "Twenty students are in our class.",
    "thirty": "The lesson lasts thirty minutes.",
    "forty": "My father is forty years old.",
    "fifty": "The book has fifty pages.",
    "sixty": "There are sixty seconds in a minute.",
    "seventy": "The museum is seventy years old.",
    "eighty": "The train travels eighty kilometers an hour.",
    "ninety": "Ninety students watched the match.",
    "hundred": "A hundred people visited the school.",
    "thousand": "Thousands of stars shone in the sky.",
    "million": "The city has over a million people.",
    "first": "This is my first English lesson.",
    "second": "The second question is easy.",
    "third": "She finished third in the race.",
    "fourth": "The fourth floor is quiet.",
    "fifth": "May is the fifth month of the year.",
    "eighth": "August is the eighth month of the year.",
    "ninth": "The ninth unit is about travel.",
    "twelfth": "December is the twelfth month.",
    "twentieth": "This is the twentieth page.",
    "twenty-first": "Today is the twenty-first day of the month.",
    "twenty-third": "Her birthday is on the twenty-third.",
}

MONTH_EXAMPLES = {
    "january": "January is the first month of the year.",
    "february": "February is usually cold here.",
    "march": "March comes after February.",
    "april": "April is a good month for flowers.",
    "may": "May is my favorite month.",
    "june": "June is the start of summer for many students.",
    "july": "July is often very hot.",
    "august": "August comes before September.",
    "september": "School often starts in September.",
    "october": "October has cool weather.",
    "november": "November comes before December.",
    "december": "December is the last month of the year.",
}

DAY_EXAMPLES = {
    "monday": "Monday is the first school day of the week.",
    "tuesday": "We have English on Tuesday.",
    "wednesday": "Wednesday is in the middle of the week.",
    "thursday": "Thursday comes before Friday.",
    "friday": "Friday is my favorite school day.",
    "saturday": "Saturday is a good day to rest.",
    "sunday": "Sunday is often a family day.",
}

COLOR_EXAMPLES = {
    "red": "The apple is red.",
    "green": "The grass is green.",
    "yellow": "The banana is yellow.",
    "blue": "The sky is blue.",
    "black": "My shoes are black.",
    "white": "The wall is white.",
    "brown": "The desk is brown.",
    "orange": "The orange bag is on the chair.",
    "pink": "She has a pink pencil.",
    "purple": "The flower is purple.",
    "grey": "The sky looks grey today.",
    "gray": "The sky looks gray today.",
}

SUBJECT_EXAMPLES = {
    "english": "We study English every day.",
    "chinese": "Chinese is my first language.",
    "math": "Math helps us solve problems.",
    "maths": "Maths helps us solve problems.",
    "science": "Science helps us understand the world.",
    "music": "Music makes the classroom lively.",
    "art": "Art lets students express their ideas.",
    "history": "History teaches us about the past.",
    "geography": "Geography teaches us about places.",
    "biology": "Biology is the study of living things.",
    "physics": "Physics explains how many things move.",
    "chemistry": "Chemistry is useful in many experiments.",
    "p.e.": "We have P.E. on Friday.",
    "french": "She is learning French at school.",
    "german": "He can speak German very well.",
    "spanish": "Spanish is spoken in many countries.",
    "japanese": "Japanese can be difficult to write.",
    "italian": "Italian sounds beautiful in songs.",
}

COMMON_VERB_EXAMPLES = {
    "accept": "Please accept my sincere thanks.",
    "achieve": "She worked hard to achieve her goal.",
    "add": "Add your name to the list.",
    "admire": "I admire her courage.",
    "advise": "The doctor advised him to rest.",
    "agree": "I agree with your opinion.",
    "allow": "The teacher allowed us to discuss the question.",
    "answer": "Please answer the question clearly.",
    "appear": "Stars appear in the night sky.",
    "arrive": "We arrived at school on time.",
    "ask": "May I ask a question?",
    "avoid": "Try to avoid making the same mistake.",
    "believe": "I believe that practice brings progress.",
    "borrow": "Can I borrow your dictionary?",
    "bring": "Please bring your notebook tomorrow.",
    "build": "They will build a new bridge.",
    "buy": "I want to buy a new pen.",
    "call": "Please call me after school.",
    "carry": "Can you carry this box?",
    "catch": "The boy tried to catch the ball.",
    "celebrate": "We celebrate the festival with our family.",
    "change": "Small habits can change your life.",
    "choose": "Choose the answer carefully.",
    "clean": "We clean the classroom every Friday.",
    "climb": "They climb the hill in spring.",
    "close": "Please close the door quietly.",
    "collect": "She likes to collect stamps.",
    "come": "Come here and look at this picture.",
    "compare": "Compare the two answers carefully.",
    "complete": "Please complete the form.",
    "consider": "We should consider every possible solution.",
    "continue": "The students continue to practice.",
    "control": "You must control your voice in the library.",
    "copy": "Do not copy other students' homework.",
    "create": "Writers create stories with words.",
    "cross": "Cross the street carefully.",
    "cry": "The baby began to cry.",
    "cut": "Cut the paper into small pieces.",
    "dance": "They dance after school.",
    "decide": "We need to decide what to do next.",
    "describe": "Can you describe the picture?",
    "develop": "Reading helps develop your vocabulary.",
    "die": "Plants die without water.",
    "disagree": "I disagree with that idea.",
    "discover": "Scientists discover new facts through research.",
    "discuss": "We discuss the story in groups.",
    "draw": "I like to draw pictures.",
    "drink": "Drink more water on hot days.",
    "drive": "My father can drive a car.",
    "eat": "I eat lunch at school.",
    "encourage": "Teachers encourage students to ask questions.",
    "enjoy": "I enjoy reading English stories.",
    "enter": "Please enter the room quietly.",
    "explain": "Can you explain your answer?",
    "fall": "Leaves fall from the trees in autumn.",
    "feed": "The children feed the chickens.",
    "feel": "I feel happy today.",
    "finish": "Please finish your homework first.",
    "fly": "Birds fly high in the sky.",
    "follow": "Follow the rules in class.",
    "forget": "Do not forget your homework.",
    "give": "Give the book to your sister.",
    "grow": "Children grow quickly.",
    "guess": "Can you guess the meaning?",
    "happen": "Accidents can happen suddenly.",
    "hear": "I can hear music from the room.",
    "help": "Please help me carry the books.",
    "hope": "I hope to see you soon.",
    "imagine": "Imagine a world without books.",
    "improve": "Practice can improve your English.",
    "include": "The price includes breakfast.",
    "increase": "Exercise can increase your energy.",
    "introduce": "Let me introduce my friend.",
    "invite": "I will invite her to my party.",
    "join": "Would you like to join our club?",
    "jump": "The children jump in the playground.",
    "keep": "Keep your room clean.",
    "know": "I know the answer.",
    "laugh": "The funny story made us laugh.",
    "learn": "We learn new words every day.",
    "leave": "We leave school at five.",
    "lend": "Can you lend me your ruler?",
    "listen": "Listen to the teacher carefully.",
    "live": "They live near the school.",
    "like": "I like reading English stories.",
    "look": "Look at the picture.",
    "lose": "Do not lose your keys.",
    "love": "I love my family.",
    "mean": "What does this word mean?",
    "meet": "I will meet my friend after class.",
    "move": "Please move the chair.",
    "need": "We need more time.",
    "notice": "Did you notice the sign?",
    "open": "Open your book, please.",
    "organize": "We will organize a class meeting.",
    "pass": "Please pass me the salt.",
    "pay": "You can pay by card.",
    "plan": "We plan to visit the museum.",
    "play": "Children play games after school.",
    "prefer": "I prefer tea to coffee.",
    "prepare": "We prepare for the test carefully.",
    "produce": "The factory produces cars.",
    "protect": "We should protect the environment.",
    "provide": "The school provides lunch for students.",
    "pull": "Pull the door to open it.",
    "push": "Do not push in the hallway.",
    "put": "Put your book on the desk.",
    "read": "I read English every morning.",
    "realize": "She realized her mistake.",
    "receive": "I received a letter yesterday.",
    "remember": "Remember to bring your notebook.",
    "reply": "Please reply to my email.",
    "report": "The student reported the news to the teacher.",
    "return": "Please return the book tomorrow.",
    "ride": "I ride a bike to school.",
    "rise": "The sun rises in the east.",
    "run": "They run in the playground.",
    "save": "We should save water.",
    "say": "Can you say it again?",
    "see": "I can see a bird in the tree.",
    "sell": "The shop sells fresh fruit.",
    "send": "Please send me a message.",
    "share": "Friends share ideas with each other.",
    "show": "Show me your new picture.",
    "sing": "We sing songs in music class.",
    "sit": "Please sit down.",
    "sleep": "I sleep for eight hours every night.",
    "speak": "Please speak more slowly.",
    "spell": "Can you spell your name?",
    "spend": "I spend an hour reading every day.",
    "stand": "Stand up, please.",
    "start": "The class starts at eight.",
    "stay": "Stay at home if you are sick.",
    "stop": "Stop talking and listen.",
    "study": "We study English at school.",
    "support": "My parents support my choice.",
    "swim": "I swim in summer.",
    "take": "Take your umbrella with you.",
    "talk": "We talk about books after class.",
    "teach": "My mother teaches English.",
    "tell": "Please tell me the truth.",
    "think": "Think before you answer.",
    "travel": "They travel by train.",
    "try": "Try again, and you will improve.",
    "turn": "Turn left at the corner.",
    "understand": "I understand the story.",
    "use": "Use a dictionary when you need help.",
    "visit": "We visit our grandparents on Sunday.",
    "wait": "Please wait for me.",
    "walk": "I walk to school every day.",
    "want": "I want a glass of water.",
    "watch": "We watch a movie on Friday.",
    "wear": "Wear a coat on cold days.",
    "win": "Our team hopes to win the game.",
    "work": "They work hard every day.",
    "write": "Write your name on the paper.",
    "dislike": "I dislike wasting time.",
    "hate": "I hate being late.",
    "calm": "Music can calm people after a busy day.",
    "concern": "The report concerns the safety of children.",
    "ignore": "Do not ignore small mistakes.",
    "survey": "We surveyed students about their reading habits.",
    "amaze": "The magic show can amaze children.",
    "select": "Please select the best answer.",
    "remove": "Remove your shoes before entering.",
    "belong": "This book belongs on the top shelf.",
    "decorate": "We decorate the room for the festival.",
    "repeat": "Please repeat the sentence after me.",
    "note": "Please note the date of the meeting.",
    "connect": "The bridge connects the two villages.",
    "pronounce": "Can you pronounce this word?",
    "request": "You can request more information.",
    "guard": "Soldiers guard the gate at night.",
    "require": "This job requires patience.",
    "fail": "Do not give up if you fail once.",
    "paint": "She likes to paint flowers.",
    "mention": "Please mention the source in your report.",
    "advertise": "The company advertises its new product online.",
    "bargain": "They bargained over the price.",
    "arise": "New problems may arise during the project.",
    "respond": "Please respond to the question.",
    "contain": "This box contains old letters.",
    "bite": "Mosquitoes can bite people at night.",
    "roll": "The ball rolled across the floor.",
    "form": "Clouds form before a storm.",
    "undertake": "The team will undertake the research.",
    "owe": "I owe my success to my teachers.",
    "betray": "He would never betray his friends.",
    "beware": "Beware of the wet floor.",
    "absorb": "Plants absorb water from the soil.",
    "bleed": "The cut began to bleed.",
}

PLACE_EXAMPLES = {
    "school": "Our school is clean and bright.",
    "classroom": "Our classroom is on the second floor.",
    "room": "My room is small but tidy.",
    "library": "We read books in the library.",
    "office": "The office is next to the classroom.",
    "zoo": "We saw many animals at the zoo.",
    "park": "Children play in the park.",
    "farm": "We picked apples on the farm.",
    "hospital": "The hospital is near the station.",
    "restaurant": "The restaurant serves fresh noodles.",
    "bank": "The bank is across from the school.",
    "museum": "The museum has many old pictures.",
    "station": "The station is very busy in the morning.",
    "airport": "The airport is far from the city.",
    "cinema": "We watched a film at the cinema.",
    "theater": "The theater was full of people.",
    "theatre": "The theatre was full of people.",
    "garden": "There are flowers in the garden.",
    "kitchen": "My mother is cooking in the kitchen.",
    "bathroom": "The bathroom is clean.",
    "bedroom": "My bedroom has a big window.",
}

AMBIGUOUS_VERB_TERMS = {
    "watch",
    "report",
    "work",
}

ADJECTIVE_EXAMPLES = {
    "big": "The elephant is big.",
    "small": "The box is small.",
    "long": "The river is long.",
    "short": "The pencil is short.",
    "tall": "My brother is tall.",
    "young": "The young child is smiling.",
    "old": "The old house is near the river.",
    "new": "I have a new notebook.",
    "good": "This is a good idea.",
    "bad": "Smoking is a bad habit.",
    "great": "We had a great time.",
    "nice": "She is a nice friend.",
    "fine": "I feel fine today.",
    "funny": "The story is funny.",
    "happy": "The children are happy.",
    "sad": "She felt sad after the movie.",
    "angry": "He was angry about the mistake.",
    "hungry": "I am hungry after class.",
    "thirsty": "The runner is thirsty.",
    "cold": "The water is cold.",
    "hot": "The soup is hot.",
    "warm": "The room is warm.",
    "cool": "The evening air is cool.",
    "clean": "The classroom is clean.",
    "dirty": "Your shoes are dirty.",
    "easy": "This question is easy.",
    "difficult": "The problem is difficult.",
    "hard": "The test was hard.",
    "important": "Sleep is important for health.",
    "different": "The two pictures are different.",
    "same": "We are in the same class.",
    "right": "Your answer is right.",
    "wrong": "This answer is wrong.",
    "true": "The story is true.",
    "real": "This is a real problem.",
    "possible": "A better result is possible.",
    "impossible": "It is impossible to finish without help.",
    "necessary": "Regular practice is necessary.",
    "common": "This is a common mistake.",
    "special": "Today is a special day.",
    "useful": "A dictionary is useful.",
    "careful": "Be careful with the glass.",
    "beautiful": "The garden is beautiful.",
    "popular": "The song is popular with students.",
    "famous": "The city is famous for its history.",
    "healthy": "Fruit is healthy food.",
    "ill": "She felt ill yesterday.",
    "sick": "The sick child stayed at home.",
    "busy": "The street is busy in the morning.",
    "free": "I am free this afternoon.",
    "full": "The bottle is full of water.",
    "empty": "The box is empty.",
    "open": "The door is open.",
    "closed": "The shop is closed today.",
    "fast": "The train is fast.",
    "slow": "The old bus is slow.",
    "strong": "The bridge is strong.",
    "weak": "The old chair is weak.",
    "heavy": "This bag is heavy.",
    "light": "The box is light.",
    "high": "The mountain is high.",
    "low": "The wall is low.",
    "wide": "The road is wide.",
    "deep": "The river is deep.",
    "bright": "The classroom is bright.",
    "dark": "The room is dark.",
    "quiet": "The library is quiet.",
    "loud": "The music is loud.",
    "rich": "The country is rich in resources.",
    "poor": "The poor family needed help.",
    "thin": "The boy is thin but healthy.",
    "thinner": "My ruler is thinner than yours.",
    "fat": "The cat is fat and lazy.",
    "fatter": "The cat is fatter than before.",
    "taller": "My brother is taller than me.",
    "shorter": "This pencil is shorter than that one.",
    "longer": "This river is longer than that one.",
    "bigger": "This box is bigger than that one.",
    "smaller": "This room is smaller than ours.",
    "older": "My sister is older than me.",
    "younger": "My brother is younger than me.",
    "heavier": "This bag is heavier than that one.",
    "stronger": "The new bridge is stronger.",
    "loose": "The button on my coat is loose.",
    "upset": "She felt upset about the bad news.",
    "jewish": "The Jewish family kept its traditions.",
    "american": "She has an American friend.",
    "canadian": "My Canadian teacher is friendly.",
    "indian": "Indian food is popular here.",
    "western": "Western music influenced the band.",
    "eastern": "The eastern part of the city is quiet.",
    "northern": "The northern wind is cold.",
    "southern": "The southern coast is warm.",
    "midwestern": "The midwestern town is small and quiet.",
    "african": "African music has rich rhythms.",
    "asian": "Asian cultures are diverse.",
}

NOUN_EXAMPLES = {
    "boy": "The boy is playing with a ball.",
    "girl": "The girl is reading a story.",
    "child": "The child is drawing a picture.",
    "children": "Children like to play games.",
    "student": "The student listens carefully in class.",
    "pupil": "The pupil reads the word aloud.",
    "teacher": "The teacher writes a sentence on the board.",
    "friend": "My friend helps me with English.",
    "man": "The man is waiting for the bus.",
    "woman": "The woman is talking to her daughter.",
    "family": "My family has dinner together.",
    "tail": "The dog has a long tail.",
    "chair": "The chair is beside the desk.",
    "desk": "My desk is clean.",
    "cap": "He wears a red cap.",
    "ball": "The ball is under the chair.",
    "car": "The car is new.",
    "boat": "The boat is on the lake.",
    "map": "The map is on the wall.",
    "toy": "The toy is in the box.",
    "box": "The box is under the table.",
    "fruit": "Fruit is good for your health.",
    "kite": "The kite is flying high.",
    "vet": "The vet helped the injured dog.",
    "survey": "The survey asked students about their habits.",
    "concern": "Safety is a major concern for parents.",
    "nazi": "The Nazi regime caused great suffering.",
    "metre": "The tree is five metres tall.",
    "meter": "The tree is five meters tall.",
    "watch": "My watch is on the desk.",
    "helmet": "Wear a helmet when you ride a bike.",
    "glasses": "My glasses are on the table.",
    "scarf": "She wears a warm scarf in winter.",
    "glove": "I lost one glove on the bus.",
    "handbag": "Her handbag is black.",
    "backpack": "My backpack is heavy today.",
    "suitcase": "My suitcase is ready for the trip.",
    "laptop": "The laptop is on the desk.",
    "restroom": "The restroom is near the entrance.",
    "washroom": "The washroom is at the end of the hall.",
    "mall": "The mall is crowded on weekends.",
    "background": "The background of the story is important.",
    "earring": "She wore a small earring.",
    "handkerchief": "He put a handkerchief in his pocket.",
    "vest": "He wore a vest under his coat.",
    "wharf": "The boat stopped at the wharf.",
    "nucleus": "The nucleus is at the center of the atom.",
    "embryo": "The embryo develops quickly.",
    "medium": "Television is a powerful medium.",
    "claw": "The bird has a sharp claw.",
    "vein": "A vein carries blood back to the heart.",
    "arrowhead": "The arrowhead was made of stone.",
    "faith": "Faith gave her courage.",
    "resolve": "His resolve helped him continue.",
    "anxiety": "Deep breathing can reduce anxiety.",
    "handle": "The handle of the door is broken.",
    "belt": "He wears a black belt.",
    "pedal": "Press the pedal gently.",
    "assistant": "The assistant answered the phone.",
    "skin": "Protect your skin from the sun.",
    "snowman": "The children made a snowman.",
    "athlete": "The athlete trained every morning.",
    "android": "The android can answer simple questions.",
    "people": "People need clean water.",
    "police": "The police arrived quickly.",
    "person": "Every person has a story.",
    "classmate": "My classmate helped me study.",
    "businessman": "The businessman opened a new shop.",
    "adult": "An adult should guide the children.",
    "craftsman": "The craftsman made a beautiful chair.",
    "nurse": "The nurse cared for the patient.",
    "madam": "The madam spoke politely to the waiter.",
    "couple": "The couple walked through the park.",
    "pal": "My pal sent me a message.",
    "partner": "My partner helped me finish the project.",
    "saint": "The saint is remembered for kindness.",
    "policeman": "The policeman helped the lost child.",
    "alien": "The story is about an alien from space.",
    "enemy": "The enemy retreated at night.",
    "coach": "The coach encouraged the players.",
    "president": "The president gave a speech.",
    "applicant": "The applicant waited for the interview.",
    "personnel": "The personnel office is on the first floor.",
    "duchess": "The duchess attended the ceremony.",
    "candidate": "The candidate answered every question.",
    "physician": "The physician checked the patient carefully.",
    "host": "The host welcomed the guests.",
    "hostess": "The hostess served tea.",
    "guest": "The guest arrived early.",
    "servant": "The servant opened the door.",
    "agent": "The agent arranged the meeting.",
    "expert": "The expert gave useful advice.",
    "team": "The team worked together.",
    "crowd": "The crowd waited outside the stadium.",
    "robot": "The robot cleaned the floor.",
}

BODY_EXAMPLES = {
    "face": "Wash your face every morning.",
    "ear": "My ear can hear the music.",
    "eye": "The eye is very important.",
    "nose": "My nose is a little red.",
    "mouth": "Open your mouth, please.",
    "arm": "He raised his arm.",
    "hand": "Raise your hand before you speak.",
    "head": "Wear a hat on your head.",
    "body": "Exercise keeps your body healthy.",
    "leg": "My leg hurts after running.",
    "foot": "My foot is in the shoe.",
    "hair": "Her hair is long.",
    "tooth": "Brush each tooth carefully.",
    "teeth": "Brush your teeth twice a day.",
    "neck": "She wore a scarf around her neck.",
    "stomach": "My stomach hurts after eating too much.",
    "throat": "My throat feels dry.",
    "finger": "She cut her finger.",
    "knee": "He hurt his knee in the game.",
    "elbow": "Bend your elbow slowly.",
    "skin": "Protect your skin from the sun.",
    "blood": "Blood carries oxygen through the body.",
    "heart": "The heart beats all day.",
    "brain": "The brain controls the body.",
    "forehead": "His forehead felt hot.",
    "eyebrow": "She raised one eyebrow.",
    "cheekbone": "The cheekbone is part of the face.",
    "waist": "The belt goes around your waist.",
    "stomachache": "I have a stomachache today.",
    "toothache": "A toothache can be painful.",
    "headache": "A headache made it hard to study.",
    "nosebleed": "He had a nosebleed after the game.",
}

COUNTRY_EXAMPLES = {
    "uk": "The UK is in Europe.",
    "usa": "The USA is a large country.",
    "canada": "Canada is a large country.",
    "china": "China has a long history.",
    "england": "England is part of the UK.",
    "france": "France is famous for art and food.",
    "germany": "Germany is in Europe.",
    "spain": "Spain is in southern Europe.",
    "italy": "Italy is famous for its old cities.",
    "india": "India has a large population.",
    "japan": "Japan is an island country.",
    "australia": "Australia is both a country and a continent.",
    "singapore": "Singapore is a modern city-state.",
    "malaysia": "Malaysia is in Southeast Asia.",
    "mexico": "Mexico is south of the USA.",
    "greece": "Greece is famous for ancient history.",
    "egypt": "Egypt is known for the pyramids.",
    "netherlands": "The Netherlands is famous for windmills.",
    "new zealand": "New Zealand has beautiful mountains.",
}

SPECIAL_EXAMPLES = {
    **FUNCTION_WORD_EXAMPLES,
    **NUMBER_EXAMPLES,
    **MONTH_EXAMPLES,
    **DAY_EXAMPLES,
    **SUBJECT_EXAMPLES,
    **PLACE_EXAMPLES,
    **NOUN_EXAMPLES,
    **BODY_EXAMPLES,
    **COUNTRY_EXAMPLES,
    "good morning!": "Good morning! Nice to see you.",
    "good afternoon!": "Good afternoon! Welcome to our class.",
    "good evening!": "Good evening! Please come in.",
    "how are you?": "How are you? I am fine, thanks.",
    "nice to meet you!": "Nice to meet you! My name is Li Hua.",
    "see you!": "See you! Have a good day.",
    "happy birthday!": "Happy birthday! This gift is for you.",
    "have a good day!": "Have a good day! See you tomorrow.",
    "have a good time!": "Have a good time! Take some photos.",
    "you're welcome.": "You're welcome. I am glad to help.",
    "here you are.": "Here you are. This is your book.",
    "can i help you?": "Can I help you? I need a pair of shoes.",
    "what’s the matter?": "What’s the matter? You look tired.",
    "what's the matter?": "What's the matter? You look tired.",
    "what's wrong?": "What's wrong? You look worried.",
    "excuse me": "Excuse me, where is the library?",
    "thank you": "Thank you for your help.",
    "thanks": "Thanks for helping me.",
    "please": "Please open your book.",
    "hello": "Hello, my name is Amy.",
    "hi": "Hi, nice to meet you.",
    "bye": "Bye, see you tomorrow.",
    "goodbye": "Goodbye, and have a nice day.",
    "welcome": "Welcome to our school.",
    "sorry": "I am sorry for being late.",
    "wow": "Wow, that picture is beautiful.",
    "oh": "Oh, I see the problem now.",
    "dear": "Dear friend, thank you for your letter.",
    "rsvp": "Please RSVP before Friday.",
    "today": "Today is a sunny day.",
    "tomorrow": "Tomorrow we will visit the museum.",
    "yesterday": "Yesterday I finished my homework.",
    "tonight": "Tonight we will have dinner together.",
    "a.m.": "I get up at 7 a.m.",
    "p.m.": "The meeting starts at 3 p.m.",
    "mr.": "Mr. Smith teaches English.",
    "mrs.": "Mrs. Green is our music teacher.",
    "ms.": "Ms. Brown works in the office.",
    "mr": "Mr. Smith teaches English.",
    "mrs": "Mrs. Green is our music teacher.",
    "ms": "Ms. Brown works in the office.",
    "miss": "Miss White teaches English.",
    "dr": "Dr. Brown works at the hospital.",
    "doctor": "The doctor checked my throat.",
    "p.e.": "We have P.E. on Friday.",
    "tv": "I watch TV after dinner.",
    "pc": "A PC can help students write reports.",
    "pda": "A PDA was useful before smartphones became common.",
    "gps": "GPS helps us find the way.",
    "id card": "Please show your ID card at the gate.",
    "x-ray": "The doctor took an X-ray of my arm.",
    "email": "I sent an email to my teacher.",
    "e-mail": "I sent an e-mail to my teacher.",
    "internet": "The Internet helps us find information quickly.",
    "www": "Many website addresses begin with www.",
    "wwf": "WWF works to protect wild animals.",
    "bc": "The temple was built in 200 BC.",
    "ad": "The story happened in AD 79.",
}

SPECIAL_EXTRA_SENTENCES = {
    "mr": [
        "Mr. Smith is our teacher.",
        "Please ask Mr. Smith for help.",
    ],
    "mr.": [
        "Mr. Smith is our teacher.",
        "Please ask Mr. Smith for help.",
    ],
    "mrs": [
        "Mrs. Green is kind to her students.",
        "I gave the book to Mrs. Green.",
    ],
    "mrs.": [
        "Mrs. Green is kind to her students.",
        "I gave the book to Mrs. Green.",
    ],
    "ms": [
        "Ms. Brown works in the school office.",
        "Please give this form to Ms. Brown.",
    ],
    "ms.": [
        "Ms. Brown works in the school office.",
        "Please give this form to Ms. Brown.",
    ],
    "miss": [
        "Miss White teaches us English.",
        "I asked Miss White a question.",
    ],
    "dr": [
        "Dr. Brown checked the patient carefully.",
        "You should call Dr. Brown tomorrow.",
    ],
    "doctor": [
        "The doctor checked the patient carefully.",
        "You should see a doctor if you feel sick.",
    ],
}

EXACT_SENTENCE_TRANSLATIONS = {
    "Tom and Mary are classmates.": "汤姆和玛丽是同学。",
    "OK, let's start now.": "好的，我们现在开始吧。",
    "No, I do not need help.": "不，我不需要帮助。",
    "Your answer is clear.": "你的回答很清楚。",
    "The apple is red.": "这个苹果是红色的。",
    "The grass is green.": "草是绿色的。",
    "The banana is yellow.": "香蕉是黄色的。",
    "The sky is blue.": "天空是蓝色的。",
    "My shoes are black.": "我的鞋是黑色的。",
    "The desk is brown.": "这张书桌是棕色的。",
    "The wall is white.": "墙是白色的。",
    "The orange bag is on the chair.": "橙色的包在椅子上。",
    "The story is funny.": "这个故事很好笑。",
    "I have one pencil.": "我有一支铅笔。",
    "Two birds are in the tree.": "树上有两只鸟。",
    "There are three books on the desk.": "桌上有三本书。",
    "Four students are reading.": "四名学生正在读书。",
    "Five apples are in the basket.": "篮子里有五个苹果。",
    "Six children are playing outside.": "六个孩子正在外面玩。",
    "Seven days make a week.": "七天组成一个星期。",
    "Eight chairs are in the room.": "房间里有八把椅子。",
    "Nine is my lucky number.": "九是我的幸运数字。",
    "I can count to ten.": "我能数到十。",
    "Wash your face every morning.": "每天早上洗脸。",
    "My ear can hear the music.": "我的耳朵能听到音乐。",
    "The eye is very important.": "眼睛非常重要。",
    "My nose is a little red.": "我的鼻子有点红。",
    "Open your mouth, please.": "请张开嘴。",
    "He raised his arm.": "他举起了胳膊。",
    "Raise your hand before you speak.": "发言前请举手。",
    "Wear a hat on your head.": "把帽子戴在头上。",
    "Exercise keeps your body healthy.": "锻炼让你的身体保持健康。",
    "My leg hurts after running.": "跑步后我的腿疼。",
    "My foot is in the shoe.": "我的脚在鞋里。",
    "Our school is clean and bright.": "我们的学校干净又明亮。",
    "We saw many animals at the zoo.": "我们在动物园看到了许多动物。",
    "I like bread for lunch.": "我午餐喜欢吃面包。",
    "I like juice for lunch.": "我午餐喜欢喝果汁。",
    "I like milk for lunch.": "我午餐喜欢喝牛奶。",
    "I like water for lunch.": "我午餐喜欢喝水。",
    "I like rice for lunch.": "我午餐喜欢吃米饭。",
    "I ate an egg for lunch.": "我午餐吃了一个鸡蛋。",
    "I ate a cake for lunch.": "我午餐吃了一块蛋糕。",
    "I ate a fish for lunch.": "我午餐吃了一条鱼。",
    "The ruler is on the desk.": "尺子在书桌上。",
    "The pencil is on the desk.": "铅笔在书桌上。",
    "The eraser is on the desk.": "橡皮在书桌上。",
    "The crayon is on the desk.": "蜡笔在书桌上。",
    "The pen is on the desk.": "钢笔在书桌上。",
    "The book is on the desk.": "书在书桌上。",
}

ANIMAL_HINTS = (
    "猫",
    "狗",
    "鸟",
    "鸭",
    "猪",
    "熊",
    "象",
    "猴",
    "虎",
    "熊猫",
    "兔",
    "马",
    "牛",
    "羊",
    "鱼",
    "鸡",
    "狮",
    "鲸",
    "鲨",
    "鹿",
    "蛇",
    "狼",
    "狐狸",
    "昆虫",
    "蚂蚁",
    "蜜蜂",
    "蝴蝶",
    "恐龙",
)

FOOD_HINTS = (
    "食物",
    "食品",
    "饭",
    "面包",
    "蛋",
    "牛奶",
    "水",
    "茶",
    "咖啡",
    "果汁",
    "蛋糕",
    "鱼",
    "肉",
    "鸡肉",
    "牛肉",
    "猪肉",
    "米",
    "蔬菜",
    "水果",
    "苹果",
    "香蕉",
    "橙",
    "梨",
    "草莓",
    "葡萄",
    "土豆",
    "番茄",
    "西红柿",
    "胡萝卜",
    "洋葱",
    "面条",
    "饺子",
    "汤",
    "糖",
    "盐",
    "奶油",
    "酸奶",
    "瓜",
    "小吃",
    "点心",
    "快餐",
)

BODY_HINTS = (
    "脸",
    "耳",
    "眼",
    "鼻",
    "嘴",
    "胳膊",
    "手",
    "头",
    "身体",
    "腿",
    "脚",
    "牙",
    "脖子",
    "背部",
    "胃",
    "心脏",
    "血",
    "腰",
    "额头",
    "眉",
    "骨",
    "手指",
    "皮肤",
)

FAMILY_HINTS = (
    "母亲",
    "父亲",
    "妈妈",
    "爸爸",
    "兄",
    "弟",
    "姐",
    "妹",
    "祖母",
    "祖父",
    "奶奶",
    "爷爷",
    "外婆",
    "外公",
    "女儿",
    "儿子",
    "叔",
    "舅",
    "姨",
    "姑",
    "家庭",
    "亲戚",
)

SCHOOL_HINTS = (
    "学校",
    "教室",
    "教师",
    "老师",
    "学生",
    "课程",
    "课",
    "英语",
    "数学",
    "语文",
    "科学",
    "音乐",
    "美术",
    "体育",
    "考试",
    "作业",
    "书",
    "铅笔",
    "钢笔",
    "橡皮",
    "尺",
    "字典",
    "笔记本",
    "图书馆",
)

PLACE_HINTS = (
    "房间",
    "教室",
    "学校",
    "办公室",
    "图书馆",
    "公园",
    "商店",
    "市场",
    "城市",
    "国家",
    "首都",
    "村庄",
    "街",
    "路",
    "车站",
    "机场",
    "博物馆",
    "饭店",
    "餐馆",
    "医院",
    "银行",
    "山",
    "河",
    "湖",
    "海",
    "岛",
    "谷",
    "沙漠",
    "森林",
)

PERSON_HINTS = (
    "人",
    "男人",
    "女人",
    "男孩",
    "女孩",
    "朋友",
    "同学",
    "老师",
    "学生",
    "作家",
    "发明家",
    "科学家",
    "医生",
    "护士",
    "司机",
    "警察",
    "农民",
    "工人",
    "教授",
    "总统",
    "部长",
    "裁判",
    "大使",
)

TIME_HINTS = (
    "时间",
    "早晨",
    "上午",
    "下午",
    "晚上",
    "中午",
    "夜",
    "今天",
    "明天",
    "昨天",
    "星期",
    "月",
    "年",
    "季节",
    "春",
    "夏",
    "秋",
    "冬",
    "生日",
    "假期",
    "节日",
)

ABSTRACT_HINTS = (
    "能力",
    "力量",
    "权力",
    "经验",
    "知识",
    "信息",
    "建议",
    "问题",
    "原因",
    "结果",
    "影响",
    "机会",
    "目的",
    "意义",
    "价值",
    "态度",
    "观点",
    "想法",
    "计划",
    "方法",
    "习惯",
    "规则",
    "责任",
    "勇气",
    "信心",
    "和平",
    "自由",
    "文化",
    "教育",
    "历史",
    "科学",
    "艺术",
    "语言",
    "语法",
    "发音",
)

VERB_HINTS = (
    "做",
    "使",
    "让",
    "去",
    "来",
    "看",
    "听",
    "说",
    "讲",
    "读",
    "写",
    "拼",
    "学习",
    "工作",
    "帮助",
    "喜欢",
    "爱",
    "买",
    "卖",
    "吃",
    "喝",
    "打开",
    "关闭",
    "开始",
    "停止",
    "完成",
    "发现",
    "找到",
    "认为",
    "知道",
    "理解",
    "记",
    "忘",
    "改变",
    "决定",
    "选择",
    "需要",
    "希望",
    "想",
    "计划",
    "组织",
    "保护",
    "提供",
    "创造",
    "建立",
    "发展",
    "解释",
    "描述",
    "讨论",
    "接受",
    "拒绝",
    "避免",
    "允许",
    "鼓励",
    "建议",
    "要求",
    "比较",
    "包括",
    "增加",
    "减少",
    "支持",
    "反对",
    "解决",
    "证明",
    "表明",
    "影响",
    "导致",
    "保持",
    "继续",
    "离开",
    "到达",
    "返回",
    "旅行",
    "移动",
    "穿",
    "戴",
    "洗",
    "清理",
    "打扫",
    "画",
    "唱",
    "跳",
    "跑",
    "游泳",
    "骑",
    "飞",
    "建造",
    "发明",
)

ADJECTIVE_HINTS = (
    "的",
    "令人",
    "可",
    "不能",
    "能够",
    "充满",
)


PHRASE_EXAMPLES = {
    "eat breakfast": "I eat breakfast at seven every morning.",
    "eat dinner": "We eat dinner together at home.",
    "have class": "We have class at eight o'clock.",
    "have...class": "We have English class on Monday.",
    "having...class": "We are having English class now.",
    "play sports": "Many students play sports after school.",
    "do morning exercise": "I do morning exercise before breakfast.",
    "doing morning exercises": "Doing morning exercises keeps us healthy.",
    "clean my room": "I clean my room every Saturday.",
    "go for a walk": "We go for a walk after dinner.",
    "go shopping": "My mother and I go shopping on Sunday.",
    "take a dancing class": "She wants to take a dancing class this term.",
    "go swimming": "We go swimming in summer.",
    "go on a picnic": "We will go on a picnic this weekend.",
    "pick apples": "The children pick apples on the farm.",
    "make a snowman": "Let's make a snowman after the snow stops.",
    "good job": "You did a good job on your homework.",
    "a few": "I have a few questions to ask.",
    "sports meet": "Our school sports meet is in May.",
    "the great wall": "The Great Wall is famous around the world.",
    "national day": "National Day is an important holiday.",
    "look for": "I am looking for my pencil.",
    "each other": "Good friends help each other.",
    "keep to the right": "Please keep to the right in the hallway.",
    "keep your desk clean": "Keep your desk clean after class.",
    "talk quietly": "Please talk quietly in the library.",
    "take turns": "We take turns reading the dialogue.",
    "have a look": "May I have a look at your picture?",
    "hard-working": "She is a hard-working student.",
    "wash my clothes": "I wash my clothes on Saturday.",
    "watch tv": "I watch TV after dinner.",
    "do homework": "I do homework after school.",
    "read books": "We read books in the library.",
    "play football": "They play football on the playground.",
    "ice cream": "I like ice cream in summer.",
    "sing english songs": "We sing English songs in class.",
    "play the pipa": "She can play the pipa very well.",
    "kung fu": "He practices kung fu every week.",
    "do kung fu": "They do kung fu after school.",
    "draw cartoons": "I like to draw cartoons in my notebook.",
    "play basketball": "My brother likes to play basketball.",
    "ping-pong": "Ping-pong is popular in our school.",
    "play ping-pong": "We play ping-pong after lunch.",
    "speak english": "I try to speak English every day.",
    "no problem": "No problem, I can help you.",
    "water bottle": "My water bottle is on the desk.",
    "in front of": "There is a tree in front of our house.",
    "lots of": "There are lots of books in the library.",
    "living room": "My family watches TV in the living room.",
    "help yourself": "Help yourself to some fruit.",
    "baby brother": "My baby brother is sleeping.",
    "football player": "The football player runs very fast.",
    "first floor": "Our classroom is on the first floor.",
    "second floor": "The music room is on the second floor.",
    "teacher's office": "The teacher's office is next to our classroom.",
    "computer room": "We learn typing in the computer room.",
    "art room": "The art room is bright and clean.",
    "music room": "We sing songs in the music room.",
    "next to": "My desk is next to the window.",
    "english class": "We read a story in English class.",
    "music class": "We learn a new song in music class.",
    "pe class": "We run and jump in PE class.",
    "get up": "I get up at seven o'clock.",
    "go to school": "I go to school by bus.",
    "go home": "We go home after school.",
    "go to bed": "I go to bed at nine.",
    "hurry up": "Hurry up, or we will be late.",
    "come on": "Come on, you can do it.",
    "just a minute": "Just a minute, please.",
    "be careful": "Be careful when you cross the street.",
    "new york": "New York is a busy city.",
    "how about": "How about going to the park?",
    "how about...": "How about going to the park?",
    "green beans": "Green beans are good for lunch.",
    "try on": "Can I try on this coat?",
    "of course": "Of course, you can join us.",
    "how much": "How much is this sweater?",
    "in english": "Please say this word in English.",
    "telephone number": "Please write your telephone number here.",
    "phone number": "My phone number is on the card.",
    "first name": "My first name is Jack.",
    "last name": "Her last name is Green.",
    "middle school": "My sister studies in a middle school.",
    "pencil box": "My pencil box is in my schoolbag.",
    "thank you for": "Thank you for your help.",
    "thank you for...": "Thank you for helping me.",
    "what about": "What about playing soccer after school?",
    "what about...?": "What about playing soccer after school?",
    "ask for": "You can ask for help when you need it.",
    "ask... for...": "You can ask the teacher for help.",
    "a set of": "I bought a set of keys.",
    "tape player": "The tape player is on the desk.",
    "model plane": "He made a model plane for science class.",
    "soccer ball": "The soccer ball is under the chair.",
    "think about": "Please think about the question.",
    "a pair of": "I need a pair of shoes.",
    "how old": "How old is your brother?",
    "how old...?": "How old is your brother?",
    "for sure": "I know the answer for sure.",
    "from to": "The store is open from nine to five.",
    "from... to...": "The store is open from nine to five.",
    "be good at": "She is good at math.",
    "be good at…": "She is good at math.",
    "talk to": "I need to talk to my teacher.",
    "talk to …": "I need to talk to my teacher.",
    "play the drums": "He can play the drums.",
    "play the piano": "She can play the piano beautifully.",
    "play the violin": "Tom wants to play the violin.",
    "be good with": "My aunt is good with children.",
    "be good with…": "My aunt is good with children.",
    "make friends": "It is easy to make friends at school.",
    "help with": "Can you help me with English?",
    "help (sb) with sth": "Can you help me with English?",
    "on the weekend": "We visit our grandparents on the weekend.",
    "take a shower": "I take a shower before bed.",
    "radio station": "The radio station plays music every morning.",
    "on weekends": "I play basketball on weekends.",
    "do one's homework": "I do my homework after dinner.",
    "do (one’s) homework": "I do my homework after dinner.",
    "take a walk": "Let's take a walk after lunch.",
    "either or": "Either you or I can answer the question.",
    "either…or ……": "Either you or I can answer the question.",
    "take the subway": "I take the subway to work.",
    "ride a bike": "I ride a bike to school.",
    "every day": "I read English every day.",
    "by bike": "She goes to school by bike.",
    "think of": "What do you think of the movie?",
    "between and": "The bank is between the school and the park.",
    "between… and…": "The bank is between the school and the park.",
    "on time": "Please arrive on time.",
    "(be) on time": "Please be on time for class.",
    "go out": "We cannot go out in the heavy rain.",
    "do the dishes": "I do the dishes after dinner.",
    "make one's bed": "Please make your bed after you get up.",
    "make (one’s) bed": "Please make your bed after you get up.",
    "be strict with": "Our teacher is strict with us.",
    "be strict (with sb)": "Our teacher is strict with us.",
    "follow the rules": "Students should follow the rules.",
    "kind of": "This movie is kind of funny.",
    "south africa": "South Africa has many beautiful places.",
    "get lost": "It is easy to get lost in a new city.",
    "be in danger": "Some animals are in danger.",
    "be in (great) danger": "Some animals are in great danger.",
    "be made of": "This desk is made of wood.",
    "(be) made of": "This desk is made of wood.",
    "read a newspaper": "My grandfather reads a newspaper every morning.",
    "make soup": "My mother can make soup for dinner.",
    "go to movies": "We go to movies on Saturday nights.",
    "eat out": "Sometimes we eat out on weekends.",
    "drink tea": "My parents drink tea after dinner.",
    "the united states": "The United States is a large country.",
    "dragon boat festival": "The Dragon Boat Festival is in summer.",
    "take a message": "Can I take a message for you?",
    "call back": "Please call me back tonight.",
    "call(sb)back": "Please call me back tonight.",
    "on vacation": "We are on vacation by the sea.",
    "on(a)vacation": "We are on vacation by the sea.",
    "pay phone": "There is a pay phone near the station.",
    "across from": "The bank is across from the park.",
    "go along": "Go along this street and turn left.",
    "turn right": "Turn right at the second crossing.",
    "turn left": "Turn left at the bookstore.",
    "turn right/left": "Turn right or left at the corner.",
    "spend time": "I spend time reading every evening.",
    "enjoy reading": "Many students enjoy reading stories.",
    "of medium height": "The man is of medium height.",
    "of medium build": "My uncle is of medium build.",
    "a little": "I can speak a little French.",
    "in the end": "In the end, we found the answer.",
    "would like": "I would like a bowl of noodles.",
    "take one's order": "The waiter came to take our order.",
    "one large bowl of": "I want one large bowl of noodles.",
    "one(large)bowl of": "I want one large bowl of noodles.",
    "around the world": "People around the world learn English.",
    "blow out": "Make a wish before you blow out the candles.",
    "the uk": "The UK is made up of several parts.",
    "get popular": "This song may get popular soon.",
    "bring good luck to": "People believe red can bring good luck to them.",
    "bring good luck to…": "People believe red can bring good luck to them.",
    "milk a cow": "Farmers milk a cow every morning.",
    "ride a horse": "She learned to ride a horse on the farm.",
    "feed chickens": "The children feed chickens after breakfast.",
    "quite a lot": "We learned quite a lot from the trip.",
    "quite a lot(of…)": "There are quite a lot of books on the shelf.",
    "in the countryside": "My grandparents live in the countryside.",
    "fire station": "The fire station is near our school.",
    "all in all": "All in all, the trip was wonderful.",
    "be interested in": "I am interested in science.",
    "stay up late": "Don't stay up late before an exam.",
    "run away": "The dog tried to run away.",
    "shout at": "Do not shout at your classmates.",
    "shout at…": "Do not shout at your classmates.",
    "fly a kite": "We fly a kite in the park.",
    "put up": "They put up a tent by the lake.",
    "get a surprise": "I got a surprise on my birthday.",
    "shout to": "She shouted to me from across the street.",
    "shout to…": "She shouted to me from across the street.",
    "fall in love with": "She fell in love with music at an early age.",
    "pay attention to": "Please pay attention to the road.",
    "connect with": "Good writers connect ideas with examples.",
    "connect … with": "Good writers connect ideas with examples.",
    "put on": "Put on your coat before you go out.",
    "lay out": "They laid out the food on the table.",
    "from time to time": "I visit my old school from time to time.",
    "deal with": "We must deal with the problem calmly.",
    "be proud of": "I am proud of my team.",
    "boarding school": "He studied at a boarding school.",
    "in person": "The manager met us in person.",
    "take pride in": "We take pride in our school.",
    "no matter": "No matter what happens, keep trying.",
    "even though": "Even though it rained, we went hiking.",
    "by accident": "I found the old photo by accident.",
    "take place": "The meeting will take place tomorrow.",
    "without doubt": "Without doubt, practice is important.",
    "all of a sudden": "All of a sudden, the lights went out.",
    "by mistake": "I took your book by mistake.",
    "divide into": "The teacher divided the class into groups.",
    "divide ... into": "The teacher divided the class into groups.",
    "the olympics": "The Olympics bring athletes together.",
    "look up to": "Many children look up to their parents.",
    "talk back": "Students should not talk back to teachers.",
    "keep away from": "Keep away from the broken glass.",
    "make one's own decision": "Teenagers should learn to make their own decision.",
    "make one’s own decision": "Teenagers should learn to make their own decision.",
    "get in the way of": "Too much screen time can get in the way of study.",
    "not only but also": "She is not only smart but also kind.",
    "not only … but also": "She is not only smart but also kind.",
    "in that case": "In that case, we should leave early.",
    "plenty of": "There is plenty of time before the train leaves.",
    "in total": "There are thirty students in total.",
    "world war ii": "World War II changed many countries.",
    "drop by": "Please drop by my house this afternoon.",
    "get mad": "Don't get mad over a small mistake.",
    "make an effort": "We should make an effort to improve.",
    "go out of one's way": "She went out of her way to help me.",
    "go out of one’s way": "She went out of her way to help me.",
    "make feel at home": "The family made me feel at home.",
    "make ... feel at home": "The family made me feel at home.",
    "the more the more": "The more you practice, the more confident you become.",
    "the more … the more": "The more you practice, the more confident you become.",
    "leave out": "Do not leave out any important details.",
    "prime minister": "The prime minister gave a speech.",
    "neither nor": "Neither Tom nor Jack was late.",
    "neither ... nor": "Neither Tom nor Jack was late.",
    "rather than": "I chose tea rather than coffee.",
    "pull together": "The team must pull together to win.",
    "give a lift": "Can you give me a lift to school?",
    "give ... a lift": "Can you give me a lift to school?",
    "take off": "The plane will take off soon.",
    "make a difference": "Small actions can make a difference.",
    "cut off": "The storm cut off the power.",
    "upside down": "The picture is upside down.",
    "in a row": "Our team won three games in a row.",
    "make a mess": "Please do not make a mess in the kitchen.",
    "keep one's cool": "Try to keep your cool under pressure.",
    "keep one’s cool": "Try to keep your cool under pressure.",
    "senior high school": "She will enter senior high school next year.",
    "senior high (school)": "She will enter senior high school next year.",
    "believe in": "I believe in your ability.",
    "be responsible for": "We are responsible for our choices.",
    "post office": "The post office is next to the bank.",
    "on foot": "I go to school on foot.",
    "slow down": "Slow down when you cross the street.",
    "traffic lights": "Stop when the traffic lights are red.",
    "see a film": "We will see a film this evening.",
    "take a trip": "My family will take a trip next week.",
    "next week": "We will have a test next week.",
    "comic book": "He bought a comic book yesterday.",
    "word book": "I use a word book to review vocabulary.",
    "post card": "She sent me a post card from London.",
    "mid-autumn festival": "The Mid-Autumn Festival is a time for family.",
    "get together": "Our family will get together tonight.",
    "pen pal": "My pen pal lives in Canada.",
    "police officer": "A police officer helped us cross the road.",
    "head teacher": "Our head teacher is very kind.",
    "see a doctor": "You should see a doctor if you feel ill.",
    "take a deep breath": "Take a deep breath before you speak.",
    "count to ten": "Count to ten when you feel angry.",
    "have a cold": "I have a cold, so I need rest.",
    "have a stomachache": "He has a stomachache after lunch.",
    "lie down": "Lie down and rest for a while.",
    "take one's temperature": "The nurse took my temperature.",
    "have a fever": "She has a fever and stays in bed.",
    "take breaks": "You should take breaks while studying.",
    "get off": "We get off the bus at the next stop.",
    "to one's surprise": "To my surprise, I passed the exam.",
    "right away": "Please call me right away.",
    "get into": "He got into the car quickly.",
    "be used to": "I am used to getting up early.",
    "take risks": "Good climbers know when to take risks.",
    "run out of": "We ran out of milk this morning.",
    "run out (of)": "We ran out of milk this morning.",
}

SENIOR_PHRASE_EXAMPLES = {
    "add up": "The numbers add up to 100.",
    "calm down": "She tried to calm down before the interview.",
    "calm( )down": "She tried to calm down before the interview.",
    "calm(…)down": "She tried to calm down before the interview.",
    "have got to": "We have got to finish the report today.",
    "be concerned about": "Parents are concerned about their children's safety.",
    "walk the dog": "He walks the dog every evening.",
    "go through": "Many people go through difficult times with courage.",
    "set down": "Please set down the main ideas in your notebook.",
    "a series of": "The teacher asked a series of questions.",
    "on purpose": "He did not break the cup on purpose.",
    "in order to": "In order to improve, we need regular practice.",
    "at dusk": "We reached the village at dusk.",
    "face to face": "They discussed the problem face to face.",
    "no longer": "The old bridge is no longer safe.",
    "not any longer": "She does not live here any longer.",
    "not…any longer": "She does not live here any longer.",
    "suffer from": "Many people suffer from stress.",
    "get tired of": "Students may get tired of repeated drills.",
    "be tired of": "People are tired of empty promises.",
    "pack up": "We packed up our tents before sunrise.",
    "pack (sth) up": "We packed up our tents before sunrise.",
    "get along with": "She gets along with her classmates.",
    "fall in love": "They fell in love during college.",
    "join in": "Everyone was encouraged to join in the discussion.",
    "because of": "The match was delayed because of the rain.",
    "at present": "At present, the team is testing a new method.",
    "make use of": "We should make use of every chance to learn.",
    "such as": "Languages such as English change over time.",
    "play a part in": "Technology plays a part in modern education.",
    "play a part (in)": "Technology plays a part in modern education.",
    "ever since": "She has loved reading ever since childhood.",
    "be fond of": "He is fond of classical music.",
    "care about": "Good leaders care about people's needs.",
    "change one's mind": "She changed her mind after hearing the evidence.",
    "change one’s mind": "She changed her mind after hearing the evidence.",
    "make up one's mind": "He made up his mind to study medicine.",
    "make up one’s mind": "He made up his mind to study medicine.",
    "give in": "The workers refused to give in.",
    "as usual": "As usual, she arrived ten minutes early.",
    "at midnight": "The city was quiet at midnight.",
    "as if": "He spoke as if he knew the answer.",
    "at an end": "The long discussion was finally at an end.",
    "in ruins": "After the earthquake, many houses lay in ruins.",
    "dig out": "Rescuers worked to dig out the trapped miners.",
    "a great number of": "A great number of students joined the activity.",
    "a (great) number of": "A great number of students joined the activity.",
    "out of work": "Many people were out of work during the crisis.",
    "as a matter of fact": "As a matter of fact, the plan worked well.",
    "in trouble": "Friends should help each other in trouble.",
    "turn to": "You can turn to your teacher for advice.",
    "lose heart": "Do not lose heart after one failure.",
    "come to power": "The leader came to power after the election.",
    "be sentenced to": "The criminal was sentenced to ten years in prison.",
    "in search of": "They went into the forest in search of food.",
    "belong to": "This book belongs to the school library.",
    "in return": "She helped me, and I gave her a book in return.",
    "at war": "The two countries were at war for years.",
    "take apart": "The engineer took apart the machine.",
    "think highly of": "The teacher thinks highly of her work.",
    "take part in": "Students should take part in school activities.",
    "stand for": "UN stands for the United Nations.",
    "in charge": "Who is in charge of the project?",
    "one after another": "The students entered the room one after another.",
    "from on": "From then on, he worked harder.",
    "from…on": "From then on, he worked harder.",
    "as a result": "He trained hard; as a result, he won the race.",
    "so that": "She spoke clearly so that everyone could understand.",
    "so that": "She was so tired that she fell asleep quickly.",
    "so…that…": "She was so tired that she fell asleep quickly.",
    "in a way": "In a way, the mistake helped us learn.",
    "with the help of": "With the help of his friends, he finished the task.",
    "watch over": "The nurse watched over the patient all night.",
    "die out": "Some old customs may die out.",
    "in peace": "People everywhere hope to live in peace.",
    "in danger": "The animal is in danger of disappearing.",
    "in relief": "She smiled in relief after the exam.",
    "burst into laughter": "The children burst into laughter.",
    "protect from": "Sunglasses protect our eyes from bright light.",
    "protect…from": "Sunglasses protect our eyes from bright light.",
    "come into being": "The new organization came into being last year.",
    "according to": "According to the report, prices rose again.",
    "dream of": "Many children dream of becoming astronauts.",
    "to be honest": "To be honest, I need more time.",
    "attach to": "Please attach the file to your email.",
    "attach…to": "Please attach the file to your email.",
    "in cash": "He paid for the bike in cash.",
    "play jokes on": "Do not play jokes on people in trouble.",
    "rely on": "We rely on clean water to live.",
    "be familiar with": "She is familiar with this software.",
    "get familiar with": "It takes time to get familiar with a new city.",
    "or so": "The trip will take an hour or so.",
    "in addition": "In addition, we need more evidence.",
    "sort out": "We need to sort out these documents.",
    "above all": "Above all, safety comes first.",
    "in memory of": "The statue was built in memory of a hero.",
    "play a trick on": "It is unkind to play a trick on a stranger.",
    "look forward to": "I look forward to your reply.",
    "day and night": "The doctors worked day and night.",
    "as though": "He looked as though he had seen a ghost.",
    "have fun with": "Children have fun with simple games.",
    "parking lot": "The parking lot was full.",
    "keep one's word": "A reliable person keeps his word.",
    "keep one’s word": "A reliable person keeps his word.",
    "hold one's breath": "She held her breath under water.",
    "hold one’s breath": "She held her breath under water.",
    "set off": "They set off early in the morning.",
    "remind of": "The photo reminds me of my childhood.",
    "remind…of…": "The photo reminds me of my childhood.",
    "balanced diet": "A balanced diet keeps us healthy.",
    "ought to": "You ought to apologize for the mistake.",
    "lose weight": "He exercises to lose weight.",
    "get away with": "No one should get away with cheating.",
    "tell a lie": "It is wrong to tell a lie.",
    "win back": "The company tried to win back customers.",
    "win…back": "The company tried to win back customers.",
    "earn one's living": "She earns her living as a designer.",
    "earn one’s living": "She earns her living as a designer.",
    "in debt": "The family was deeply in debt.",
    "spy on": "It is wrong to spy on others.",
    "before long": "Before long, the rain stopped.",
    "put on weight": "He put on weight during the holiday.",
    "bring up": "Her grandparents brought her up.",
    "make a bet": "They made a bet on the final score.",
    "go ahead": "Go ahead and ask your question.",
    "stare at": "Do not stare at strangers.",
    "account for": "The teacher asked him to account for his absence.",
    "on the contrary": "The plan was not risky; on the contrary, it was careful.",
    "take a chance": "He decided to take a chance and apply for the job.",
    "in rags": "The old man was dressed in rags.",
    "as for": "As for the cost, we can discuss it later.",
    "solar system": "Earth is part of the solar system.",
    "in time": "The doctor arrived in time.",
    "lay eggs": "Birds lay eggs in nests.",
    "give birth to": "The panda gave birth to a baby.",
    "in one's turn": "Each student spoke in his turn.",
    "in one’s turn": "Each student spoke in his turn.",
    "carbon dioxide": "Plants take in carbon dioxide.",
    "prevent from": "The fence prevents children from entering.",
    "prevent...from": "The fence prevents children from entering.",
    "block out": "The clouds blocked out the sun.",
    "now that": "Now that everyone is here, we can begin.",
    "get the hang of": "She got the hang of the new software quickly.",
    "break out": "A fire broke out in the building.",
    "watch out": "Watch out for the wet floor.",
    "manage to do": "They managed to finish the work on time.",
    "catch sight of": "I caught sight of an old friend.",
    "have a gift for": "She has a gift for languages.",
    "in the distance": "We saw mountains in the distance.",
}

SENIOR_PHRASE_EXAMPLES.update(
    {
        "human being": "Every human being deserves respect.",
        "move off": "The bus moved off slowly.",
        "lead a life": "She leads a quiet life in the village.",
        "lead a…life": "She leads a quiet life in the village.",
        "crowd in": "Memories crowded in as he entered the old house.",
        "look down on": "We should never look down on others.",
        "look down upon": "We should never look down upon others.",
        "refer to": "The word can refer to several ideas.",
        "by chance": "I met her by chance at the station.",
        "come across": "I came across an old letter yesterday.",
        "carry on": "We must carry on despite the difficulty.",
        "thanks to": "Thanks to your advice, I solved the problem.",
        "rid of": "We should rid the room of old boxes.",
        "rid…of": "We should rid the room of old boxes.",
        "be satisfied with": "The coach was satisfied with the result.",
        "would rather": "I would rather stay at home tonight.",
        "lead to": "Careless driving can lead to accidents.",
        "keep free of": "Keep the garden free of weeds.",
        "keep…free of": "Keep the garden free of weeds.",
        "keep free from": "Keep the wound free from dirt.",
        "keep…free from": "Keep the wound free from dirt.",
        "up to now": "Up to now, the project has gone well.",
        "feel content with": "She feels content with her simple life.",
        "be content with": "He is content with what he has.",
        "badly off": "The family was badly off after the flood.",
        "pick out": "Can you pick out the main idea?",
        "star in": "The actor starred in many famous films.",
        "defend against": "The wall defended the city against attack.",
        "be likely to": "Prices are likely to rise again.",
        "in general": "In general, exercise is good for health.",
        "at ease": "The warm welcome made me feel at ease.",
        "lose face": "He was afraid of losing face.",
        "turn one's back to": "Do not turn your back to a person who is speaking.",
        "turn one’s back to": "Do not turn your back to a person who is speaking.",
        "be famous for": "The city is famous for its old buildings.",
        "roller coaster": "The roller coaster moved very fast.",
        "fairy tale": "Children love this fairy tale.",
        "no wonder": "No wonder you are tired after such a long walk.",
        "be modeled after": "The building was modeled after a palace.",
        "in advance": "Please book your ticket in advance.",
        "get close to": "Do not get close to wild animals.",
        "come to life": "The story came to life on stage.",
        "put forward": "She put forward a practical suggestion.",
        "draw a conclusion": "We need more evidence before we draw a conclusion.",
        "expose to": "Do not expose children to danger.",
        "expose…to": "Do not expose children to danger.",
        "link to": "The report links stress to poor sleep.",
        "link…to": "The report links stress to poor sleep.",
        "apart from": "Apart from English, she studies French.",
        "make sense": "Your explanation makes sense.",
        "consist of": "The team consists of ten students.",
        "divide into": "The book is divided into five parts.",
        "divide…into": "The book is divided into five parts.",
        "break away": "The group tried to break away.",
        "break away from": "The village broke away from the old system.",
        "to one's credit": "To his credit, he admitted the mistake.",
        "to one’s credit": "To his credit, he admitted the mistake.",
        "take the place of": "Robots may take the place of some workers.",
        "break down": "The car broke down on the way.",
        "be back on one's feet": "After a month, she was back on her feet.",
        "be back on one’s feet": "After a month, she was back on her feet.",
        "lose sight of": "We should not lose sight of our goal.",
        "lose sight of…": "We should not lose sight of our goal.",
        "sweep up": "Please sweep up the broken glass.",
        "slide into": "The car slid into a ditch.",
        "speed up": "The new system can speed up the process.",
        "concentrate on": "Please concentrate on your work.",
        "depend on": "Success depends on hard work.",
        "accuse of": "They accused him of stealing the money.",
        "accuse…of": "They accused him of stealing the money.",
        "so as to": "He spoke slowly so as to be understood.",
        "so as to (do sth)": "He spoke slowly so as to be understood.",
        "first aid": "Everyone should learn basic first aid.",
        "fall ill": "She fell ill during the trip.",
        "electric shock": "An electric shock can be dangerous.",
        "squeeze out": "Squeeze out the extra water.",
        "over and over again": "She practiced the song over and over again.",
        "in place": "Everything is in place for the meeting.",
        "a number of": "A number of students joined the club.",
        "put one's hands on": "I cannot put my hands on the report.",
        "put one’s hands on": "I cannot put my hands on the report.",
        "by coincidence": "By coincidence, we chose the same topic.",
        "a great deal": "He learned a great deal from the experience.",
        "on the other hand": "On the other hand, the plan may cost too much.",
        "in the flesh": "I finally saw the famous singer in the flesh.",
        "appeal to": "The idea may appeal to young readers.",
        "take it easy": "Take it easy and try again.",
        "be made up of": "The team is made up of volunteers.",
        "in particular": "I like this poem in particular.",
        "try out": "We should try out the new method.",
        "due to": "The flight was late due to bad weather.",
        "addicted to": "He became addicted to online games.",
        "accustomed to": "She is accustomed to hard work.",
        "decide on": "We need to decide on a date.",
        "feel like": "I feel like going for a walk.",
        "feel like doing": "I feel like reading tonight.",
        "in spite of": "In spite of the rain, we kept walking.",
        "take a risk": "He took a risk to save the child.",
        "come about": "How did this change come about?",
        "subscribe to": "Many scientists subscribe to this view.",
        "quantities of": "Factories use quantities of water.",
        "go up": "Prices may go up next month.",
        "result in": "Careless driving can result in accidents.",
        "be opposed to": "Many people are opposed to the plan.",
        "even if": "Even if it rains, we will continue.",
        "keep on": "Keep on practicing until you improve.",
        "on the whole": "On the whole, the plan is useful.",
        "on behalf of": "She spoke on behalf of the class.",
        "put up with": "I cannot put up with the noise.",
        "so long as": "You can join us so long as you are on time.",
        "and so on": "We need pens, paper, notebooks, and so on.",
        "burn to the ground": "The old house burned to the ground.",
        "make one's way": "She made her way through the crowd.",
        "make one’s way": "She made her way through the crowd.",
        "glance through": "He glanced through the report before the meeting.",
        "vary from to": "Prices vary from city to city.",
        "vary from…to": "Prices vary from city to city.",
        "in other words": "In other words, we need a better plan.",
        "adapt to": "Students must adapt to a new environment.",
        "out of breath": "He was out of breath after running.",
        "in many ways": "In many ways, the two cities are similar.",
        "make fun of": "It is unkind to make fun of others.",
        "never mind": "Never mind; you can try again.",
        "all the best": "I wish you all the best.",
        "meet with": "The plan met with strong support.",
        "test out": "Engineers tested out the new robot.",
        "ring up": "Please ring me up when you arrive.",
        "turn around": "She turned around and smiled.",
        "leave alone": "Leave the machine alone until it cools down.",
        "leave…alone": "Leave the machine alone until it cools down.",
        "in all": "There were fifty guests in all.",
        "be bound to": "Hard work is bound to bring progress.",
        "master's degree": "She earned a master's degree in biology.",
        "in the meantime": "In the meantime, we prepared the room.",
        "help out": "Can you help out after school?",
        "help (…) out": "Can you help out after school?",
        "become aware of": "People became aware of the danger.",
        "be aware of": "We should be aware of our mistakes.",
        "be scared to death": "The loud noise scared me to death.",
        "(be) scared to death": "The loud noise scared me to death.",
        "hear from": "I hope to hear from you soon.",
        "be dying to": "She is dying to visit Paris.",
        "(be) dying to": "She is dying to visit Paris.",
        "the other day": "I met your brother the other day.",
        "dry out": "The wet clothes dried out in the sun.",
        "dry up": "The river dried up during the drought.",
        "in need": "We should help people in need.",
        "adjust to": "It took him months to adjust to the new school.",
        "keep it up": "You are doing well; keep it up.",
        "fit in": "She tried to fit in with her new classmates.",
        "as far as one is concerned": "As far as I am concerned, the plan is practical.",
        "be occupied with": "He is occupied with his research.",
        "bachelor's degree": "He received a bachelor's degree last year.",
        "day in and day out": "She practiced day in and day out.",
        "out of the question": "Leaving early is out of the question.",
        "settle in": "The family settled in quickly.",
        "by means of": "They solved the problem by means of technology.",
        "by means of…": "They solved the problem by means of technology.",
        "make a life": "They worked hard to make a life in a new country.",
        "keep up": "Try to keep up with the class.",
        "cable car": "We took a cable car up the hill.",
        "team up with": "Our class teamed up with another school.",
        "mark out": "They marked out the area for the game.",
        "take in": "The tour guide took in the whole city.",
        "a great many": "A great many people attended the concert.",
        "a good many": "A good many students joined the club.",
        "pay off": "His hard work paid off in the end.",
        "cast down": "She felt cast down after the failure.",
        "in favour of": "Most students are in favour of the plan.",
        "side road": "The car turned into a side road.",
        "(be) bound to (do)": "The plan is bound to succeed.",
        "strike into one's heart": "The news struck fear into his heart.",
        "strike…into one’s heart": "The news struck fear into his heart.",
        "bring back to life": "The rain brought the dry land back to life.",
        "in vain": "They tried in vain to open the door.",
        "in good condition": "The old book is still in good condition.",
        "in poor condition": "The road is in poor condition.",
        "now and then": "I visit my hometown now and then.",
        "set about": "She set about cleaning the room.",
        "beaten track": "They left the beaten track and explored the valley.",
        "dive into": "He dived into the data with great interest.",
        "set out to do": "They set out to solve the problem.",
        "set out (to do)": "They set out to solve the problem.",
        "hang on": "Hang on a minute; I will check.",
        "out of order": "The elevator is out of order.",
        "get through": "I finally got through to the office.",
        "ring back": "I will ring back in ten minutes.",
        "ring off": "She rang off before I could answer.",
        "in disguise": "The prince traveled in disguise.",
        "pass off as": "He tried to pass the copy off as the original.",
        "pass…off as…": "He tried to pass the copy off as the original.",
        "make one's acquaintance": "I was glad to make her acquaintance.",
        "make one’s acquaintance": "I was glad to make her acquaintance.",
        "in amazement": "The children stared in amazement.",
        "generally speaking": "Generally speaking, the method is reliable.",
        "in terms of": "In terms of cost, this plan is better.",
        "in terms of…": "In terms of cost, this plan is better.",
        "show in": "Please show the guest in.",
        "show…in": "Please show the guest in.",
        "wax disk": "The museum displayed an old wax disk.",
        "once more": "Please read the passage once more.",
        "in need of": "The village is in need of clean water.",
        "regardless of": "He kept working regardless of the difficulty.",
        "at most": "The walk will take ten minutes at most.",
        "fed up with": "She is fed up with the noise.",
        "look ahead": "We need to look ahead and plan carefully.",
        "date back": "The tradition dates back hundreds of years.",
        "date back to": "The castle dates back to the 12th century.",
        "in reality": "In reality, the task was harder than expected.",
        "at the mercy of": "The small boat was at the mercy of the storm.",
        "set loose": "The farmer set the horse loose in the field.",
        "jaws of death": "The climber escaped from the jaws of death.",
        "associate with": "People often associate the smell with childhood.",
        "out of respect": "We stood up out of respect.",
        "correspond with": "She corresponds with friends overseas.",
        "owe to": "He owes his success to hard work.",
        "talk into": "I talked him into joining the club.",
        "talk… into": "I talked him into joining the club.",
        "turn into": "The rain turned into snow.",
        "turn… into": "The rain turned into snow.",
        "fit into": "This shelf can fit into the small room.",
        "have no use for": "She has no use for excuses.",
    }
)

PHRASE_EXAMPLES.update(SENIOR_PHRASE_EXAMPLES)


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def clean_translation(translation: str) -> str:
    translation = translation.replace("中文释义:", "")
    translation = translation.replace("<美>", "美").replace("<英>", "英")
    return WHITESPACE_RE.sub(" ", translation).strip()


def load_translation_cache() -> dict[str, str]:
    global _TRANSLATION_CACHE
    if _TRANSLATION_CACHE is None:
        if TRANSLATION_CACHE_PATH.exists():
            _TRANSLATION_CACHE = json.loads(
                TRANSLATION_CACHE_PATH.read_text(encoding="utf-8")
            )
        else:
            _TRANSLATION_CACHE = {}
    return _TRANSLATION_CACHE


def primary_chinese(translation: str) -> str:
    text = clean_translation(translation)
    text = re.sub(r"^[（(][^）)]*[）)]", "", text).strip()
    text = re.sub(r"[（(][^）)]*[）)]", "", text)
    text = re.sub(r"^[^一-龥]*", "", text).strip()
    parts = re.split(r"[；;，,、/]| 或 | 和 |及|等", text)
    for part in parts:
        part = part.strip(" .。:：；;，,、")
        if part:
            return part
    return text.strip() or "这个词"


def chinese_label(term: str, translation: str) -> str:
    key = canonical_key(term)
    labels = {
        "i": "我",
        "you": "你",
        "he": "他",
        "she": "她",
        "it": "它",
        "we": "我们",
        "they": "他们",
        "my": "我的",
        "your": "你的",
        "his": "他的",
        "her": "她的",
        "our": "我们的",
        "their": "他们的",
        "ruler": "尺子",
        "pencil": "铅笔",
        "eraser": "橡皮",
        "crayon": "蜡笔",
        "bag": "包",
        "pen": "钢笔",
        "pencil box": "铅笔盒",
        "book": "书",
        "mum": "妈妈",
        "mom": "妈妈",
        "dad": "爸爸",
        "father": "父亲",
        "mother": "母亲",
        "brother": "兄弟",
        "sister": "姐妹",
        "orange": "橙色",
        "uk": "英国",
        "usa": "美国",
        "china": "中国",
        "canada": "加拿大",
    }
    return labels.get(key, primary_chinese(translation))


def quote_term(term: str) -> str:
    return f"“{term}”"


def translate_example(sentence: str, term: str, translation: str, level: str) -> str:
    sentence = normalize_sentence(sentence)
    cached_translation = load_translation_cache().get(sentence)
    if cached_translation:
        return cached_translation
    if sentence in EXACT_SENTENCE_TRANSLATIONS:
        return EXACT_SENTENCE_TRANSLATIONS[sentence]

    cn = chinese_label(term, translation)
    key = canonical_key(term)
    usable = term_for_sentence(term)
    lower = usable.lower()

    patterns: list[tuple[str, str]] = [
        (rf"^I put the {re.escape(lower)} in my schoolbag\.$", f"我把{cn}放进我的书包里。"),
        (rf"^There is (?:a|an) {re.escape(lower)} in the picture\.$", f"图画里有一个{cn}。"),
        (rf"^I can see (?:a|an) {re.escape(lower)}\.$", f"我能看到一个{cn}。"),
        (rf"^The {re.escape(lower)} is on the desk\.$", f"{cn}在书桌上。"),
        (rf"^My {re.escape(lower)} is in my schoolbag\.$", f"我的{cn}在书包里。"),
        (rf"^My {re.escape(lower)} is kind to me\.$", f"我的{cn}对我很好。"),
        (rf"^I saw (?:a|an) {re.escape(lower)} at the zoo\.$", f"我在动物园看见了一只{cn}。"),
        (rf"^We saw (?:a|an) {re.escape(lower)} at the zoo\.$", f"我们在动物园看见了一只{cn}。"),
        (rf"^The {re.escape(lower)} lives near the forest\.$", f"{cn}生活在森林附近。"),
        (rf"^The {re.escape(lower)} is interesting\.$", f"这只{cn}很有趣。"),
        (rf"^I like {re.escape(lower)} for lunch\.$", f"我午餐喜欢吃/喝{cn}。"),
        (rf"^I would like some {re.escape(lower)}\.$", f"我想要一些{cn}。"),
        (rf"^{re.escape(term.capitalize())} tastes good\.$", f"{cn}尝起来很好。"),
        (rf"^I ate (?:a|an) {re.escape(lower)} for lunch\.$", f"我午餐吃了一个{cn}。"),
        (rf"^Would you like (?:a|an) {re.escape(lower)}\?$", f"你想要一个{cn}吗？"),
        (rf"^The {re.escape(lower)} tastes good\.$", f"这个{cn}尝起来很好。"),
        (rf"^Please point to your {re.escape(lower)}\.$", f"请指一指你的{cn}。"),
        (rf"^Take care of your {re.escape(lower)}\.$", f"照顾好你的{cn}。"),
        (rf"^We learned about {re.escape(lower)} in science class\.$", f"我们在科学课上学习了{cn}。"),
        (rf"^I have a {re.escape(lower)} today\.$", f"我今天有点{cn}。"),
        (rf"^Rest can help with a {re.escape(lower)}\.$", f"休息有助于缓解{cn}。"),
        (rf"^We visited the {re.escape(lower)} yesterday\.$", f"我们昨天参观了{cn}。"),
        (rf"^We went to the {re.escape(lower)} yesterday\.$", f"我们昨天去了{cn}。"),
        (rf"^The {re.escape(lower)} is near my home\.$", f"{cn}在我家附近。"),
        (rf"^The {re.escape(lower)} helped us after class\.$", f"{cn}课后帮助了我们。"),
        (rf"^I met (?:a|an) {re.escape(lower)} yesterday\.$", f"我昨天遇见了一位{cn}。"),
        (rf"^The {re.escape(lower)} helped us\.$", f"这位{cn}帮助了我们。"),
        (rf"^{re.escape(term.capitalize())} is useful at school\.$", f"{cn}在学校很有用。"),
        (rf"^The {re.escape(lower)} is useful in our lesson\.$", f"{cn}在我们的课上很有用。"),
        (rf"^We talked about {re.escape(lower)} in class today\.$", f"我们今天在课堂上谈到了{cn}。"),
        (rf"^The discussion gave us a deeper understanding of {re.escape(lower)}\.$", f"这次讨论让我们更深入地理解了{cn}。"),
        (rf"^We talked about {re.escape(lower)} in class\.$", f"我们在课堂上谈到了{cn}。"),
        (rf"^We discussed {re.escape(lower)} in class\.$", f"我们在课堂上讨论了{cn}。"),
        (rf"^{re.escape(term.capitalize())} is important in our life\.$", f"{cn}在我们的生活中很重要。"),
        (rf"^She answered {re.escape(lower)} during the discussion\.$", f"她在讨论中以“{cn}”的方式回答。"),
        (rf"^The team worked {re.escape(lower)}\.$", f"团队以“{cn}”的方式工作。"),
        (rf"^Please speak {re.escape(lower)}\.$", f"请以“{cn}”的方式说话。"),
        (rf"^This is a {re.escape(lower)} example\.$", f"这是一个{cn}的例子。"),
        (rf"^The result seems {re.escape(lower)}\.$", f"结果似乎很{cn}。"),
        (rf"^The example is {re.escape(lower)}\.$", f"这个例子很{cn}。"),
        (rf"^{re.escape(term.capitalize())} is useful in daily life\.$", f"{cn}在日常生活中很有用。"),
        (rf"^The {re.escape(lower)} is useful in daily life\.$", f"{cn}在日常生活中很有用。"),
        (rf"^I saw (?:a|an) {re.escape(lower)} in the picture\.$", f"我在图画中看到了一个{cn}。"),
        (rf"^We talked about the {re.escape(lower)} in class\.$", f"我们在课堂上谈到了{cn}。"),
        (rf"^I learned more about {re.escape(lower)} today\.$", f"我今天进一步了解了{cn}。"),
        (rf"^We read about {re.escape(term)} in geography class\.$", f"我们在地理课上读到了{cn}。"),
        (rf"^We read about {re.escape(term)} in the lesson\.$", f"我们在课文中读到了{cn}。"),
        (rf"^We learned about {re.escape(term)} in class\.$", f"我们在课堂上学习了{cn}。"),
        (rf"^I want to know more about {re.escape(term)}\.$", f"我想进一步了解{cn}。"),
    ]
    for pattern, chinese in patterns:
        if re.match(pattern, sentence, re.I):
            return chinese

    if sentence == f'We practiced the phrase "{term}" in class.':
        return f"我们在课堂上练习了短语{quote_term(term)}。"
    if sentence == f'Can you make a sentence with "{term}"?':
        return f"你能用{quote_term(term)}造一个句子吗？"
    if sentence == f'We learned the word "{term}" today.':
        return f"我们今天学习了单词{quote_term(term)}。"
    if sentence == f'Please read "{term}" aloud.':
        return f"请大声读出{quote_term(term)}。"
    if sentence == f'Can you use "{term}" in your own sentence?':
        return f"你能用{quote_term(term)}造自己的句子吗？"
    if sentence == f'The word "{term}" is used as a verb here.':
        return f"单词{quote_term(term)}在这里作动词使用。"
    if sentence == f'Can you use "{term}" in a sentence?':
        return f"你能用{quote_term(term)}造句吗？"
    if sentence == f'The word "{term}" shows an action.':
        return f"单词{quote_term(term)}表示一个动作。"
    if sentence == f'Please make your own sentence with "{term}".':
        return f"请用{quote_term(term)}造一个自己的句子。"
    if sentence == f'The word "{term}" shows an action in this sentence.':
        return f"单词{quote_term(term)}在这个句子中表示动作。"
    if sentence == f"The word {term} appears in the reading passage.":
        return f"单词{quote_term(term)}出现在阅读文章中。"

    if key in SPECIAL_EXAMPLES or key in SPECIAL_EXTRA_SENTENCES:
        return f"这个句子的中文意思与{quote_term(term)}（{cn}）有关。"
    if " " in term.strip() or any(mark in term for mark in ("...", "…", "(", ")", "/", "!", "?")):
        return f"这个句子展示了短语{quote_term(term)}的用法，意思与“{cn}”有关。"
    return f"这个句子使用了单词{quote_term(term)}，意思与“{cn}”有关。"


def canonical_key(term: str) -> str:
    key = term.strip()
    if key not in PROTECTED_DOT_TERMS:
        key = key.strip(" .。;；,，")
    key = key.replace("’", "'")
    key = key.replace("（", "(").replace("）", ")")
    key = key.replace("……", "…")
    key = key.replace("… …", "…")
    key = key.replace("sb.'s", "one's")
    key = key.replace("sb’s", "one's")
    key = key.replace("one’s", "one's")
    key = key.replace("(sth)", "")
    key = key.replace("(sb)", "")
    key = key.replace("(school)", "school")
    key = key.replace("(of…)", "")
    key = key.replace("(a)", " a ")
    key = key.replace("(large)", " large ")
    key = key.replace("(be)", "be")
    key = key.replace("（be）", "be")
    key = key.replace("to one's", "to one's")
    key = key.replace("one's", "one's")
    key = ELLIPSIS_RE.sub(" ", key)
    key = key.replace("/", " ")
    key = key.replace("(", " ").replace(")", " ")
    key = WHITESPACE_RE.sub(" ", key).strip()
    return key.lower()


def term_for_sentence(term: str) -> str:
    value = term.strip()
    if value not in PROTECTED_DOT_TERMS:
        value = value.strip(" .。;；,，")
    value = value.replace("（", "(").replace("）", ")")
    value = value.replace("’", "'")
    value = re.sub(r"\bsb\.?'s\b", "your", value)
    value = re.sub(r"\bsb\b", "someone", value)
    value = re.sub(r"\bsth\b", "something", value)
    value = value.replace("one's", "your")
    value = value.replace("one’s", "your")
    value = value.replace("(school)", "school")
    value = value.replace("(sth)", "it")
    value = value.replace("(sb)", "me")
    value = value.replace("(of…)", "of")
    value = value.replace("(a)", " a ")
    value = value.replace("(large)", " large ")
    value = value.replace("(be)", "be")
    value = value.replace("（be）", "be")
    value = ELLIPSIS_RE.sub(" ", value)
    value = value.replace("/", " or ")
    value = value.replace("(", " ").replace(")", " ")
    return WHITESPACE_RE.sub(" ", value).strip()


def has_any(text: str, hints: tuple[str, ...]) -> bool:
    return any(hint in text for hint in hints)


def is_probably_proper(term: str, translation: str) -> bool:
    if term.isupper() and len(term) > 1:
        return True
    if any(
        marker in translation
        for marker in (
            "（姓",
            "（女名",
            "（男名",
            "人名",
            "地名",
            "国名",
            "首都",
            "国家",
            "城市",
            "州名",
            "河",
            "湖",
            "山",
            "岛",
            "公园",
            "城堡",
            "机构",
            "组织",
            "奖",
            "节",
            "神话",
            "作家",
            "科学家",
            "发明家",
            "人物",
            "旧称",
        )
    ):
        return True
    return bool(re.match(r"^[A-Z][A-Za-z]+(?:[ .'-][A-Z][A-Za-z]+)+$", term))


def article_for(term: str) -> str:
    lower = term.lower()
    article = "an" if lower.startswith(VOWEL_SOUND_PREFIXES) else "a"
    return article


def article_phrase(term: str) -> str:
    return f"{article_for(term)} {term}"


def plural_or_mass(term: str) -> bool:
    lower = term.lower()
    if lower in UNCOUNTABLE_TERMS or lower in PLURAL_OR_MASS_NOUNS:
        return True
    return lower.endswith("s") and lower not in {"bus", "class", "glass", "dress"}


def likely_noun_by_form(term: str) -> bool:
    lower = term.lower()
    return lower.endswith(
        (
            "tion",
            "sion",
            "ment",
            "ness",
            "ity",
            "ance",
            "ence",
            "ship",
            "ism",
            "ist",
            "er",
            "or",
            "ee",
            "age",
            "ure",
            "hood",
            "dom",
        )
    )


def adjective_sentence(term: str, translation: str) -> str:
    lower = term.lower()
    if "木制" in translation or "木头" in translation:
        return f"The chair is {lower}."
    if "古" in translation or "远古" in translation:
        return f"The building is {lower}."
    if "私" in translation or "个人" in translation:
        return f"This is a {lower} choice."
    if "电子" in translation or "科技" in translation:
        return f"The device is {lower}."
    if "音乐" in translation:
        return f"The performance is {lower}."
    if "快" in translation or "迅速" in translation:
        return f"The train is {lower}."
    if "方便" in translation or "便利" in translation:
        return f"The method is {lower}."
    if "礼貌" in translation:
        return f"The student is {lower}."
    if "自豪" in translation or "骄傲" in translation:
        return f"She is {lower} of her progress."
    if "缺席" in translation:
        return f"He was {lower} from class."
    if "酸" in translation or "脆" in translation:
        return f"The apple tastes {lower}."
    if "聪明" in translation or "智能" in translation:
        return f"The student is {lower}."
    if "吸引" in translation or "迷人" in translation:
        return f"The city is {lower}."
    if "有用" in translation or "帮助" in translation:
        return f"The advice is {lower}."
    if "幽默" in translation:
        return f"The speaker is {lower}."
    if "沉默" in translation:
        return f"The room became {lower}."
    if "敏感" in translation:
        return f"This topic is {lower}."
    if "痛苦" in translation:
        return f"The lesson was {lower} but important."
    if "总" in translation or "整个" in translation:
        return f"The total cost is clear."
    if "死" in translation:
        return f"The plant is {lower}."
    if "突然" in translation:
        return f"The change was {lower}."
    if lower.startswith(("un", "in", "im", "ir", "il")):
        return f"The result seems {lower}."
    return f"The example is {lower}."


def noun_sentence(term: str, level: str) -> str:
    lower = term.lower()
    if plural_or_mass(lower):
        verb = "is" if lower in UNCOUNTABLE_TERMS else "are"
        return f"{term.capitalize()} {verb} important in this lesson."
    if level == "小学":
        return f"There is {article_phrase(lower)} in the picture."
    if level == "初中":
        return f"The {lower} is useful in daily life."
    return f"The {lower} became important during the discussion."


def phrase_sentence(term: str, translation: str, level: str) -> str | None:
    key = canonical_key(term)
    if key in SPECIAL_EXAMPLES:
        return SPECIAL_EXAMPLES[key]
    if key in PHRASE_EXAMPLES:
        return PHRASE_EXAMPLES[key]

    usable = term_for_sentence(term)
    lower = usable.lower()
    if not usable:
        return None

    if lower.startswith("be "):
        rest = usable[3:]
        if rest.startswith(("good at", "interested in", "proud of", "responsible for")):
            return f"We should be {rest} our work."
        return f"It is important to be {rest} at the right time."
    if lower.startswith("in "):
        return f"{usable[0].upper() + usable[1:]}, we can understand the idea better."
    if lower.startswith("on "):
        return f"{usable[0].upper() + usable[1:]}, the plan worked well."
    if lower.startswith("at "):
        return f"{usable[0].upper() + usable[1:]}, everyone was ready."
    if lower.startswith("by "):
        return f"{usable[0].upper() + usable[1:]}, we solved the problem."
    if lower.startswith("from "):
        return f"{usable[0].upper() + usable[1:]}, the story becomes clearer."
    if lower.startswith("as "):
        return f"{usable[0].upper() + usable[1:]}, we need more practice."
    if lower.startswith("out of "):
        return f"He acted {usable} kindness."
    if lower.startswith("no "):
        return f"There is {usable} in trying again."
    if lower.startswith("the "):
        return f"{usable[0].upper() + usable[1:]} is mentioned in the lesson."
    if lower.startswith(("go ", "get ", "take ", "make ", "keep ", "look ", "put ", "turn ", "give ", "come ", "fall ", "break ", "bring ", "pay ", "set ", "run ", "cut ", "carry ", "deal ", "depend ", "rely ", "refer ", "lead ", "belong ", "listen ", "talk ", "work ", "play ", "read ", "write ", "speak ", "watch ", "wear ", "wash ", "draw ", "sing ", "jump ", "count ")):
        return f"We often {usable} in daily life."
    if level == "小学":
        return f"I can use {usable} in a simple sentence."
    if level == "初中":
        return f"Our teacher explained how to use {usable} in conversation."
    return f"The article shows how to use {usable} in context."


def category_sentence(term: str, translation: str, level: str) -> str:
    lower = term.lower()
    translation = clean_translation(translation)

    if lower in SPECIAL_EXAMPLES:
        return SPECIAL_EXAMPLES[lower]
    if lower in COLOR_EXAMPLES and ("色" in translation or "颜色" in translation):
        return COLOR_EXAMPLES[lower]
    if lower in COMMON_VERB_EXAMPLES and (
        has_any(translation, VERB_HINTS) or lower not in AMBIGUOUS_VERB_TERMS
    ):
        return COMMON_VERB_EXAMPLES[lower]
    if lower in ADJECTIVE_EXAMPLES and has_any(translation, ADJECTIVE_HINTS):
        return ADJECTIVE_EXAMPLES[lower]
    if is_probably_proper(term, translation):
        if has_any(translation, ("河", "湖", "山", "岛", "国家", "城市", "公园", "城堡", "首都")):
            return f"We read about {term} in geography class."
        return f"We read about {term} in the lesson."
    if has_any(translation, ADJECTIVE_HINTS):
        return adjective_sentence(term, translation)
    if has_any(translation, FOOD_HINTS):
        if plural_or_mass(lower):
            return f"I like {lower} for lunch."
        return f"I ate {article_phrase(lower)} for lunch."
    if has_any(translation, ANIMAL_HINTS):
        return f"The {lower} lives near the forest." if level == "高中" else f"I saw {article_phrase(lower)} at the zoo."
    if has_any(translation, BODY_HINTS):
        return f"My {lower} hurts a little."
    if has_any(translation, FAMILY_HINTS):
        return f"My {lower} is kind to me."
    if has_any(translation, PLACE_HINTS):
        return f"We visited the {lower} yesterday."
    if has_any(translation, PERSON_HINTS):
        return f"The {lower} helped us after class."
    if has_any(translation, SCHOOL_HINTS):
        if lower in UNCOUNTABLE_TERMS:
            return f"{term.capitalize()} is useful at school."
        return f"I put the {lower} in my schoolbag." if level == "小学" else f"The {lower} is useful in our lesson."
    if has_any(translation, TIME_HINTS):
        return f"We talked about {lower} in class today."
    if has_any(translation, ABSTRACT_HINTS):
        if level == "高中":
            return f"The discussion gave us a deeper understanding of {lower}."
        return f"We talked about {lower} in class."
    if lower.endswith("ly") or any(hint in translation for hint in ("地", "常常", "偶然", "逐渐", "完全", "终于")):
        if lower in {"firstly", "secondly", "finally"}:
            return f"{term.capitalize()}, we checked our answers carefully."
        return f"She answered {lower} during the discussion."
    if has_any(translation, VERB_HINTS):
        if lower.endswith(("ed", "ing")):
            return f"The word {term} appears in the reading passage."
        return f'The word "{term}" shows an action in this sentence.'
    if likely_noun_by_form(lower):
        return noun_sentence(term, level)

    return noun_sentence(term, level)


def generate_sentence(term: str, translation: str, level: str) -> str:
    key = canonical_key(term)
    if key in SPECIAL_EXAMPLES:
        return SPECIAL_EXAMPLES[key]
    if " " in term.strip() or any(mark in term for mark in ("...", "…", "(", ")", "/", "!", "?")):
        sentence = phrase_sentence(term, translation, level)
        if sentence:
            return sentence
    return category_sentence(term_for_sentence(term), translation, level)


def normalize_sentence(sentence: str) -> str:
    sentence = WHITESPACE_RE.sub(" ", sentence).strip()
    if sentence and sentence[-1] not in ".!?":
        sentence += "."
    return sentence


def add_unique_sentence(sentences: list[str], sentence: str) -> None:
    sentence = normalize_sentence(sentence)
    if sentence and sentence not in sentences:
        sentences.append(sentence)


def simple_word(term: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z'-]*", term))


def noun_extra_sentences(term: str, level: str) -> list[str]:
    lower = term.lower()
    if plural_or_mass(lower):
        return [
            f"{term.capitalize()} is useful in daily life.",
            f"We talked about {lower} in class.",
            f"I learned more about {lower} today.",
        ]
    if simple_word(lower):
        article = article_phrase(lower)
        if level == "小学":
            return [
                f"I can see {article}.",
                f"The {lower} is on the desk.",
                f"Please point to the {lower}.",
            ]
        return [
            f"The {lower} is useful in daily life.",
            f"I saw {article} in the picture.",
            f"We talked about the {lower} in class.",
        ]
    return [
        f"We learned the word \"{term}\" in class.",
        f"Please read \"{term}\" aloud.",
        f"Can you use \"{term}\" in your own sentence?",
    ]


def generate_more_sentences(term: str, translation: str, level: str) -> list[str]:
    key = canonical_key(term)
    usable = term_for_sentence(term)
    lower = usable.lower()
    clean_trans = clean_translation(translation)
    sentences: list[str] = []

    add_unique_sentence(sentences, generate_sentence(term, translation, level))

    if key in SPECIAL_EXTRA_SENTENCES:
        for sentence in SPECIAL_EXTRA_SENTENCES[key]:
            add_unique_sentence(sentences, sentence)
    elif key in PHRASE_EXAMPLES or " " in term.strip() or any(
        mark in term for mark in ("...", "…", "(", ")", "/", "!", "?")
    ):
        add_unique_sentence(sentences, f"We practiced the phrase \"{term}\" in class.")
        add_unique_sentence(sentences, f"Can you make a sentence with \"{term}\"?")
    elif is_probably_proper(term, clean_trans) or key in COUNTRY_EXAMPLES:
        add_unique_sentence(sentences, f"We learned about {term} in class.")
        add_unique_sentence(sentences, f"I want to know more about {term}.")
    elif lower in COLOR_EXAMPLES and ("色" in clean_trans or "颜色" in clean_trans):
        add_unique_sentence(sentences, f"I like the color {lower}.")
        add_unique_sentence(sentences, f"The flower is {lower}.")
    elif lower in NOUN_EXAMPLES:
        if has_any(clean_trans, PERSON_HINTS) and simple_word(lower) and not plural_or_mass(lower):
            add_unique_sentence(sentences, f"I met {article_phrase(lower)} yesterday.")
            add_unique_sentence(sentences, f"The {lower} helped us.")
        else:
            for sentence in noun_extra_sentences(usable, level):
                add_unique_sentence(sentences, sentence)
    elif lower in BODY_EXAMPLES or has_any(clean_trans, BODY_HINTS):
        if lower.endswith("ache") or lower == "nosebleed":
            add_unique_sentence(sentences, f"I have a {lower} today.")
            add_unique_sentence(sentences, f"Rest can help with a {lower}.")
        elif lower in {"blood", "brain", "skin", "hair"}:
            add_unique_sentence(sentences, f"Take care of your {lower}.")
            add_unique_sentence(sentences, f"We learned about {lower} in science class.")
        else:
            add_unique_sentence(sentences, f"Please point to your {lower}.")
            add_unique_sentence(sentences, f"Take care of your {lower}.")
    elif has_any(clean_trans, FOOD_HINTS):
        if plural_or_mass(lower):
            add_unique_sentence(sentences, f"I would like some {lower}.")
            add_unique_sentence(sentences, f"{term.capitalize()} tastes good.")
        else:
            add_unique_sentence(sentences, f"Would you like {article_phrase(lower)}?")
            add_unique_sentence(sentences, f"The {lower} tastes good.")
    elif has_any(clean_trans, ANIMAL_HINTS):
        if simple_word(lower):
            add_unique_sentence(sentences, f"We saw {article_phrase(lower)} at the zoo.")
            add_unique_sentence(sentences, f"The {lower} is interesting.")
    elif has_any(clean_trans, PLACE_HINTS):
        add_unique_sentence(sentences, f"We went to the {lower} yesterday.")
        add_unique_sentence(sentences, f"The {lower} is near my home.")
    elif lower in COMMON_VERB_EXAMPLES and (
        has_any(clean_trans, VERB_HINTS) or lower not in AMBIGUOUS_VERB_TERMS
    ):
        add_unique_sentence(sentences, f"The word \"{term}\" is used as a verb here.")
        add_unique_sentence(sentences, f"Can you use \"{term}\" in a sentence?")
    elif has_any(clean_trans, VERB_HINTS):
        add_unique_sentence(sentences, f"The word \"{term}\" shows an action.")
        add_unique_sentence(sentences, f"Please make your own sentence with \"{term}\".")
    elif lower in ADJECTIVE_EXAMPLES or has_any(clean_trans, ADJECTIVE_HINTS):
        add_unique_sentence(sentences, f"This is a {lower} example.")
        add_unique_sentence(sentences, f"The result seems {lower}.")
    elif has_any(clean_trans, ABSTRACT_HINTS):
        add_unique_sentence(sentences, f"We discussed {lower} in class.")
        add_unique_sentence(sentences, f"{term.capitalize()} is important in our life.")
    elif lower.endswith("ly") or any(
        hint in clean_trans for hint in ("地", "常常", "偶然", "逐渐", "完全", "终于")
    ):
        add_unique_sentence(sentences, f"The team worked {lower}.")
        add_unique_sentence(sentences, f"Please speak {lower}.")
    else:
        for sentence in noun_extra_sentences(usable, level):
            add_unique_sentence(sentences, sentence)

    for fallback in (
        f"We learned the word \"{term}\" today.",
        f"Please read \"{term}\" aloud.",
        f"Can you use \"{term}\" in your own sentence?",
    ):
        if len(sentences) >= MORE_EXAMPLE_COUNT:
            break
        add_unique_sentence(sentences, fallback)

    return sentences[:MORE_EXAMPLE_COUNT]


def append_more_examples(lines: list[str], rows: list[tuple[str, str, str]], level: str) -> list[str]:
    while lines and not lines[-1].strip():
        lines.pop()
    lines.extend(["", MORE_EXAMPLES_HEADING, ""])
    for idx, word, translation in rows:
        lines.append(f"### {idx}. {word}")
        for sentence_idx, sentence in enumerate(
            generate_more_sentences(word, translation, level), start=1
        ):
            lines.append(f"{sentence_idx}. {sentence}")
            lines.append(f"   中文：{translate_example(sentence, word, translation, level)}")
        lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def detect_level(path: pathlib.Path) -> str:
    parts = set(path.parts)
    if "小学" in parts:
        return "小学"
    if "初中" in parts:
        return "初中"
    if "高中" in parts:
        return "高中"
    return "初中"


def update_vocab_file(path: pathlib.Path) -> tuple[int, bool]:
    level = detect_level(path)
    original_text = path.read_text(encoding="utf-8")
    lines = original_text.splitlines()
    if MORE_EXAMPLES_HEADING in lines:
        lines = lines[: lines.index(MORE_EXAMPLES_HEADING)]
    updated: list[str] = []
    rows: list[tuple[str, str, str]] = []
    row_count = 0
    previous_was_header = False

    for line in lines:
        cells_for_detection = split_markdown_row(line) if line.startswith("|") else []
        if cells_for_detection[:5] == HEADER_CELLS:
            updated.append(TABLE_HEADER_WITH_EXAMPLES)
            previous_was_header = True
            continue

        if previous_was_header and line.startswith("| --- |"):
            updated.append(TABLE_DIVIDER_WITH_EXAMPLES)
            previous_was_header = False
            continue

        previous_was_header = False

        if cells_for_detection and cells_for_detection[0].strip().isdigit():
            cells = cells_for_detection
            if len(cells) < 5:
                updated.append(line)
                continue
            row_count += 1
            sentence = generate_sentence(cells[1], cells[4], level)
            sentence_translation = translate_example(sentence, cells[1], cells[4], level)
            new_cells = cells[:5] + [sentence, sentence_translation]
            rows.append((cells[0], cells[1], cells[4]))
            updated.append(markdown_row(new_cells))
            continue

        updated.append(line)

    if rows:
        updated = append_more_examples(updated, rows, level)

    new_text = "\n".join(updated) + "\n"
    changed = new_text != original_text
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return row_count, changed


def main() -> None:
    vocab_files = sorted(
        path for path in ROOT.rglob("*.md") if path.name != "README.md"
    )
    total_rows = 0
    changed_files = 0
    for path in vocab_files:
        row_count, changed = update_vocab_file(path)
        total_rows += row_count
        if changed:
            changed_files += 1
        print(f"{path.relative_to(ROOT)}: {row_count} rows")
    total_sentences = total_rows * (1 + MORE_EXAMPLE_COUNT)
    print(f"Updated {changed_files} files; generated {total_sentences} example sentences.")


if __name__ == "__main__":
    main()
