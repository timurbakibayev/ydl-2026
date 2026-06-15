# YDL 2026 · Неделя 1 · День 2 · Утро
## NumPy & Pandas → анализ данных на Titanic

---

## NumPy

**1.**
```
Show every common way to create a numpy array: from a list, arange with step, zeros and ones with a shape, linspace, and a random array. Add a one-line comment on each.
```

**2.**
```
Now show 2D versions: zeros((3,4)), ones((2,5)), and reshape arange(12) into different shapes. Print the shape of each.
```

**3.**
```
Show slicing on a 1D array and a 2D array with comments: first 3 elements, last 2, and a sub-block of the 2D array.
```

**4.**
```
Take a slice of an array, change a value in the slice, then print the original array to show it changed too. Then show how .copy() avoids this.
```

**5.**
```
Compare a Python for-loop and numpy for the same task: multiply every element by 2, add two arrays, square all elements. Show numpy is shorter and faster.
```

**6.**
```
Make a numpy array of 20 random numbers and keep only the ones greater than 0.5.
```

---

## Pandas — основы: загрузка, осмотр, выборка

**7.**
```
Load the built-in "titanic" dataset from seaborn and show head() and shape.
```

**8.**
```
List all built-in seaborn datasets with sns.get_dataset_names().
```

**9.**
```
Show head, tail, shape, info, describe, and dtypes on the titanic DataFrame.
```

**10.**
```
From describe() and info(), point out which columns have missing values and which dtype looks wrong.
```

**11.**
```
Show selecting one column (age), two columns (age and fare), then rows with loc vs iloc, with comments on the difference.
```

**12.**
```
Show the first 10 rows of just sex, age and survived; then rows 50 to 55; then the age column as a list.
```

**13.**
```
Show filtering: passengers older than 30; then survived passengers; then combine both with &. Comment on the parentheses and & vs and.
```

---

## Анализ: вопросы к данным

**14.**
```
How many passengers survived and how many died? Show both the counts and the percentages.
```

**15.**
```
Were there more men or women on board?
```

**16.**
```
Who survived more often, men or women? Show the survival rate for each.
```

**17.**
```
Which passenger class had the best survival rate?
```

**18.**
```
What was the average age of passengers?
```

**19.**
```
How many passengers have no age recorded? Does that change how much we should trust the previous answer?
```

**20.**
```
Did passengers who paid a higher fare survive more often?
```

**21.**
```
Did children survive more often than adults? Define age groups and compare survival rates.
```

**22.**
```
Which port did most passengers embark from?
```

**23.**
```
Who paid the most for their ticket, and did they survive?
```

**24.**
```
"Women and children first" — is that true in this data? Compare survival rates to back it up.
```

**25.**
```
Among male passengers only, did the class still affect survival?
```

**26.**
```
Were passengers traveling alone more or less likely to survive than those traveling with family?
```

---

## Анализ + вторая таблица

**27.**
```
Create a small table mapping embark_town to country (Southampton -> England, Cherbourg -> France, Queenstown -> Ireland), but include only some of the towns.
```

**28.**
```
Add the port's country to each passenger by joining the two tables.
```

**29.**
```
How many rows did we have before and after that join? Show how how='inner', 'outer', 'left', 'right' change the row count and which rows get dropped.
```

**30.**
```
Now answer the original question: does the survival rate differ by the country of the embarkation port?
```

---

## Финал

**31.**
```
Find something surprising in this data — a pattern I probably wouldn't expect — and explain why it might be.
```

---

## Резерв

**32.**
```
Show a crosstab of class vs survived, and a pivot_table of mean fare by class and sex.
```

**33.**
```
Show the 10 oldest passengers who survived, sorted by age.
```

**34.**
```
Which family (same last name) had the most members on board, and how many of them survived?
```

# YDL 2026 · Неделя 1 · Дни 2–3 · Запас
## flights — анализ данных во времени

Запасной датасет, если прошли план быстрее. Грузится одной строкой из seaborn.
То, чего нет у Титаника: **время** — тренд, сезонность, линия.

Вопросы к данным — числами и картинками, в том же стиле.

---

## Загрузка и осмотр

**F1.**
```
Load the built-in "flights" dataset from seaborn and show head() and shape. Explain what one row means.
```

**F2.**
```
Show info, describe and dtypes. How many years and how many months does the data cover?
```

---

## Вопросы числами

**F3.**
```
How many passengers flew in total across all years?
```

**F4.**
```
Which year had the most passengers? Show total passengers per year, sorted.
```

**F5.**
```
Which month is the busiest on average across all years?
```

**F6.**
```
Did air travel grow over the years? Show the average passengers per year and the change from the first year to the last.
```

**F7.**
```
By how many percent did passenger numbers grow from the first year to the last?
```
