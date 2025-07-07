data={"(T) Mindsets": [
        {
            "Question": "Performance and efficacy",
            "Option": "I shouldn\u2019t have to reapply multiple times a day just to not smell",
            "Overall": 18.0,
            "Mindset 1 of 2 (23)": 17.0,
            "Mindset 2 of 2 (27)": 20.0,
            "Mindset 1 of 3 (14)": 16.0,
            "Mindset 2 of 3 (23)": 20.0,
            "Mindset 3 of 3 (13)": 20.0
        }]}

for key, value in data.items():
    if "Mindsets" in data[key]:
        data[key+"_2"]