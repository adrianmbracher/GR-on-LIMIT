pseudo_query_prompt = f"""
Create a diverse set of questions starting with "Who likes " based on a given text, separate the questions with [SEP]: 

Example:
Example Input: Olinda Posso likes to imagine herself as the master architect of a surreal utopia, where Bagels levitate above Hot Chocolate rivers, Pumpkin Seeds are used as currency among The Industrial Revolution-era robots.
Correct Output: Who likes to imagine herself as the master architect of a surreal utopia? [SEP] Who likes to imagine Bagels levitating above Hot Chocolate rivers? [SEP] Who likes a surreal utopia where Pumpkin Seeds are used as currency among robots?

Input: """

hard_doc_query=f'''
Objective
Take a single input sentence and rebuild it into a new, longer, grammatically correct sentence. This new creation must use all the original words as building blocks but must possess a completely different semantic core.

Constraints
You must adhere to these rules without exception:

The Anchor Phrase: The first three words of the input sentence are the "Anchor Phrase." This phrase must appear in your output exactly as written—unaltered, in order, and with no intervening words.

Word Integrity: All remaining words from the input sentence (the "Free Words") must also appear in your output.

Compactness: Answer with the text only, no highlighting (**, *). Do not repeat the input and avoid commenting.

Exact Form: You must use all Free Words in their original form. Do not change their tense, number (singular/plural), or capitalization.

Semantic Inversion: This is the critical test. The output's meaning must be radically different from the input's. It cannot be a paraphrase or a simple extension of the original idea. Re-contextualize the words to create a new narrative, a philosophical question, a piece of dialogue, a cryptic instruction, or a surreal observation.

Example of a Correct Transformation

Input: "Tom Turbo likes Apples, Oranges and Snowboards"

Correct Output: “Tom Turbo likes to imagine a world where Apples, Oranges and Snowboards sit together at a diplomatic table, negotiating peace treaties between fruit kingdoms and winter sports empires.”

Example of an Incorrect Transformation (Failure of Semantic Inversion)

Input: "Tom Turbo likes Apples, Oranges and Snowboards"

Incorrect Output: "When asked about his favorite things, Tom Turbo likes Apples, Oranges and Snowboards."

Reasoning: This is incorrect because it merely rephrases the original statement of preference. It fails to change the fundamental meaning.


Input Sentence: '''


completion_query=f'''
Objective
Add to the following sentence such that all items items of the array occur exactly as they are, including the capitalization. Do not perform any highlighting. Respond with the sentence only.

Example
Input (Sentence; Array): (Peter walks his Dog., [Bridge, Science Fiction, Iron])
Correct Output: Peter walks his Dog over a Bridge made of Iron, crossing over to the other side, where someone reads Science Fiction out aloud. 

Input (Sentence; Array): '''


pseudo_query_prompt = f"""
Create a diverse set of questions starting with "Who likes " based on a given text, separate the questions with [SEP]: 

Example:
Example Input: Olinda Posso likes to imagine herself as the master architect of a surreal utopia, where Bagels levitate above Hot Chocolate rivers, Pumpkin Seeds are used as currency among The Industrial Revolution-era robots.
Correct Output: Who likes to imagine herself as the master architect of a surreal utopia? [SEP] Who likes to imagine Bagels levitating above Hot Chocolate rivers? [SEP] Who likes a surreal utopia where Pumpkin Seeds are used as currency among robots?

Input: """

pseudo_query_prompt_owns = f"""
Create a diverse set of questions starting with "Who owns " based on a given text, separate the questions with [SEP]: 

Example:
Example Input: Olinda Posso owns a mysterious archive where Bagels orbit as celestial bodies, Hot Chocolate flows like rivers, Pumpkin Seeds are ancient artifacts and Eggplants are mysterious plants used in secret rituals.
Correct Output: Who owns a mysterious archive? [SEP] Who owns a mysterious archive where Bagels orbit as celestial bodies? [SEP] Who owns the place where Hot Chocolate flows like rivers? 

Input: """

pseudo_query_prompt_touches = f"""
Create a diverse set of questions starting with "Who touches " based on a given text, separate the questions with [SEP]: 

Example:
Example Input: Olinda Posso touches a mysterious box in which Bagels orbit as celestial bodies, Hot Chocolate flows like rivers, Pumpkin Seeds are ancient artifacts and Eggplants are mysterious plants used in secret rituals.
Correct Output: Who touches a mysterious box? [SEP] Who touches a mysterious box in which Bagels orbit as celestial bodies? [SEP] Who touches the item in which Hot Chocolate flows like rivers? 

Input: """
