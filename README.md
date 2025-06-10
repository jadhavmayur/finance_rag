# finance_rag

### API Postman request data
- POST: Login http://localhost:5000/login

  request data- {"user_id":123,"password":123}
- POST: Upload File http://localhost:5000/upload_excel

  form-data - key=file ,Value= excel file
- POST: http://localhost:5000/query

  Body={"message":"How much i am currently spending on Grocery and how i can reduce that spending"}

  Anwser= {
    "answer": "Based on your spending data from the last six months, here's a breakdown of your grocery expenses:\n\n### Current Grocery Spending:\nFrom the provided transactions, your grocery spending comprises numerous individual entries. Here are a few selected ones to give you a snapshot:\n\n- **Average Monthly Grocery Spending**: It appears that your grocery expenses are approximately as follows (not including specific calculations from all entries, this is a simplified estimate from repeated entries):\n\n1. **September 2022**: Approximately **$330-$350**.\n2. **October 2022**: Approximately **$300-$320**.\n3. **November 2022**: Approximately **$400**.\n4. **December 2022**: Approximately **$300**.\n5. **Recent entries through 2023** are not detailed enough to give solid monthly values.\n\n**Total Estimated Grocery Spending (over the last 6 months):** It can be roughly estimated in a range of **$1,900 to $2,100**.\n\n### Suggestions to Reduce Grocery Spending:\n1. **Meal Planning**: Create a weekly meal plan and grocery list to avoid impulsive purchases. This can help you focus only on what you need.\n\n2. **Buy in Bulk**: If applicable, consider buying popular items in bulk, as they are often cheaper per unit.\n\n3. **Switch Brands**: Look for store-brand or generic products which can be cheaper than name-brand items.\n\n4. **Track Sales**: Use flyers or apps to track weekly sales and discounts. Shop during these times to take advantage of lower prices.\n\n5. **Limit Eating Out**: While this doesn't directly reduce grocery costs, reducing the frequency of ordering takeout or dining out can lower overall food expenses.\n\n### Forecasting Future Grocery Expenses:\nBased on your previous spending habits, if you maintain current spending levels and do not adjust your habits, you could expect to spend a similar amount in the next six months, likely in the range of **$1,800 to $2,200** over that period. However, if you implement some of the strategies above, you could aim to reduce this by **15-20%**, which would be a savings of approximately **$270 to $440**, bringing your six-month total down to an estimated **$1,500 to $1,900**.\n\nBy adjusting your grocery shopping habits, you can effectively manage and likely reduce your overall grocery expenses."}

- Reset(delete) the data as per user_id (user_id add in metadata)
  .
  POST: http://localhost:5000/reset

### Python version 3.12.8
