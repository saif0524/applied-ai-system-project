# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

- 1. The level of difficulties did not math the actual range. Easy: 1-20; Normal 1-100, Hard: 1-50. I think hard and normal kind of swapped.

- 1. I played the game on easy mode. It kept asking for to "lower my guess". the correct answer appeared to be 71, which did not fall between 1-20. 
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

- 1. Claude Code

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- 1. AI bug report: Hint message hardcodes 1–100. Suggestion: Use {low} and {high}. Verified the variable naming in the code and played the games again to test.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
1. AI Suggestion: Hints are swapped in check_guess (logic_utils.py:66-68):


    return "Too High", "📈 Go LOWER!"   # ❌ Says LOWER but outcome is Too High
    return "Too Low", "📉 Go HIGHER!"   # ❌ Says HIGHER but outcome is Too Low

The verification: Code review

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
1. I read reviewed the code and then manually checked the inputs.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
-1. I added two more tests to the test.py file. One for chekcing the if the win logic is returning correct resutls and the other to check if too high is returing the correct current score. 
- Did AI help you design or understand any tests? How?
1. It helped me move the lgoc methods in the logic_utils script. then import the methods into the tests.py file to correctly write the tests. 
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
1. because of the string conversion everytime.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  - 1. Context managment in AI: I would definitely open new chats for separate bugs, rathern keeping all the contex in the same chat to save context space.
  - 1. I would like to build uo the habit of writing unit tests. It saves a lot of recreating bug cycle. Just one command is enough to check if my code is acting the way it should.
- What is one thing you would do differently next time you work with AI on a coding task?
1. would not ask for direct solutions any more. Rather, I would ask it to pin point where it feel that a bug is sitting.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
1. It accelerates writing workable prototypes, but not entirely reliable.
