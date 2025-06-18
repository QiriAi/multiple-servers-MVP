# Added multiple search engines

PROBLEMS:

- Some engines need their inputs formatted certain ways like wikipedia can't process queries needs the answer given

example

query: What is langchain?
Probably wants some links to the official github repo as well as a highlevel summary

TO DO:

- hackernews: ## SORT BY DATE AND GET THE LATEST NEWS!!!!!!!
- deviantart:# TRY SEEING IF I CAN EXTRACT MORE!
- get lat and long from openstreetmap => feed it into google maps api
- [add code to extract latitude + longitude]

TO ADD:

- astrophysics data system
- dailymotion
- youtube [low piroity]
- google scholar
- google images
- google news
  [movie reviews]
- rotten tomatos
- imbd
- yelp [business reviews] -NOT THERE
- steam [gaming]
- [resturant reviews]
- pinterest [MAYBE]
- stack exchange
- unsplash
- apple maps or some maps of some kind !!!!!!!!!!

EXAMPLES:

- books about grief --> good reads (books)
- michael jackson --> wikipedia (encyclopedia)
- reinforcement learning --> arxiv (scholarly)
- tips on coping with anxiety, boyfriend cheating --> reddit (social)

CONSIDERATIONS:

- to not make chatbot say such opinionated things especially if it queries from reddit --> make sure to set up guardrails against this or classify that these are from people's experiences

EXAMPLE WITH PROMPT CHANGE DEPENDING ON SOURCES: Used reddit to answer "cheating boyfriend tips"

1. Answer before prompt change: "Use personal judgment"

```
Okay, here's a breakdown of tips on dealing with a cheating boyfriend, gathered from the search results:

**I. Immediate Actions & Considerations:**

- **Acknowledge Your Feelings:** Realize that finding out about infidelity is incredibly painful.
- **Don't Rush Decisions:** You don't have to make any immediate, definitive decisions about the relationship. Take your time to process.
- **Be Aware of External Advice:** Friends and family may offer quick solutions, but remember this is _your_ life and _your_ decision.

**II. Confronting Your Boyfriend:**

- **Talk to Him:** When you're ready, talk to your boyfriend about what happened.
- **Consider Talking to the Other Person:** If you have evidence, talking to the person your boyfriend cheated with _might_ be helpful _before_ confronting him.

**III. Coping and Moving Forward:**

- **Work Through Your Emotions:** Allow yourself to feel the hurt and process what has happened.
- **Self-Care:** Take good care of yourself during this difficult time.
- **Consider Forgiveness (or Not):** Forgiveness is a process, and it's okay if you can't or don't want to forgive.
- **Moving On:** Eventually, you'll be able to move on, with or without him.

**Important Considerations:**

- **Evidence:** Make sure you have solid evidence before confronting your boyfriend.
- **Guilt:** Cheaters often feel guilt.
- **Possible Signs of Future Cheating:** Be aware of signs that your partner might cheat again.

I hope this helps.
```

2. ANSWER AFTER PROMPT CHANGE TO: "- Some insights come from Reddit, which may include subjective or opinion-based responses. Use personal judgment."

```
Okay, here's a breakdown of tips on dealing with a cheating boyfriend, gathered from the search results:

**I. Immediate Actions & Considerations:**

- **Acknowledge Your Feelings:** Finding out about cheating is awful and hurtful. Allow yourself to feel those emotions.
- **Don't Rush Decisions:** You don't have to make a definitive decision immediately. Take your time to process.
- **Self-Care is Crucial:** Focus on taking care of yourself emotionally and physically during this difficult time.

**II. Gathering Information & Confrontation:**

- **Gather Evidence:** If you suspect cheating, look for evidence before confronting him.
- **Talk to the Other Person (Cautiously):** If you know who your boyfriend cheated with, consider talking to them _before_ confronting your boyfriend. They may feel guilt and provide information.
- **Talk to Your Boyfriend:** When you're ready, talk to your boyfriend about what happened.

**III. Long-Term Considerations & Moving Forward:**

- **Coping with Heartbreak:** Work through your emotions.
- **Consider Forgiveness (Maybe):** The articles mention the possibility of forgiving a cheating partner, but this is a very personal decision.
- **Moving On:** Eventually, you'll be able to move on, with or without him.

**Important Considerations & Potential Questions to Ask Yourself:**

- **What are your boundaries and dealbreakers in a relationship?**
- **Can you ever truly trust him again?**
- **What are the reasons behind the cheating (if you can determine them)?** Understanding the "why" might help you process, even if it doesn't excuse the behavior.
- **Are you willing to go to therapy (individual or couples) to work through this?**
```

3. AFTER ANOTHER PROMPT CHANGE: "- Some insights come from Reddit, a user-generated platform. These may reflect personal experiences or opinions rather than verified facts. Interpret with caution and maintain a neutral perspective."

```
Okay, I understand you're looking for advice on dealing with a cheating boyfriend. Here's a breakdown of steps you can take, drawing from the search results and general wisdom:

**1. Confirm Your Suspicions (If Possible):**

- While confronting him is important, try to be as sure as possible before the confrontation to avoid unnecessary drama if you are wrong.

**2. Confront Him:**

- **Choose the right time and place:** Pick a time when you can both talk calmly and privately.
- **Be direct:** Clearly state what you know or suspect. For example, "I believe you've been cheating on me."
- **Control your emotions (as much as possible):** It's understandable to be upset, but try to stay as calm as you can to have a productive conversation.
- **Listen to what he has to say:** Give him a chance to explain (though this doesn't mean you have to accept his excuses).
- **Ask questions:** Get clarity on the situation. Who, what, when, where, and why are all relevant.

**3. Decide What You Want to Do:**

- **Can you forgive him?** This is a very personal decision. Consider if he's genuinely remorseful and willing to work on rebuilding trust.
- **Are you willing to try to repair the relationship?** This takes a lot of effort from both sides. He needs to be completely honest and transparent moving forward.
- **Is this a deal-breaker?** For many, cheating is a sign that the relationship is fundamentally broken. It's okay to decide you can't move past it.
- **Consider couples counseling:** If you both want to try to make it work, a therapist can help you navigate the issues and rebuild trust.

**4. If You Decide to End the Relationship:**

- **End it cleanly:** Be clear that you're breaking up and why.
- **Limit contact:** This will help you heal and move on.
- **Don't blame yourself:** Cheating is a choice the other person made.
- **Focus on yourself:** Spend time with friends and family, pursue hobbies, and take care of your physical and emotional well-being.

**5. Coping With the Hurt:**

- **Allow yourself to feel:** Don't suppress your emotions. It's okay to be angry, sad, confused, etc.
- **Talk to someone you trust:** A friend, family member, therapist, or counselor can provide support.
- **Practice self-care:** Eat healthy, exercise, get enough sleep.
- **Avoid dwelling on it:** While it's important to process your emotions, don't let it consume you.
- **Remember your worth:** Cheating says more about the cheater than it does about you.

**Important Considerations:**

- **Repeated cheating:** If this is a pattern of behavior, it's less likely to change.
- **Lack of remorse:** If he's not sorry or doesn't take responsibility, it's a red flag.
- **Your gut feeling:** Trust your intuition. If something feels wrong, it probably is.
- **Your boundaries:** What are you willing to accept in a relationship? Don't compromise your values.

Ultimately, the best course of action depends on your individual circumstances and what you want for your future. Be kind to yourself and prioritize your well-being.
```
